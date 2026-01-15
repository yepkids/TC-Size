# This program assigns track types to each tropical cyclone track in IBTrACS based on their precurosr and posterior states.
# Author: Yushan Han
# Date: Dec 2025

import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

hour_filter=np.array([0,6,12,18])
tcfile='../IB_tracks/ibtracs_rad_all_interp.csv'
exfile='/pscratch/sd/y/ykh5116/FIKE/IB_tracks/ibtracs_rad_all_ex.csv'
dfstc=pd.read_csv(tcfile,keep_default_na=False)
dfsex=pd.read_csv(exfile,keep_default_na=False)

dfsex['ISO_TIME']=pd.to_datetime(dfsex['ISO_TIME'])
dfext=dfsex[(dfsex['BASIN'].isin(['NA','WP'])) & (dfsex.ISO_TIME.dt.year>= 1988) & (dfsex.ISO_TIME.dt.year <= 2024)]
# Check if a TC underwent extratropical transition (ET) after reaching tropical status
def check_et_after_tropical(group):
	sshs = group['USA_SSHS'].values
	grade = group['TOKYO_GRADE'].values
	basin = group['BASIN'].values
 
	# Find indices where the TC had tropical status
	tropical_indices = np.where(((sshs >= 0) & (basin=='NA')) | ((np.isin(grade, [3,4,5])) & (basin=='WP')))[0]
	if len(tropical_indices) == 0:
		# No tropical status found
		return False	
	# Get the last index where it was tropical
	last_tropical_idx = tropical_indices[-1]
	# Check if there are ET indicators (-2 or -4) after the last tropical status
	if last_tropical_idx + 1 < len(sshs):
		post_tropical = sshs[last_tropical_idx + 1]
		if (np.any(np.isin(post_tropical, [-2, -4])) & (basin[0]=='NA')) or ((grade[last_tropical_idx + 1] == 6) & (basin[0]=='WP')):
			return True
	return False

def check_tropical_transition(group):
	sshs = group['USA_SSHS'].values
	grade = group['TOKYO_GRADE'].values
	ws = group['WS'].values
	basin = group['BASIN'].values
	# Find indices where the TC had tropical status
	tropical_indices = np.where(((sshs >= 0) & (basin=='NA')) | ((np.isin(grade, [3,4,5])) & (basin=='WP')))[0]
	if len(tropical_indices) == 0:
		# No tropical status found
		return False	
	# Get the first index where it was tropical
	first_tropical_idx = tropical_indices[0]
	# Check if there are ET indicators (-2 or -4) after the last tropical status
	if first_tropical_idx - 1 >= 0:
		pre_tropical_sshs = sshs[:first_tropical_idx]
		pre_tropical_grade = grade[:first_tropical_idx]
  
		if (np.any(np.isin(pre_tropical_sshs, [-2, -4])) & (basin[0]=='NA')) or (np.any(pre_tropical_grade == 6) & (basin[0]=='WP')):
			return True
	return False

def check_land_after_tropical(group):
	sshs = group['USA_SSHS'].values
	dist = group['DIST2LAND'].values
	basin = group['BASIN'].values
	grade = group['TOKYO_GRADE'].values
	lat = group['LAT'].values
	# Find indices where the TC had tropical status
	tropical_indices = np.where(((sshs >= 0) & (basin=='NA')) | ((np.isin(grade, [3,4,5])) & (basin=='WP')))[0]
	if len(tropical_indices) == 0:
		return False
	# Get the last index where it was tropical
	last_tropical_idx = tropical_indices[-1]
	if lat[last_tropical_idx] >=40:
		return False
	# Check if there are DIST2LAND == 0 after the last tropical status
	if dist[last_tropical_idx] == 0 or (last_tropical_idx + 1 < len(dist) and dist[last_tropical_idx + 1] == 0):
		return True
	return False 

ib_et_id = dfext['SID'].unique()[dfext.groupby('SID').apply(check_et_after_tropical)]
ib_tt_id = dfext['SID'].unique()[dfext.groupby('SID').apply(check_tropical_transition)]
ib_land_id = dfext['SID'].unique()[dfext.groupby('SID').apply(check_land_after_tropical)]

