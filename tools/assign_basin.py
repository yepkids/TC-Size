# This program assigns basin labels to tropical cyclone records based on their latitude and longitude positions.
# Author: Yushan Han
# Date: Dec 2025

import numpy as np
import xarray as xr
import pandas as pd
# Load basin mask
basinmask1=xr.open_dataset('basin_mask_05deg.nc').mask
basinmask1=basinmask1.fillna(-1)

lats = basinmask1.lat.values
lons = basinmask1.lon.values
mask_grid = basinmask1.values

def assign_basin(name, df):
    dftrack = df.copy()
    dftrack.rename(columns={"track_id":"TID"}, inplace=True)
    df_lats = dftrack['LAT'].to_numpy(dtype=float)
    df_lons = np.mod(dftrack['LON'].to_numpy(dtype=float), 360.0)  # ensure 0-360 range
    mask_vals = np.full(dftrack.shape[0], np.nan)
    valid = ~np.isnan(df_lats) & ~np.isnan(df_lons)
    if valid.any():
        # compute nearest index for each valid latitude and longitude (vectorized)
        lat_idx = np.abs(lats[:, None] - df_lats[valid][None, :]).argmin(axis=0)
        lon_idx = np.abs(lons[:, None] - df_lons[valid][None, :]).argmin(axis=0)
        mask_vals[valid] = mask_grid[lat_idx, lon_idx]
    lon_col = 'LON'
    lat_col = 'LAT'
    dftrack['mask_val'] = mask_vals.astype(int)
    # Assign basin labels based on mask values and locations
    basin_label=np.array(["Others"]*len(dftrack),dtype=object)
    basin_label[(dftrack.mask_val==2) | ((dftrack.mask_val==-1) & (dftrack[lon_col]>130) & (dftrack[lon_col]<300) & (dftrack[lat_col]<0))] = "SP"
    basin_label[(((dftrack.mask_val==3) & (dftrack[lon_col]<=180)) | (dftrack.mask_val==4))| ((dftrack.mask_val==-1) & (dftrack[lon_col]>=100) & (dftrack[lon_col]<=180) & (dftrack[lat_col]>=0))] = "WP"
    basin_label[((dftrack.mask_val==5) & (dftrack.LAT>=0)) | ((dftrack.mask_val==-1) & (dftrack[lat_col]>=20) & (dftrack[lon_col]<100) & (dftrack[lat_col]>=0) & (dftrack[lat_col]<=40))] = "NI"
    basin_label[((dftrack.mask_val==5) & (dftrack.LAT<0))| ((dftrack.mask_val==-1) & (dftrack[lon_col]>=20) & (dftrack[lon_col]<=130) & (dftrack[lat_col]<0))] = "SI"
    basin_label[(dftrack.mask_val==8) | ((dftrack.mask_val==-1) & (((dftrack[lon_col]>=0) & (dftrack[lon_col]<=20)) | ((dftrack[lon_col]<=360) & (dftrack[lon_col]>=340))) & (dftrack[lat_col]>0) & (dftrack[lat_col]<=30)) |
                ((dftrack.mask_val==-1) & (dftrack[lon_col]>=260) & (dftrack[lon_col]<340) & (dftrack[lat_col]>=0))] = "NA"
    basin_label[((dftrack.mask_val==3) & (dftrack[lon_col]>180)) | ((dftrack.mask_val==-1) & (dftrack[lon_col]<252) & (dftrack[lon_col]>180) & (dftrack[lat_col]>=0))] = "EP"
    dftrack['BASIN'] = basin_label
    
    dftrack.to_csv(f'./final_track_file/{name}.csv',index=False)
        
files ={
    'mris': '../output_size/MRI-S_SIZE.csv',
    'mrih': '../output_size/MRI-H_SIZE.csv',
    'ipslvhr': '../output_size/IPSL-VHR_SIZE.csv',
    'ipslhr': '../output_size/IPSL-HR_SIZE.csv',
    'echrm1': '../output_size/ECMWF-HR-mem1_SIZE.csv',
    'eclrm1': '../output_size/ECMWF-LR-mem1_SIZE.csv',
    'era5deg1': '../output_size/ERA5deg1_SIZE.csv',
    'era5': '../output_size/ERA5_SIZE.csv',
    'hadgem': '../output_size/HadGEM-HR_SIZE.csv',
    'cnrm': '../output_size/CNRM-HR_SIZE.csv',
    'hadgem-coup': '../output_size/HadGEM-HR-COUP_SIZE.csv',
    'cnrm-coup': '../output_size/CNRM-HR-COUP_SIZE.csv',
    'echrm1-coup': '../output_size/ECMWF-HR-mem1-COUP_SIZE.csv',
    'ecearth3p': '../output_size/EC-Earth3P-HR_SIZE.csv'
}
# Load CSVs
dfsize = {}
for name, path in files.items():
    df = pd.read_csv(path,keep_default_na=False)
    dfsize[name] = df
# Assign basins and save
for name, df in dfsize.items():
    assign_basin(name+'_SyCLoPS', df)
    
# File paths for ZU tracks
ZU_files = {
    'hadgem': '../classified_track/zu_tctrack/hadgem_zu_tracks.csv',
    'cnrm': '../classified_track/zu_tctrack/cnrm_zu_tracks.csv',
    'hadgem-coup': '../classified_track/zu_tctrack/hadgem-coup_zu_tracks.csv',
    'mrih': '../classified_track/zu_tctrack/mrih_zu_tracks.csv',
    'mris': '../classified_track/zu_tctrack/mris_zu_tracks.csv',
    'ipslhr': '../classified_track/zu_tctrack/ipslhr_zu_tracks.csv',
    'ipslvhr': '../classified_track/zu_tctrack/ipslvhr_zu_tracks.csv',
    'echrm1': '../classified_track/zu_tctrack/echrm1_zu_tracks.csv',
    'eclrm1': '../classified_track/zu_tctrack/eclrm1_zu_tracks.csv',
    'cnrm-coup': '../classified_track/zu_tctrack/cnrm-coup_zu_tracks.csv',
    'ecearth3p': '../classified_track/zu_tctrack/ecearth3p_zu_tracks.csv',
    'echrm1-coup': '../classified_track/zu_tctrack/echrm1-coup_zu_tracks.csv',
    'era5': '../classified_track/zu_tctrack/era5_zu_tracks.csv',
    'era5deg1': '../classified_track/zu_tctrack/era5deg1_zu_tracks.csv'
}

# Load and clean CSVs
dfo_tc = {}
for name, path in ZU_files.items():
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={"lon": "LON", "lat": "LAT", "track_id": "TID"})
    if name =='era5':
        df=df[df.year.between(1988, 2014)]
    dfo_tc[name] = df

for name, df in dfo_tc.items():
    assign_basin(name+'_ZU', df)
