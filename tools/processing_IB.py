# This program assigns basin labels to tropical cyclone records based on their latitude and longitude positions.
# Author: Yushan Han
# Date: Jan 2026

import pandas as pd
import numpy as np

Mode= 'Selected' # 'Selected' or 'ETC-included'
# Load IBTrACS data
IB_DATA='IB_track_file/ibtracs.since1980.list.v04r01.csv'
df=pd.read_csv(IB_DATA,keep_default_na=False)
df=df[1:]
df=df[['SID','SEASON','BASIN','SUBBASIN','NAME','ISO_TIME','NATURE','LAT','LON','WMO_WIND','WMO_PRES','WMO_AGENCY','TRACK_TYPE',\
    'USA_WIND','USA_PRES','USA_STATUS','USA_SSHS','TOKYO_GRADE','USA_R34_NE','USA_R34_SE','USA_R34_NW','USA_R34_SW','USA_RMW','DIST2LAND']]
df[['SEASON','USA_SSHS']]=df[['SEASON','USA_SSHS']].astype(int)
float_cols = ['LON','LAT','WMO_WIND','WMO_PRES','USA_PRES', 'USA_WIND', 'TOKYO_GRADE','USA_R34_NE','USA_R34_SE','USA_R34_NW','USA_R34_SW','USA_RMW','DIST2LAND']
df[float_cols] = df[float_cols].replace(' ', 0)
df[float_cols] = df[float_cols].astype(float)
df['ISO_TIME'] = pd.to_datetime(df['ISO_TIME'])
df=df[df.ISO_TIME.dt.year>=1988] # Change start year if needed
df=df[df['ISO_TIME'].dt.hour.isin([0,6,12,18])]
df=df[df['TRACK_TYPE']=='main']
df.LON=df.LON%360

# Load Extended Best Track (EBT) data
EBT_DATA='IB_track_file/ebt_1988_2021.csv'
df1=pd.read_csv(EBT_DATA)
df1['ISO_TIME'] = pd.to_datetime(df1['YEAR'].astype(str) + df1['DATE'].astype(str).str.zfill(6), format='%Y%m%d%H')
df1.loc[df1.LON==360,'LON']=0.0
df1.LON=-df1.LON%360

# Adjust wind speeds based on basin and data source
df['ADJ_WIND']=df.apply(lambda x: np.round(x['USA_WIND']*(1.06/1.11)) if x['WMO_WIND']==0 and x['BASIN'] == 'NI' else x['WMO_WIND'], axis=1)
df['ADJ_WIND']=df.apply(lambda x: np.round(x['USA_WIND']*(1.03/1.11)) if x['WMO_WIND']==0 and any(x['BASIN'] != np.array(['EP','NA','NI'])) else x['WMO_WIND'], axis=1)
df = df.rename(columns={'ADJ_WIND':'WS'})

if Mode=='Selected': # Only keep tropical LPS records
    df=df[~(df['NATURE'].isin(['SS','ET'])) & ~(df['USA_SSHS'].isin([-4,-2]))]

# Keep only storms that reached at least tropical storm strength (34 kt)
tcid=pd.unique(df.SID)[(df.groupby('SID')['WS'].max()>=34).values]
df=df[df.SID.isin(tcid)]

wind_radii_cols = ['USA_R34_NE','USA_R34_SE','USA_R34_NW','USA_R34_SW','USA_RMW']
df1=df1[df1["ISO_TIME"].dt.year<2004]

# Mapping from df1_lookup columns to df columns
df1_to_df_col = {
    'NE34': 'USA_R34_NE',
    'SE34': 'USA_R34_SE',
    'NW34': 'USA_R34_NW',
    'SW34': 'USA_R34_SW',
    'RMW' : 'USA_RMW'
}

# Create a mapping from (ISO_TIME, LON, LAT) to wind radii in df1
df1_lookup = df1.set_index(['ISO_TIME', 'LON', 'LAT'])[
    list(df1_to_df_col.keys())
]

# Function to update wind radii from EBT data if match exists
def update_wind_radii(row):
    key = (row['ISO_TIME'], row['LON'], row['LAT'])
    if key in df1_lookup.index:
        vals = df1_lookup.loc[key]
        for df1_col, df_col in df1_to_df_col.items():
            row[df_col] = vals[df1_col]
    return row

df = df.apply(update_wind_radii, axis=1)
# Rename columns from 'USA_R34_NE' to 'NE34', etc.
df = df.rename(columns={v: k for k, v in df1_to_df_col.items()})

# Interpolate missing wind radii for NA and WP basins

dftc=df.copy()
wind_radii_cols = ['NE34', 'SE34', 'NW34', 'SW34', 'RMW']

# Mask for rows that are candidates for interpolation (NA/WP basins and WS >= 34)
mask_basin = (dftc['BASIN']=='NA') | ((dftc['BASIN']=='WP') & (dftc.ISO_TIME.dt.year>=2002))
mask_ws = dftc['WS'] >= 34
mask_target = mask_basin & mask_ws
SID_list = dftc[mask_basin]['SID'].unique() 
# Replace 0 with NaN in target rows for the radii columns
dftc.loc[mask_target, wind_radii_cols] = dftc.loc[mask_target, wind_radii_cols].replace(0, np.nan)

# Create a temporary dataframe for the subset to interpolate
subset_df = dftc[mask_target].copy()

# Perform interpolation for each wind radii column within each SID
for col in wind_radii_cols:
    subset_df[col] = subset_df.groupby('SID')[col].transform(lambda x: x.interpolate(method='linear', limit_direction='both'))

# Update the original dataframe with the interpolated values
dftc.update(subset_df)
dftc[wind_radii_cols] = dftc[wind_radii_cols].fillna(0)
if Mode=='Selected':
    dftc.to_csv('IB_track_file/ibtracs_radii_all.csv')
else:
    dftc.to_csv('IB_track_file/ibtracs_radii_ETC_included.csv')