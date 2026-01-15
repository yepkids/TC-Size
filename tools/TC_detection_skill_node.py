# This script evaluates tropical cyclone (TC) detection skill by comparing model output with IBTrACS best track data at the node level.
# It uses spatial matching (via cKDTree) and various criteria to compute hit rates, false alarm rates, and skill scores.
# Parallel processing is used to speed up the computation.
# Author: Yushan Han
# Date: Oct 2025

import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import multiprocess as ma


# The function to calculate hit rates
def hit_rate(i):
    hit=np.zeros(len(fst.iloc[i]))
    dft=dflow[dflow.ISOTIME==fst.index[i]]
    if not dft.empty:
        LON=dft.LON; LAT=dft.LAT
        X=np.cos(LON*(np.pi/180))*np.cos(LAT*(np.pi/180))
        Y=np.sin(LON*(np.pi/180))*np.cos(LAT*(np.pi/180))
        Z=np.sin(LAT*(np.pi/180))
        T=cKDTree(list(zip(X,Y,Z)))
        for i1,i2 in enumerate(fst.iloc[i]):          
            idx=T.query_ball_point((x[i2],y[i2],z[i2]),r=2.0001*(np.pi/180))
            ibMSLP = dfib_usa.iloc[i2]['WMO_PRES']
            if len(idx)>1:
                ind = T.query([x[i2],y[i2],z[i2]],k=1)[1]
                modMSLP = dft.iloc[ind]['MSLP']/100
                #print(modMSLP, ibMSLP)
                if modMSLP > 1005 and ibMSLP > -1500:
                    hit[i1]=1
                else:
                    hit[i1]=1
            elif len(idx)==1:
                ind = idx[0]
                modMSLP = dft.iloc[ind]['MSLP']/100
                #print(modMSLP, ibMSLP)
                if modMSLP > 1005 and modMSLP - ibMSLP > -1500:
                    hit[i1]=1
                else:
                    hit[i1]=1
            else:
                continue
    return hit
# The function to calculate adjustments for hit rates
def hit_rate_adj(i):
    adj=np.zeros(len(fst.iloc[i]))
    dft=dfc[dfc.ISOTIME==fst.index[i]]
    if not dft.empty:
        LON=dft.LON; LAT=dft.LAT
        X=np.cos(LON*(np.pi/180))*np.cos(LAT*(np.pi/180))
        Y=np.sin(LON*(np.pi/180))*np.cos(LAT*(np.pi/180))
        Z=np.sin(LAT*(np.pi/180))
        T=cKDTree(list(zip(X,Y,Z)))
        for i1,i2 in enumerate(fst.iloc[i]):
            idx=T.query_ball_point((x[i2],y[i2],z[i2]),r=2.0001*(np.pi/180))
            if len(idx)>0:
                continue
            else:
                adj[i1]=2
    return adj
# The function to calculate false alarm rates
def far(i):
    far = [(i0, 1) for i0 in FST.iloc[i]]
    dft=dfib_usa[dfib_usa.ISO_TIME==FST.index[i]]
    if not dft.empty:
        lon=dft.LON%360; lat=dft.LAT
        x=np.cos(lon*(np.pi/180))*np.cos(lat*(np.pi/180))
        y=np.sin(lon*(np.pi/180))*np.cos(lat*(np.pi/180))
        z=np.sin(lat*(np.pi/180))
        T=cKDTree(list(zip(x,y,z)))
        for i1,i2 in enumerate(FST.iloc[i]):
            idx=T.query_ball_point((X[i2],Y[i2],Z[i2]),r=2.0001*(np.pi/180))
            modMSLP = dflow.iloc[i2]['MSLP']/100
            modLAT= dflow.iloc[i2]['LAT']
            if len(idx)>1:
                ind = T.query([X[i2],Y[i2],Z[i2]],k=1)[1]
                ibMSLP = dft.iloc[ind]['WMO_PRES']
                if modMSLP > 1005 and modMSLP - ibMSLP > 15:
                    far[i1]=(i2,0)
                else:
                    far[i1]=(i2,0)
            elif len(idx)==1:
                ind = idx[0]
                ibMSLP = dft.iloc[ind]['WMO_PRES']
                if modMSLP > 1005 and modMSLP - ibMSLP > 15:
                    far[i1]=(i2,0)
                else:
                    far[i1]=(i2,0)
            else:
                far[i1]=(i2,1)
    return far
