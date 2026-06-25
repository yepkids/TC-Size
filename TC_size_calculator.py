#!/usr/bin/env python3
"""End-to-end TC size workflow.

This script combines the old `write_nodefile.py`, `TE_NodeFileEditor.sh`, and
`TC_size_calculator.py` steps into one Python entry point:

1. Read SyCLoPS classified track parquet files.
2. Write TempestExtremes StitchNodes nodefiles.
3. Run TempestExtremes NodeFileEditor through subprocess jobs.
4. Compute quadrant wind radii and an area-equivalent mean TC size.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import numpy as np
import pandas as pd

# ------------------Change this section if needed to adjust the default paths and parameters for your case--------------------------------------
print("Please make sure to create input data lists that contains u10 (uas) and v10 (vas) variables of each model for TempestExtremes computation.\n \
      The list files in txt should locate in the DEFAULT_FILE_LIST_DIR. Please also change list files' filenames in the MODEL_SPECS section if needed.")
ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = ROOT / "output_size"
DEFAULT_FILE_LIST_DIR = ROOT / "file_list"
DEFAULT_TEMPESTEXTREMESDIR = Path(os.environ.get("TEMPESTEXTREMESDIR", "~/tempestextremes/bin")).expanduser()
IBTRACS_DIR = ROOT / "IB_track_file"
IBTRACS_FILENAME = ROOT / "IB_track_file" / "ibtracs_radii_test.csv"

CUTOFF_THRESHOLD = 30 # in knots. 30 is the default for most climate models. For km-scale models, 34 is recommended.
START_YEAR = 1988
END_YEAR = 2014

START_RE = re.compile(r"^start\b")
RADMX = 13


@dataclass(frozen=True)
class ModelSpec:
    key: str
    parquet_path: Path
    uv10_list_path: Path
    te_u_name: str
    te_v_name: str
    model_res: float

# Change the MODEL_SPECS section accordingly.
MODEL_SPECS = [
    # ModelSpec("era5", ROOT / "classified_track" / "SyCLoPS_track" / "SyCLoPS_classified_ERA5.parquet", DEFAULT_FILE_LIST_DIR / "era5_uv10in.txt", "VAR_10U", "VAR_10V", 0.25),
    # ModelSpec("era5deg1", ROOT / "classified_track" / "SyCLoPS_track" / "SyCLoPS_classified_ERA5deg1.parquet", DEFAULT_FILE_LIST_DIR / "era5deg1_uv10in.txt", "VAR_10U", "VAR_10V", 1.0),
    # ModelSpec("cnrm", ROOT / "classified_track" / "SyCLoPS_track" / "SyCLoPS_classified_CNRM-HR.parquet", DEFAULT_FILE_LIST_DIR / "cnrm_uv10in.txt", "uas", "vas", 0.25),
    # ModelSpec("cnrm-coup", ROOT / "classified_track" / "SyCLoPS_track" / "SyCLoPS_classified_CNRM-HR-COUP.parquet", DEFAULT_FILE_LIST_DIR / "cnrm-coup_uv10in.txt", "uas", "vas", 0.25),
    # ModelSpec("ecearth3p", ROOT / "classified_track" / "SyCLoPS_track" / "SyCLoPS_classified_EC-Earth3P-HR.parquet", DEFAULT_FILE_LIST_DIR / "ecearth3p_uv10in.txt", "uas", "vas", 0.25),
    # ModelSpec("echrm1", ROOT / "classified_track" / "SyCLoPS_track" / "SyCLoPS_classified_ECMWF-HR-mem1.parquet", DEFAULT_FILE_LIST_DIR / "echrm1_uv10in.txt", "uas", "vas", 0.25),
    # ModelSpec("eclrm1", ROOT / "classified_track" / "SyCLoPS_track" / "SyCLoPS_classified_ECMWF-LR-mem1.parquet", DEFAULT_FILE_LIST_DIR / "eclrm1_uv10in.txt", "uas", "vas", 1.0),
    # ModelSpec("echrm1-coup", ROOT / "classified_track" / "SyCLoPS_track" / "SyCLoPS_classified_ECMWF-HR-mem1-COUP.parquet", DEFAULT_FILE_LIST_DIR / "echrm1-coup_uv10in.txt", "uas", "vas", 0.25),
    # ModelSpec("hadgm", ROOT / "classified_track" / "SyCLoPS_track" / "SyCLoPS_classified_HadGEM-HR.parquet", DEFAULT_FILE_LIST_DIR / "hadgm_uv10in.txt", "uas", "vas", 0.25),
    # ModelSpec("hadgm-coup", ROOT / "classified_track" / "SyCLoPS_track" / "SyCLoPS_classified_HadGEM-HR-COUP.parquet", DEFAULT_FILE_LIST_DIR / "hadgm-coup_uv10in.txt", "uas", "vas", 0.25),
    # ModelSpec("ipslhr", ROOT / "classified_track" / "SyCLoPS_track" / "SyCLoPS_classified_IPSL-HR.parquet", DEFAULT_FILE_LIST_DIR / "ipslhr_uv10in.txt", "uas", "vas", 0.25),
    # ModelSpec("ipslvhr", ROOT / "classified_track" / "SyCLoPS_track" / "SyCLoPS_classified_IPSL-VHR.parquet", DEFAULT_FILE_LIST_DIR / "ipslvhr_uv10in.txt", "uas", "vas", 0.25),
    # ModelSpec("mrih", ROOT / "classified_track" / "SyCLoPS_track" / "SyCLoPS_classified_MRI-H.parquet", DEFAULT_FILE_LIST_DIR / "mrih_uv10in.txt", "uas", "vas", 0.25),
    # ModelSpec("mris", ROOT / "classified_track" / "SyCLoPS_track" / "SyCLoPS_classified_MRI-S.parquet", DEFAULT_FILE_LIST_DIR / "mris_uv10in.txt", "uas", "vas", 0.25),
]

##############################################################

def round5(value: float) -> float:
    return round(value / 5.0) * 5.0


def ensure_directories(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    DEFAULT_FILE_LIST_DIR.mkdir(parents=True, exist_ok=True)


def load_tracks(spec: ModelSpec) -> pd.DataFrame:
    if not spec.parquet_path.exists():
        raise FileNotFoundError(f"Missing classified track file for {spec.key}: {spec.parquet_path}")
    return pd.read_parquet(spec.parquet_path)


def filter_tc_tracks(df: pd.DataFrame) -> pd.DataFrame:
    adjusted = df["Adjusted_Label"].astype(str).str.contains("TC", na=False)
    track_info = df["Track_Info"].astype(str).str.contains("TC", na=False)
    cond = adjusted & track_info
    if "ISOTIME" in df.columns:
        isotime = pd.to_datetime(df["ISOTIME"], errors="coerce")
        cond &= isotime.dt.year.between(START_YEAR, END_YEAR, inclusive="both")
    return df.loc[cond].reset_index(drop=True).copy()


def filter_tc_tracks_ib() -> pd.DataFrame:
    df = pd.read_csv(IBTRACS_FILENAME, keep_default_na=False)
    df.rename(columns={'SID':'TID','ISO_TIME':'ISOTIME','USA_PRES':'MSLP'}, inplace=True)
    df['ISOTIME'] = pd.to_datetime(df['ISOTIME'])
    df = df[df.WS>=34] # Filter for tropical storm intensity and above (TC definition)
    df = df[df['ISOTIME'].dt.year.between(START_YEAR, END_YEAR, inclusive="both")]
    return df.reset_index(drop=True).copy()


def time_components(series: pd.Series) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    dt = pd.to_datetime(series, errors="coerce")
    if dt.notna().all():
        return dt.dt.year.to_numpy(), dt.dt.month.to_numpy(), dt.dt.day.to_numpy(), dt.dt.hour.to_numpy()
    values = series.astype(str).to_numpy()
    year = np.array([int(text[0:4]) for text in values], dtype=int)
    month = np.array([int(text[5:7]) for text in values], dtype=int)
    day = np.array([int(text[8:10]) for text in values], dtype=int)
    hour = np.array([int(text[11:13]) for text in values], dtype=int)
    return year, month, day, hour


def write_nodefile(spec: ModelSpec, df: pd.DataFrame, output_dir: Path) -> Path:
    nodefile_path = output_dir / f"{spec.key}_tc_nodefile.txt"
    if df.empty:
        nodefile_path.write_text("")
        return nodefile_path

    times = df["ISOTIME"] if "ISOTIME" in df.columns else pd.to_datetime(
        dict(year=df["year"], month=df["month"], day=df["day"], hour=df["hour"]),
        errors="coerce",
    )
    year, month, day, hour = time_components(times)

    grouped = df.groupby("TID", sort=False)
    with nodefile_path.open("w") as handle:
        for _, group in grouped:
            first_time = times.loc[group.index].iloc[0]
            if pd.isna(first_time):
                raise ValueError(f"Unable to parse ISOTIME for model {spec.key}")
            handle.write(
                f"start\t{len(group)}\t{int(year[group.index[0]])}\t{int(month[group.index[0]])}\t{int(day[group.index[0]])}\t{int(hour[group.index[0]])}\n"
            )
            for idx, row in group.iterrows():
                handle.write(
                    f"\t{row['i']}\t{row['j']}\t{row['LON']}\t{row['LAT']}\t{row['MSLP']}\t{int(year[idx])}\t{int(month[idx])}\t{int(day[idx])}\t{int(hour[idx])}\n"
                )
    return nodefile_path


def build_nodefiles(output_dir: Path) -> dict[str, pd.DataFrame]:
    tc_tracks: dict[str, pd.DataFrame] = {}
    for spec in MODEL_SPECS:
        if not spec.parquet_path.exists():
            print(f"Skipping nodefile generation for {spec.key}: missing {spec.parquet_path}")
            continue
        df = filter_tc_tracks(load_tracks(spec))
        tc_tracks[spec.key] = df
        write_nodefile(spec, df, output_dir)
        print(f"Wrote nodefile for {spec.key}: {output_dir / f'{spec.key}_tc_nodefile.txt'}")
    return tc_tracks


def area_equivalent_radius(radii_nm: Iterable[float], conv_rate: float) -> float:
    values = np.asarray(list(radii_nm), dtype=float) * conv_rate
    if not np.isfinite(values).any() or np.all(values <= 0):
        return 0.0
    angles = np.deg2rad(np.array([45.0, 135.0, 225.0, 315.0, 405.0]))
    extended = np.concatenate([values, values[:1]])
    sample_angles = np.linspace(0.0, 2.0 * np.pi, 360, endpoint=False)
    sample_radii = np.interp(sample_angles, angles, extended)
    area = np.trapezoid(0.5 * sample_radii**2, sample_angles)
    return float(np.sqrt(area / np.pi))


def calculate_wind_radii(df: pd.DataFrame, conv_rate: float, ib_mode: bool) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    out = df.copy()
    if not ib_mode:
        r30_values = out["r30"].apply(lambda x: eval(x.strip('"'), {"__builtins__": None}, {"nan": np.nan}))
    else:
        r30_values = out[["NE34", "SE34", "SW34", "NW34"]].apply(lambda row: row.to_numpy(), axis=1)
    out[["NE34", "SE34", "SW34", "NW34"]] = pd.DataFrame(r30_values.tolist(), index=out.index)
    out["MeanRad"] = out[["NE34", "SE34", "SW34", "NW34"]].apply(
        lambda row: area_equivalent_radius(row.to_numpy(), conv_rate), axis=1
    )
    return out


def read_nodefileeditor_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing NodeFileEditor output: {path}")
    return pd.read_csv(path,  sep=", ", na_values=' nan', engine='python')


def align_ws_from_source(output_df: pd.DataFrame, source_df: pd.DataFrame) -> pd.DataFrame:
    if output_df.empty:
        return output_df.copy()
    if len(output_df) != len(source_df):
        raise ValueError(
            f"Row count mismatch between NodeFileEditor output ({len(output_df)}) and source tracks ({len(source_df)})"
        )
    out = output_df.copy()
    if "WS" in source_df.columns:
        out["WS"] = source_df["WS"].to_numpy()
    else:
        raise ValueError("Source track dataframe is missing 'WS' (wind speed) column")
    return out


def build_nodefile_editor_command(tempestextremesdir: Path, spec: ModelSpec, output_dir: Path) -> list[str]:
    nodefile = output_dir / f"{spec.key}_tc_nodefile.txt"
    uv10_list = spec.uv10_list_path
    out_csv = output_dir / f"{spec.key}_windrad.csv"
    calculate = (
        f"RWP=radial_quadrant_profile(_VECMAG({spec.te_u_name},{spec.te_v_name}),53,0.2500001);"
        f"r30=firstwhere(RWP,fallsbelow,{CUTOFF_THRESHOLD*0.514},3.0)"
    )
    return [
        str(tempestextremesdir / "NodeFileEditor"),
        "--in_nodefile", str(nodefile),
        "--in_nodefile_type", "SN",
        "--in_data_list", str(uv10_list),
        "--out_nodefile", str(out_csv),
        "--in_fmt", "lon,lat,MSLP",
        "--out_fmt", "lon,lat,MSLP,r30",
        "--out_nodefile_format", "csv",
        "--calculate", calculate,
    ]


def run_subprocesses(commands: list[list[str]], max_workers: int) -> None:
    if not commands:
        return

    def run_one(command: list[str]) -> None:
        print("Running:", " ".join(command))
        subprocess.run(command, check=True)

    with cf.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_one, command) for command in commands]
        for future in cf.as_completed(futures):
            future.result()


def run_nodefile_editor(specs: list[ModelSpec], tempestextremesdir: Path, output_dir: Path, max_workers: int) -> None:
    commands: list[list[str]] = []
    for spec in specs:
        if not spec.uv10_list_path.exists():
            print(f"Skipping NodeFileEditor for {spec.key}: missing {spec.uv10_list_path}")
            continue
        commands.append(build_nodefile_editor_command(tempestextremesdir, spec, output_dir))
    run_subprocesses(commands, max_workers=max_workers)


def calculate_outputs(specs: list[ModelSpec], output_dir: Path, tc_tracks: dict[str, pd.DataFrame], conv_rate: float, ib_mode: bool) -> pd.DataFrame:
    cols = ['NE34', 'SE34', 'SW34', 'NW34', 'MeanRad']
    if ib_mode:
        calculated = calculate_wind_radii(tc_tracks, conv_rate, ib_mode)
        outname = IBTRACS_DIR / f"IBTrACS_TC_size.csv"
        calculated.to_csv(outname, index=False)
        print(f"Processed {outname}")
        return 
    for spec in specs:
        windrad_path = output_dir / f"{spec.key}_windrad.csv"
        if not windrad_path.exists():
            print(f"Skipping size calculation for {spec.key}: missing {windrad_path}")
            continue
        output_df = read_nodefileeditor_csv(windrad_path)
        source_df = tc_tracks.get(spec.key)
        if source_df is None:
            print(f"Skipping size calculation for {spec.key}: no source track dataframe loaded")
            continue
        aligned = align_ws_from_source(output_df, source_df)
        calculated = calculate_wind_radii(aligned, conv_rate, ib_mode)
        calculated.drop(columns=['RWP'], inplace=True)
        STEP_DEG = 0.25 if spec.model_res < 0.6 else 0.5
        calculated[cols] = calculated[cols].where(calculated[cols] <= 0, (calculated[cols] - STEP_DEG / 2) * 111 / 1.852).round(2)
        calculated['WS'] = calculated['WS']/0.5144
        outname = output_dir / f"{spec.key}_TC_size.csv"
        calculated.to_csv(outname, index=False)
        print(f"Processed {outname}")
    return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Combined TC size workflow.")
    parser.add_argument("--tempestextremesdir", type=Path, default=DEFAULT_TEMPESTEXTREMESDIR, help="Path to the TempestExtremes installation directory.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for nodefiles and wind-radius CSV outputs.")
    parser.add_argument("--max-workers", type=int, default=8, help="Maximum number of concurrent NodeFileEditor subprocesses. Default is 8.")
    parser.add_argument("--skip-nodefiles", action="store_true", help="Skip writing StitchNodes nodefiles.")
    parser.add_argument("--skip-te", action="store_true", help="Skip TempestExtremes NodeFileEditor execution.")
    parser.add_argument("--skip-size", action="store_true", help="Skip TC size calculation from NodeFileEditor outputs.")
    parser.add_argument("--ib-mode", action="store_true", help="Run in IBTrACS mode. Skip writing nodefiles and TempestExtremes execution and use the processed IBTrACS data.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_directories(args.output_dir)
    args.output_dir.parent.mkdir(parents=True, exist_ok=True)
    conv_rate = 1 if not args.ib_mode else 0.85
    if args.ib_mode:
        tc_tracks = pd.DataFrame()
        tc_tracks = filter_tc_tracks_ib()
        calculate_outputs(MODEL_SPECS, args.output_dir, tc_tracks, conv_rate, args.ib_mode)
        return 0

    if not args.tempestextremesdir.exists():
        raise FileNotFoundError(f"TempestExtremes directory does not exist: {args.tempestextremesdir}")
    
    tc_tracks: dict[str, pd.DataFrame] = {}
    if not args.skip_nodefiles:
        tc_tracks = build_nodefiles(args.output_dir)

    if not args.skip_te:
        run_nodefile_editor(MODEL_SPECS, args.tempestextremesdir, args.output_dir, args.max_workers)
        
    if not args.skip_size:
        if not tc_tracks:
            for spec in MODEL_SPECS:
                if spec.parquet_path.exists():
                    tc_tracks[spec.key] = filter_tc_tracks(load_tracks(spec))
        calculate_outputs(MODEL_SPECS, args.output_dir, tc_tracks, conv_rate, args.ib_mode)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
