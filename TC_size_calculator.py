# This program calculates the size of tropical cyclones (TCs) from wind radii data output by NodeFileEditor.
# Author: Yushan Han
# Date: Aug 2025

import numpy as np
import time
import pandas as pd
#import multiprocessing as mp
# Constants
model_key_list=('era5' 'era5deg1' 'cnrm' 'cnrm-coup' 'ecearth3p' 'echrm1' 'eclrm1' 'echrm1-coup' 'hadgm' 'hadgm-coup' 'ipslhr' 'ipslvhr' 'mrih' 'mris')
#corresponding model names: 'ERA5' 'ERA5deg1' 'CNRM-HR' 'CNRM-HR-COUP' 'EC-Earth3P-HR' 'ECMWF-HR-mem1' 'ECMWF-LR-mem1' 'ECMWF-HR-mem1-COUP' 'HadGEM-HR' 'HadGEM-HR-COUP' 'IPSL-HR' 'IPSL-VHR' 'MRI-H' 'MRI-S'
ib_file_path="IB_track_file/ibtracs_radii_all.csv" # Input IB track file directory

# The function to read CSV files and process wind radii
def read_csv(file_path,profile_spacing,mode):
    if mode == 'Model':
        dft=pd.read_csv(file_path, sep=", ", na_values=' nan', engine='python')
        dftc=pd.read_parquet(f"classified_track/SyCLoPS_track/SyCLoPS_classified_{model_name}.parquet")
        cond=(dftc['Adjusted_Label'].str.contains('TC')) & (dftc['Track_Info'].str.contains('TC'))
        dftc=dftc[cond].reset_index(drop=True)
        if 'WS' not in dft.columns:
            dft['WS']=dftc['WS'].values
        try:
            dft.insert(5, 'ISOTIME', pd.to_datetime(dict(year=dft.year, month=dft.month, day=dft.day,hour=dft.hour)))
        except:
            pass
        dft['r30']=dft['r30'].apply(lambda x: eval(x.strip('"'), {"__builtins__": None}, {"nan": np.nan}))
        dft.rename(columns={'lat':'LAT','lon':'LON'}, inplace=True)
        dft.drop(columns=['RWP'], inplace=True)
        dft['NE34'] = dft['r30'].apply(lambda x: np.array(x)[0])
        dft['SE34'] = dft['r30'].apply(lambda x: np.array(x)[1])
        dft['SW34'] = dft['r30'].apply(lambda x: np.array(x)[2])
        dft['NW34'] = dft['r30'].apply(lambda x: np.array(x)[3])
        dft['NE34'] = np.where(dft['NE34'] > 0, (dft['NE34'] - profile_spacing/2) * 111 / 1.852, 0)
        dft['SE34'] = np.where(dft['SE34'] > 0, (dft['SE34'] - profile_spacing/2) * 111 / 1.852, 0)
        dft['SW34'] = np.where(dft['SW34'] > 0, (dft['SW34'] - profile_spacing/2) * 111 / 1.852, 0)
        dft['NW34'] = np.where(dft['NW34'] > 0, (dft['NW34'] - profile_spacing/2) * 111 / 1.852, 0)
        dft['WS'] = dft.WS/0.5144
    else: # IB mode
        dft = pd.read_csv(file_path,keep_default_na=False)
        dft.rename(columns={'SID':'TID','ISO_TIME':'ISOTIME','USA_PRES':'MSLP'}, inplace=True)
        dft['ISOTIME'] = pd.to_datetime(dft['ISOTIME'])
        dft=dft[dft.WS>=34] # Filter for tropical storm intensity and above (TC definition)
        # Optional: Filter data based on basin and year
        dft = dft[(((dft['BASIN']=='NA') & (dft.ISOTIME.dt.year>=1988))| ((dft['BASIN']=='WP') & (dft.ISOTIME.dt.year>=2002))) & (dft.ISOTIME.dt.year<=2024)]
    df_rad = dft[['NE34', 'SE34', 'SW34', 'NW34']].astype(np.float64) # Extract radius data
    return df_rad,dft

# The function to compute mean radii
def compute_radii(rad_cut, rad_conv=1.0):
    # Interpolate to get radii at every degree
    rad_cut=np.append(rad_cut,rad_cut[0])  
    angles = np.linspace(0, 2 * np.pi, 360, endpoint=False)+np.pi/4
    quadrant_bounds = np.array([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])+np.pi/4
    r_cut_all = np.interp(angles, quadrant_bounds, rad_cut) * rad_conv 
    # Calculate the area-equivalent mean radius
    Area=0
    for i in range(360):
        Area = Area + 0.5 * r_cut_all[i]**2 * (np.pi / 180)
    MeanRadCut = (Area / np.pi)**0.5

    return MeanRadCut

if __name__ == "__main__":
    for name in model_key_list:
        profile_spacing=0.25 # degrees
        mode = 'Model'
        print("Timing function...")
        start_time = time.time()
        model_name = name
        file_path=f"path_to_NodeFileEditor_outputs/{model_name}_windrad.csv"
        conv=1 #Conversion ratio for radii
        print(f"Processing model: {model_name}")
        if model_name == 'IBTrACS':
            mode = 'IB'
            conv=0.85
            file_path=ib_file_path
        elif model_name =='ECMWF-LR-mem1':
            profile_spacing=0.5
        df_rad,dft=read_csv(file_path=file_path,profile_spacing=profile_spacing,mode=mode)
        Rad_arr = np.zeros(len(df_rad), dtype=np.float64)
        # Calculate mean radii for each record
        for i in range(len(df_rad)): 
            Rad_arr[i] = compute_radii(df_rad.iloc[i].values, rad_conv=conv)
        dft['MeanRad'] = np.round(Rad_arr)
        # Save the results to CSV
        if mode=='IB':
            dft.to_csv(f"IB_track_file/IBTrACS_TC_Size.csv", index=False)
        else:
            dft.to_csv(f"path_to_store/{model_name}_TC_Size.csv", index=False)
        fast_time = time.time() - start_time
        print(f"TC size calculation time: {fast_time:.4f} seconds")