hour_filter=np.array([0,6,12,18])
dfs=dfstc.rename(columns={"SID": "TID","ISO_TIME":"ISOTIME"})
dfs['ISOTIME']=pd.to_datetime(dfs['ISOTIME'])
dfs=dfs[(((dfs['BASIN']=='NA') & (dfs.ISOTIME.dt.year>=1988))| ((dfs['BASIN']=='WP') & (dfs.ISOTIME.dt.year>=2002))) & (dfs.WS>=34) & (dfs.ISOTIME.dt.year<=2024)].reset_index(drop=True)
tcfreq = len(dfs[dfs.WS>=34])
print(tcfreq)
lon=np.array(dfs.LON)
lat=np.array(dfs.LAT)
x=np.cos(lon*(np.pi/180))*np.cos(lat*(np.pi/180))
y=np.sin(lon*(np.pi/180))*np.cos(lat*(np.pi/180))
z=np.sin(lat*(np.pi/180))
fst = np.unique(dfs.TID.values, return_index=1)[1]
lst=len(dfs)-np.unique(dfs.TID.values[::-1], return_index=1)[1]-1
id2=np.arange(0,len(dfs['LON']),1)
dfs['id1']=id2
sday=dfs.groupby(dfs['ISOTIME'])['id1'].apply(list)
fsttime=dfs.groupby(dfs['TID'])['ISOTIME'].first()

otrack='../classified_track/SyCLoPS_classified_ERA5_7024.parquet'
df2=pd.read_parquet(otrack)
dftc=df2
dftc=dftc[(dftc.ISOTIME.dt.hour.isin(hour_filter))&(dftc.ISOTIME.dt.year<=2024)&(dftc.ISOTIME.dt.year>=1988)].reset_index()
LAT=np.array(dftc.LAT)
LON=np.array(dftc.LON)
X=np.cos(LON*(np.pi/180))*np.cos(LAT*(np.pi/180))
Y=np.sin(LON*(np.pi/180))*np.cos(LAT*(np.pi/180))
Z=np.sin(LAT*(np.pi/180))
FST = np.unique(dftc.TID.values, return_index=1)[1]
LST=len(dftc)-np.unique(dftc.TID.values[::-1], return_index=1)[1]-1
id2=np.arange(0,len(dftc['LON']),1)
dftc['id1']=id2
SDAY=dftc.groupby(dftc['ISOTIME'])['id1'].apply(list)

hitid=np.ones(len(fst))-2
for k in range(len(fst)):
    for i in range(fst[k],lst[k]+1):
        dayn=np.where(SDAY.index==dfs.ISOTIME.iloc[i])[0]
        if len(dayn)==0:
            pass
        elif len(dayn)>0:
            dayn=dayn[0]
            T=cKDTree(list(zip(X[SDAY[dayn]],Y[SDAY[dayn]],Z[SDAY[dayn]])))
            idx=T.query_ball_point((x[i],y[i],z[i]),r=2.0001*(np.pi/180))
            if len(idx)==0:
                pass
            elif len(idx)>1:
                pass
            elif len(idx)==1:
                hitid[k]=dftc.TID.iloc[np.array(SDAY.iloc[dayn])[idx[0]]]
                break

begin_type=np.array(["Non-MS"]*len(fst),dtype=object)
end_type=np.array(["Non-ET"]*len(fst),dtype=object)
basin_label=np.array(["None"]*len(fst),dtype=object)
track_label=np.array(["None"]*len(fst),dtype=object)
for k in range(len(fst)):
    basin_label[k]=dfs.BASIN.iloc[fst[k]]
    dft=dftc[dftc.TID==hitid[k]].reset_index(drop=True)
    dft_pre=dft[dft.ISOTIME<fsttime.iloc[k]]
    if len(dft)==0:
        continue
    track_label[k]=dft.Track_Info.iloc[0]

    if np.any(dft_pre.Tropical_Flag==0):
    #if dfs.TID.iloc[fst[k]] in ib_tt_id:
        begin_type[k]="TT"
    elif 'MS' in dft.iloc[0].Track_Info:
        begin_type[k]="MS"
    if dfs.TID.iloc[lst[k]] in ib_land_id:
        end_type[k]="LAND"
    elif dfs.TID.iloc[lst[k]] in ib_et_id:
        end_type[k]="ET"

dftype=pd.DataFrame({'TID':np.array(dfs.TID[fst]),'hitid':hitid,'track_label':track_label,'basin_label':basin_label,'begin_type':begin_type,'end_type':end_type})
dftype.to_csv('../IB_tracks/ibtracs_ERA5_track_pair.csv', index=False)