# The function to calculate adjustments for false alarm rates
def far_hr_adj(i):
    adj=np.zeros(len(FST2.iloc[i]))
    dft=dfib_all[dfib_all.ISO_TIME==FST2.index[i]]
    if not dft.empty:
        lon=dft.LON; lat=dft.LAT
        x=np.cos(lon*(np.pi/180))*np.cos(lat*(np.pi/180))
        y=np.sin(lon*(np.pi/180))*np.cos(lat*(np.pi/180))
        z=np.sin(lat*(np.pi/180))
        T=cKDTree(list(zip(x,y,z)))
        for i1,i2 in enumerate(FST2.iloc[i]):
            idx=T.query_ball_point((X2[i2],Y2[i2],Z2[i2]),r=2.0001*(np.pi/180))
            modMSLP = dfc_tr.iloc[i2]['MSLP']/100
            if len(idx)>1:
                ind = T.query([X2[i2],Y2[i2],Z2[i2]],k=1)[1]
                modMSLP = dfc_tr.iloc[i2]['MSLP']/100
                ibMSLP = dft.iloc[ind]['WMO_PRES']
                ibLabel= dft.iloc[ind]['USA_SSHS']
                modLabel = dfc_tr.iloc[i2]['Adjusted_Label']
                modTlabel = dfc_tr.iloc[i2]['Track_Info']
                modUpp = dfc_tr.iloc[i2]['UPPTKCC']
                modvo = dfc_tr.iloc[i2]['VO500AVG']
                if modMSLP < 1005 and (ibLabel ==-1 or ibLabel ==-3) and modLabel == 'TC' and 'TC' in modTlabel:
                    adj[i1]=1
                elif modLabel != 'TC' and ibLabel >= 0:
                    if  ((modMSLP - ibMSLP > 10) and (modMSLP > 1005)) or (modUpp == 0) or (modvo <= 0):
                        adj[i1]=2       
            elif len(idx)==1:
                ind = idx[0]
                modMSLP = dfc_tr.iloc[i2]['MSLP']/100
                ibMSLP = dft.iloc[ind]['WMO_PRES']
                ibLabel= dft.iloc[ind]['USA_SSHS']
                modLabel = dfc_tr.iloc[i2]['Adjusted_Label']
                modTlabel = dfc_tr.iloc[i2]['Track_Info']
                modUpp = dfc_tr.iloc[i2]['UPPTKCC']
                modvo = dfc_tr.iloc[i2]['VO500AVG']
                if modMSLP < 1005 and (ibLabel ==-1 or ibLabel ==-3) and modLabel == 'TC' and 'TC' in modTlabel:
                    adj[i1]=1
                elif modLabel != 'TC' and ibLabel >= 0:
                    if ((modMSLP - ibMSLP > 10) and (modMSLP > 1005)) or (modUpp == 0) or (modvo <= 0):
                        adj[i1]=2
    return adj

