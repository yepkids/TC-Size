#bin/bash
# This script calculates tropical cyclone quadrant wind profiles and wind radii for each model's output using the TempestExtremes NodeFileEditor tool.
TEMPESTEXTREMESDIR=~/path_to_tempestextremes_directory

model_key_list=('era5' 'era5deg1' 'cnrm' 'cnrm-coup' 'ecearth3p' 'echrm1' 'eclrm1' 'echrm1-coup' 'hadgm' 'hadgm-coup' 'ipslhr' 'ipslvhr' 'mrih' 'mris')
#corresponding model names: 'ERA5' 'ERA5deg1' 'CNRM-HR' 'CNRM-HR-COUP' 'EC-Earth3P-HR' 'ECMWF-HR-mem1' 'ECMWF-LR-mem1' 'ECMWF-HR-mem1-COUP' 'HadGEM-HR' 'HadGEM-HR-COUP' 'IPSL-HR' 'IPSL-VHR' 'MRI-H' 'MRI-S'
# u10 and v10 variable names for each model
u10_list=('VAR_10U' 'VAR_10U' 'uas' 'uas' 'uas' 'uas' 'uas' 'uas' 'uas' 'uas' 'uas' 'uas' 'uas' 'uas')
v10_list=('VAR_10U' 'VAR_10U' 'vas' 'vas' 'vas' 'vas' 'vas' 'vas' 'vas' 'vas' 'vas' 'vas' 'vas' 'vas')

# Write commands of each model to a txt file for GNU parallel
rm -rf windrad_par.txt
# Input data list should include filenames of files that contain u10 (uas) and v10 (vas) variables
for ((i=0; i<${#data_list1[@]}; i++)); do
echo "$TEMPESTEXTREMESDIR/NodeFileEditor \
--in_nodefile 'editor_nodefile/${data_list1[i]}_tc_nodefile.txt' --in_nodefile_type SN \
--in_data_list 'file_list/${data_list2[i]}_uv10in.txt' --out_nodefile 'path_to_store/${data_list2[i]}_windrad.csv' \
--in_fmt 'lon,lat,MSLP' \
--out_fmt 'lon,lat,MSLP,RWP,r30' --out_nodefile_format csv \
--calculate 'RWP=radial_quadrant_profile(_VECMAG(${u10_list[i]},${v10_list[i]}),53,0.2500001);r30=firstwhere(RWP,fallsbelow,15.43,3.0)'" >> windrad_par.txt
done

# you may need to load GNU parallel module first
# module load parallel
parallel -a windrad_par.txt -j 14 --ungroup # This runs 14 jobs in parallel to save time; adjust -j value as needed
