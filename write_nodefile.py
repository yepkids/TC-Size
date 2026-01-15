# This program generates node files for tropical cyclone tracks detected with SyCLoPS in various climate models.
# Inputs are the classified SyCLoPS track files in parquet format.
# Outputs are node files in StictNodes (SN) format that is readable by TempestExtremes NodeFileEditor.
import numpy as np
import pandas as pd
import xarray as xr
import re

# Define file paths (examples)
files = {
    'cnrm-hr': 'classified_track/SyCLoPS_track/SyCLoPS_classified_CNRM-HR.parquet',
    'cnrm-hr-coup': 'classified_track/SyCLoPS_track/SyCLoPS_classified_CNRM-HR-COUP.parquet',
    'ecearth3p-hr': 'classified_track/SyCLoPS_track/SyCLoPS_classified_EC-Earth3P-HR.parquet',
    'ecmwf-hr-mem1': 'classified_track/SyCLoPS_track/SyCLoPS_classified_ECMWF-HR-mem1.parquet',
    'ecmwf-lr-mem1': 'classified_track/SyCLoPS_track/SyCLoPS_classified_ECMWF-LR-mem1.parquet',
    'ecmwf-hr-mem1-coup': 'classified_track/SyCLoPS_track/SyCLoPS_classified_ECMWF-HR-mem1-COUP.parquet',
    'era5': 'classified_track/SyCLoPS_track/SyCLoPS_classified_ERA5.parquet',
    'era5deg1': 'classified_track/SyCLoPS_track/SyCLoPS_classified_ERA5deg1.parquet',
    'hadgem': 'classified_track/SyCLoPS_track/SyCLoPS_classified_HadGEM-HR.parquet',
    'hadgem-coup': 'classified_track/SyCLoPS_track/SyCLoPS_classified_HadGEM-HR-COUP.parquet',
    'cnrm': 'classified_track/SyCLoPS_track/SyCLoPS_classified_CNRM-HR.parquet',
    'cnrm-coup': 'classified_track/SyCLoPS_track/SyCLoPS_classified_CNRM-HR-COUP.parquet',
    'echrm1-coup': 'classified_track/SyCLoPS_track/SyCLoPS_classified_ECMWF-HR-mem1-COUP.parquet',
    'ecearth': 'classified_track/SyCLoPS_track/SyCLoPS_classified_EC-Earth3P-HR.parquet',
    'mrih': 'classified_track/SyCLoPS_track/SyCLoPS_classified_MRI-H.parquet',
    'ipslhr': 'classified_track/SyCLoPS_track/SyCLoPS_classified_IPSL-HR.parquet',
}

# Load all DataFrames
dfs = {name: pd.read_parquet(path) for name, path in files.items()}

# Filtering function
def filter_tc(df):
    cond = (df['Adjusted_Label'].str.contains('TC')) & (df['Track_Info'].str.contains('TC'))
    if 'ISOTIME' in df.columns:
        cond &= df.ISOTIME.dt.year.between(1988, 2014)
    return df[cond]

dfs_tc = {
    name + '_tc': filter_tc(df)
    for name, df in dfs.items()
}

def write_nodefile(key):
    dfcol= dfs_tc[key].copy()
    noden=dfcol.groupby('TID')['LON'].count()
    print(key)
    if 'hadgem' in key:
        year0=dfcol.groupby('TID')['ISOTIME'].first().str.slice(0,4).astype(int)
        month0=dfcol.groupby('TID')['ISOTIME'].first().str.slice(5,7).astype(int)
        day0=dfcol.groupby('TID')['ISOTIME'].first().str.slice(8,10).astype(int)
        hour0=dfcol.groupby('TID')['ISOTIME'].first().str.slice(11,13).astype(int)
        year = dfcol['ISOTIME'].str.slice(0,4).astype(int).values
        month = dfcol['ISOTIME'].str.slice(5,7).astype(int).values
        day = dfcol['ISOTIME'].str.slice(8,10).astype(int).values
        hour = dfcol['ISOTIME'].str.slice(11,13).astype(int).values
    else:
        year0=dfcol.groupby('TID')['ISOTIME'].first().dt.year
        month0=dfcol.groupby('TID')['ISOTIME'].first().dt.month
        day0=dfcol.groupby('TID')['ISOTIME'].first().dt.day
        hour0=dfcol.groupby('TID')['ISOTIME'].first().dt.hour
        year=dfcol.ISOTIME.dt.year.values
        month=dfcol.ISOTIME.dt.month.values
        day=dfcol.ISOTIME.dt.day.values
        hour=dfcol.ISOTIME.dt.hour.values
        
    start_line=[]
    for i in range(len(noden)):
        start_line.append('start\t'+str(noden.iloc[i])+'\t'+str(year0.iloc[i])+'\t'+str(month0.iloc[i])+'\t'+str(day0.iloc[i])\
        +'\t'+str(hour0.iloc[i]))
    dfcol['ind']=np.arange(0,len(dfcol),1)
    idfst=dfcol.groupby('TID')['ind'].first()

    nodex=dfcol.i.values
    nodey=dfcol.j.values
    lon1=dfcol.LON.values
    lat1=dfcol.LAT.values
    mslp=dfcol.MSLP.values

# Output to the final modified StictNodes-style text file.
    ct=-1
    with open(f'path_to_store/{key}_nodefile.txt', 'w') as f:
        for i in range(len(nodex)):
            if any(i==idfst):
                ct+=1
                f.write(start_line[ct])
                f.write('\n')
                f.write('\t'+str(nodex[i])+'\t'+str(nodey[i])+'\t'+str(lon1[i])+'\t'+str(lat1[i])+'\t'+str(mslp[i])+'\t'+str(year[i])+'\t'+str(month[i])+'\t'+str(day[i])+'\t'+str(hour[i]))
                f.write('\n')
            else:
                f.write('\t'+str(nodex[i])+'\t'+str(nodey[i])+'\t'+str(lon1[i])+'\t'+str(lat1[i])+'\t'+str(mslp[i])+'\t'+str(year[i])+'\t'+str(month[i])+'\t'+str(day[i])+'\t'+str(hour[i]))
                f.write('\n')
                
for key in dfs_tc.keys():
    write_nodefile(key)