dfin = pd.read_parquet("path_to_syclops_input_file/SyCLoPS_input_ERA5.parquet") # The input catalog of ERA5 SyCLoPS tracks
dfc = pd.read_parquet("path_to_syclops_classified_file/SyCLoPS_classified_ERA5.parquet") # The classified SyCLoPS track catalog
# Prepare LPS catalog dataframes
dfc['MSLPCC20'] = dfin['MSLPCC20']
dfc['UPPTKCC'] = dfin['UPPTKCC']
dfc['VO500AVG']= dfin['VO500AVG']
dfc['LOWTKCC'] = dfin['LOWTKCC']
dfc_tc = dfc[(dfc['Track_Info'].str.contains('TC')) & (dfc.Adjusted_Label=='TC')].reset_index(drop=True)
dfc_tr = dfc[(dfc.Tropical_Flag==1)].reset_index(drop=True)
dfc_tc=dfc_tc[(dfc_tc.ISOTIME.dt.year>=1988)&(dfc_tc.ISOTIME.dt.year<=2014)].reset_index()
dfc_tr=dfc_tr[(dfc_tr.ISOTIME.dt.year>=1988)&(dfc_tr.ISOTIME.dt.year<=2014)].reset_index()
labels = dfc_tc.Short_Label.values.copy()
tid_values = dfc_tc.TID.values
fi = dfc_tc.groupby('TID').head(1).index
li = dfc_tc.groupby('TID').tail(1).index
# Load IBTrACS data
ibfile='../IB_tracks/ibtracs_rad_all.csv'
dfib=pd.read_csv(ibfile)
dfib['ISO_TIME']=pd.to_datetime(dfib.ISO_TIME)
dfib_usa=dfib[(dfib.ISO_TIME.dt.year>=1988)&(dfib.ISO_TIME.dt.year<=2014)&(dfib.WS>=34)].reset_index()
dfib_all=dfib[(dfib.ISO_TIME.dt.year>=1988)&(dfib.ISO_TIME.dt.year<=2014)].reset_index()
dfib_usa=dfib_usa[['SID','WMO_PRES','USA_PRES','WS','BASIN','SUBBASIN','ISO_TIME','LAT','LON','USA_STATUS', 'USA_SSHS']]
dfib_all=dfib_all[['SID','WMO_PRES','USA_PRES','WS','BASIN','SUBBASIN','ISO_TIME','LAT','LON','USA_STATUS', 'USA_SSHS']]
# Prepare for matching
dflow = dfc_tc
LON=dflow.LON; LAT=dflow.LAT
LON2=dfc_tr.LON; LAT2=dfc_tr.LAT
id2=np.arange(0,len(dflow),1)
dflow['id1']=id2
id2=np.arange(0,len(dfc_tr),1)
dfc_tr['id1']=id2
id2=np.arange(0,len(dfib_usa),1)
dfib_usa['id1']=id2
X=np.array(np.cos(LON*(np.pi/180))*np.cos(LAT*(np.pi/180)))
Y=np.array(np.sin(LON*(np.pi/180))*np.cos(LAT*(np.pi/180)))
Z=np.array(np.sin(LAT*(np.pi/180)))
FST=dflow.groupby(dflow['ISOTIME'])['id1'].apply(list)
X2=np.array(np.cos(LON2*(np.pi/180))*np.cos(LAT2*(np.pi/180)))
Y2=np.array(np.sin(LON2*(np.pi/180))*np.cos(LAT2*(np.pi/180)))
Z2=np.array(np.sin(LAT2*(np.pi/180)))
FST2=dfc_tr.groupby(dfc_tr['ISOTIME'])['id1'].apply(list)
lat=dfib_usa.LAT;lon=dfib_usa.LON
x=np.array(np.cos(lon*(np.pi/180))*np.cos(lat*(np.pi/180)))
y=np.array(np.sin(lon*(np.pi/180))*np.cos(lat*(np.pi/180)))
z=np.array(np.sin(lat*(np.pi/180)))
fst=dfib_usa.groupby(dfib_usa['ISO_TIME'])['id1'].apply(list)

# Parallel processing to compute hit rates and false alarm rates
pool_obj = ma.Pool(64)
hitlst=pool_obj.map(hit_rate,range(len(fst)))
farlst=pool_obj.map(far,range(len(FST)))
adjlst2=pool_obj.map(hit_rate_adj,range(len(fst)))
adjlst=pool_obj.map(far_hr_adj,range(len(FST2)))
pool_obj.close()
# Aggregate results and calculate CSI and adjusted CSI
adjlstf=np.concatenate(adjlst)
adjlstf2=np.concatenate(adjlst2)
hitlstf=np.concatenate(hitlst)
farlstf=np.concatenate(farlst)
farlstf=np.array([i[1] for i in farlstf])
hitrate=len(hitlstf[hitlstf==1])/len(hitlstf)
farrate=len(farlstf[farlstf==1])/len(farlstf)
#dfo['FA']=farlstf
hit_adj = (len(adjlstf[adjlstf==2])+len(adjlstf2[adjlstf2==2]))/ len(hitlstf)
far_adj = len(adjlstf[adjlstf==1])/ len(farlstf)
print(hit_adj, far_adj)
CSI=len(hitlstf[hitlstf==1])/(len(hitlstf[hitlstf==1])+len(hitlstf[hitlstf==0])+len(farlstf[farlstf==1]))
CSI_adj=len(hitlstf[hitlstf==1])/(len(hitlstf[hitlstf==1])+len(hitlstf[hitlstf==0])-len(adjlstf[adjlstf>0])-len(adjlstf2[adjlstf2>0])+len(farlstf[farlstf==1]))
print(hitrate, farrate, CSI, CSI_adj)
