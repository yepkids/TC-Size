#!/bin/bash
# This script detects and tracks tropical cyclones in various models with the TempestExtremes software using the ZU method.
TEMPESTEXTREMESDIR=~/path_to_tempestextremes_directory

#CNRM-HR
inputfile=./file_list/CNRM-HR_lpsnode_in.txt
outputfile=./file_list/CNRM-HR_zu_out.txt
srun -n 256 $TEMPESTEXTREMESDIR/DetectNodes \
--in_data_list $inputfile --out_file_list $outputfile \
--searchbymin psl --closedcontourcmd "psl,200,5.5,0" \
--mergedist 6.0 \
--closedcontourcmd "psl,200.0,5.5,0;_DIFF(zg(250hPa),zg(500hPa)),-6,6.5,1.0" \
--outputcmd "psl,min,0;_VECMAG(uas,vas),max,2;orog,min,0" \
--timefilter "6hr" --logdir "./TE_log"

$TEMPESTEXTREMESDIR/StitchNodes \
--in_list "./file_list/CNRM-HR_zu_out.txt" --out "./classified_track/zu_tctrack/cnrm_zu_tracks.csv" \
--in_fmt "lon,lat,MSLP,WS,WS925,ZS" \
--range 8.0 --mintime "54h" --maxgap "24h" \
--threshold "WS,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;ZS,<=,15.0,10" --out_file_format "csv"

#CNRM-HR-COUP
inputfile=./file_list/CNRM-HR-COUP_lpsnode_in.txt
outputfile=./file_list/CNRM-HR-COUP_zu_out.txt
srun -n 256 $TEMPESTEXTREMESDIR/DetectNodes \
--in_data_list $inputfile --out_file_list $outputfile \
--searchbymin psl --closedcontourcmd "psl,200,5.5,0" \
--mergedist 6.0 \
--closedcontourcmd "psl,200.0,5.5,0;_DIFF(zg(250hPa),zg(500hPa)),-6,6.5,1.0" \
--outputcmd "psl,min,0;_VECMAG(uas,vas),max,2;orog,min,0" \
--timefilter "6hr" --logdir "./TE_log"

$TEMPESTEXTREMESDIR/StitchNodes \
--in_list "./file_list/CNRM-HR-COUP_zu_out.txt" --out "./classified_track/zu_tctrack/cnrm-coup_zu_tracks.csv" \
--in_fmt "lon,lat,MSLP,WS,WS925,ZS" \
--range 8.0 --mintime "54h" --maxgap "24h" \
--threshold "WS,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;ZS,<=,15.0,10" --out_file_format "csv"

#EC-Earth3P-HR
inputfile=./file_list/EC-Earth3P-HR_lpsnode_in.txt
outputfile=./file_list/EC-Earth3P-HR_zu_out.txt
srun -n 256 $TEMPESTEXTREMESDIR/DetectNodes \
--in_data_list $inputfile --out_file_list $outputfile \
--searchbymin psl --mergedist 6.0 --latname "latitude" --lonname "longitude" \
--closedcontourcmd "psl,200,5.5,0;_DIFF(zg(250hPa),zg(500hPa)),-6,6.5,1.0" \
--outputcmd "psl,min,0;_VECMAG(uas,vas),max,2;orog,min,0" \
--timefilter "6hr" --logdir "./TE_log"

$TEMPESTEXTREMESDIR/StitchNodes \
--in_list "./file_list/EC-Earth3P-HR_zu_out.txt" --out "./classified_track/zu_tctrack/ecearth3p_zu_tracks.csv" \
--in_fmt "lon,lat,MSLP,WS,WS925,ZS" \
--range 8.0 --mintime "54h" --maxgap "24h" \
--threshold "WS,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;ZS,<=,15.0,10" --out_file_format "csv"

#ECMWF-HR-mem1
inputfile=./file_list/ECMWF-HR-mem1_in.txt
outputfile=./file_list/ECMWF-HR-mem1_zu_out.txt
srun -n 256 $TEMPESTEXTREMESDIR/DetectNodes \
--in_data_list $inputfile --out_file_list $outputfile \
--searchbymin psl --closedcontourcmd "psl,200,5.5,0" \
--mergedist 6.0 \
--closedcontourcmd "psl,200.0,5.5,0;_DIFF(zg(250hPa),zg(500hPa)),-6,6.5,1.0" \
--outputcmd "psl,min,0;_VECMAG(uas,vas),max,2;_VECMAG(ua(925hPa),va(925hPa)),max,2;orog,min,0" \
--timefilter "6hr" --logdir "./TE_log"

$TEMPESTEXTREMESDIR/StitchNodes \
--in_list "./file_list/ECMWF-HR-mem1_zu_out.txt" --out "./out_track/echrm1_zu_tracks.csv" \
--in_fmt "lon,lat,MSLP,WS,WS925,ZS" \
--range 8.0 --mintime "54h" --maxgap "24h" \
--threshold "WS,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;ZS,<=,15.0,10" --out_file_format "csv"

#ECMWF-HR-mem1-COUP
inputfile=./file_list/ECMWF-HR-mem1-COUP_lpsnode_in.txt
outputfile=./file_list/ECMWF-HR-mem1-COUP_zu_out.txt
srun -n 256 $TEMPESTEXTREMESDIR/DetectNodes \
--in_data_list $inputfile --out_file_list $outputfile \
--searchbymin psl --closedcontourcmd "psl,200,5.5,0" \
--mergedist 6.0 \
--closedcontourcmd "psl,200.0,5.5,0;_DIFF(zg(250hPa),zg(500hPa)),-6,6.5,1.0" \
--outputcmd "psl,min,0;_VECMAG(uas,vas),max,2;orog,min,0" \
--timefilter "6hr" --logdir "./TE_log"

$TEMPESTEXTREMESDIR/StitchNodes \
--in_list "./file_list/ECMWF-HR-mem1-COUP_zu_out.txt" --out "./classified_track/zu_tctrack/echrm1-coup_zu_tracks.csv" \
--in_fmt "lon,lat,MSLP,WS,WS925,ZS" \
--range 8.0 --mintime "54h" --maxgap "24h" \
--threshold "WS,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;ZS,<=,15.0,10" --out_file_format "csv"

#ECMWF-LR-mem1
inputfile=./file_list/ECMWF-LR-mem1_in.txt
outputfile=./file_list/ECMWF-LR-mem1_zu_out.txt
srun -n 256 $TEMPESTEXTREMESDIR/DetectNodes \
--in_data_list $inputfile --out_file_list $outputfile \
--searchbymin psl --closedcontourcmd "psl,200,5.5,0" \
--mergedist 6.0 \
--closedcontourcmd "psl,200.0,5.5,0;_DIFF(zg(250hPa),zg(500hPa)),-6,6.5,1.0" \
--outputcmd "psl,min,0;_VECMAG(uas,vas),max,2;_VECMAG(ua(925hPa),va(925hPa)),max,2;orog,min,0" \
--timefilter "6hr" --logdir "./TE_log"

$TEMPESTEXTREMESDIR/StitchNodes \
--in_list "./file_list/ECMWF-LR-mem1_zu_out.txt" --out "./out_track/eclrm1_zu_tracks.csv" \
--in_fmt "lon,lat,MSLP,WS,WS925,ZS" \
--range 8.0 --mintime "54h" --maxgap "24h" \
--threshold "WS,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;ZS,<=,15.0,10" --out_file_format "csv"

#ERA5
inputfile=./file_list/ERA5_lpsnode_in.txt
outputfile=./file_list/ERA5_zu_out.txt
srun -n 256 $TEMPESTEXTREMESDIR/DetectNodes \
--in_data_list $inputfile --out_file_list $outputfile \
--searchbymin MSL --closedcontourcmd "MSL,200,5.5,0" \
--mergedist 6.0 \
--mergeequal \
--closedcontourcmd "MSL,200.0,5.5,0;_DIFF(Z(250hPa),Z(500hPa)),-58.8,6.5,1.0" \
--outputcmd "MSL,min,0;_VECMAG(VAR_10U,VAR_10V),max,2;ZS,min,0" \
--timefilter "6hr" --logdir "./TE_log" --latname "latitude" --lonname "longitude"

$TEMPESTEXTREMESDIR/StitchNodes \
--in_list "./file_list/ERA5_zu_out.txt" --out "./classified_track/zu_tctrack/era5_zu_tracks.csv" \
--in_fmt "lon,lat,MSLP,WS,ZS" \
--range 8.0 --mintime "54h" --maxgap "24h" \
--threshold "WS,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;ZS,<=,147.0,10" --out_file_format "csv"

#ERA5 deg1
inputfile=./file_list/ERA5deg1_lpsnode_in.txt
outputfile=./file_list/ERA5deg1_zu_out.txt
srun -n 256 $TEMPESTEXTREMESDIR/DetectNodes \
--in_data_list $inputfile --out_file_list $outputfile \
--searchbymin MSL --closedcontourcmd "MSL,200,5.5,0" \
--mergedist 6.0 \
--closedcontourcmd "MSL,200.0,5.5,0;_DIFF(Z(300hPa),Z(500hPa)),-58.8,6.5,1.0" \
--outputcmd "MSL,min,0;_VECMAG(VAR_10U,VAR_10V),max,2;ZS,min,0" \
--timefilter "6hr" --logdir "./TE_log" --latname "latitude" --lonname "longitude"

$TEMPESTEXTREMESDIR/StitchNodes \
--in_list "./file_list/ERA5deg1_zu_out.txt" --out "./classified_track/zu_tctrack/era5deg1_zu_tracks.csv" \
--in_fmt "lon,lat,MSLP,WS,ZS" \
--range 8.0 --mintime "54h" --maxgap "24h" \
--threshold "WS,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;ZS,<=,147.0,10" --out_file_format "csv"

#HadGEM-HR
inputfile=./file_list/HadGEM-HR_lpsnode_in.txt
outputfile=./file_list/HadGEM-HR_zu_out.txt
srun -n 256 $TEMPESTEXTREMESDIR/DetectNodes \
--in_data_list $inputfile --out_file_list $outputfile \
--searchbymin psl --closedcontourcmd "psl,200,5.5,0" \
--mergedist 6.0 \
--closedcontourcmd "psl,200.0,5.5,0;_DIFF(zg7h(250hPa),zg7h(500hPa)),-6,6.5,1.0" \
--outputcmd "psl,min,0;_VECMAG(uas,vas),max,2;orog,min,0" \
--timefilter "6hr" --logdir "./TE_log"

$TEMPESTEXTREMESDIR/StitchNodes \
--in_list "./file_list/HadGEM-HR_zu_out.txt" --out "./classified_track/zu_tctrack/hadgem-hr_zu_tracks.csv" \
--in_fmt "lon,lat,MSLP,WS,WS925,ZS" \
--range 8.0 --mintime "54h" --maxgap "24h" \
--threshold "WS,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;ZS,<=,15.0,10" --out_file_format "csv"

#HadGEM-HR-COUP
inputfile=./file_list/HadGEM-HR-COUP_lpsnode_in.txt
outputfile=./file_list/HadGEM-HR-COUP_zu_out.txt
srun -n 256 $TEMPESTEXTREMESDIR/DetectNodes \
--in_data_list $inputfile --out_file_list $outputfile \
--searchbymin psl --closedcontourcmd "psl,200,5.5,0" \
--mergedist 6.0 \
--closedcontourcmd "psl,200.0,5.5,0;_DIFF(zg7h(250hPa),zg7h(500hPa)),-6,6.5,1.0" \
--outputcmd "psl,min,0;_VECMAG(uas,vas),max,2;orog,min,0" \
--timefilter "6hr" --logdir "./TE_log"

$TEMPESTEXTREMESDIR/StitchNodes \
--in_list "./file_list/HadGEM-HR-COUP_zu_out.txt" --out "./classified_track/zu_tctrack/hadgem-coup_zu_tracks.csv" \
--in_fmt "lon,lat,MSLP,WS,WS925,ZS" \
--range 8.0 --mintime "54h" --maxgap "24h" \
--threshold "WS,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;ZS,<=,15.0,10" --out_file_format "csv"

#IPSL-HR
inputfile=./file_list/IPSL-HR_in.txt
outputfile=./file_list/IPSL-HR_zu_out.txt
srun -n 27 $TEMPESTEXTREMESDIR/DetectNodes \
--in_data_list $inputfile --out_file_list $outputfile \
--searchbymin psl --closedcontourcmd "psl,200,5.5,0" \
--mergedist 6.0 \
--closedcontourcmd "psl,200.0,5.5,0;_DIFF(zg(250hPa),zg(500hPa)),-6,6.5,1.0" \
--outputcmd "psl,min,0;_VECMAG(uas,vas),max,2;_VECMAG(ua(925hPa),va(925hPa)),max,2;orog,min,0" \
--timefilter "6hr" --logdir "./TE_log"

$TEMPESTEXTREMESDIR/StitchNodes \
--in_list "./file_list/IPSL-HR_zu_out.txt" --out "./out_track/ipslhr_zu_tracks.csv" \
--in_fmt "lon,lat,MSLP,WS,WS925,ZS" \
--range 8.0 --mintime "54h" --maxgap "24h" \
--threshold "WS,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;ZS,<=,15.0,10" --out_file_format "csv"

#IPSL-VHR
inputfile=./file_list/IPSL-VHR_in.txt
outputfile=./file_list/IPSL-VHR_zu_out.txt
srun -n 256 $TEMPESTEXTREMESDIR/DetectNodes \
--in_data_list $inputfile --out_file_list $outputfile \
--searchbymin psl --closedcontourcmd "psl,200,5.5,0" \
--mergedist 6.0 \
--closedcontourcmd "psl,200.0,5.5,0;_DIFF(zg(250hPa),zg(500hPa)),-6,6.5,1.0" \
--outputcmd "psl,min,0;_VECMAG(uas,vas),max,2;_VECMAG(ua(925hPa),va(925hPa)),max,2;orog,min,0" \
--timefilter "6hr" --logdir "./TE_log"

$TEMPESTEXTREMESDIR/StitchNodes \
--in_list "./file_list/IPSL-VHR_zu_out.txt" --out "./out_track/ipslvhr_zu_tracks.csv" \
--in_fmt "lon,lat,MSLP,WS,WS925,ZS" \
--range 8.0 --mintime "54h" --maxgap "24h" \
--threshold "WS,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;ZS,<=,15.0,10" --out_file_format "csv"

#MRI-H
inputfile=./file_list/MRI-H_in.txt
outputfile=./file_list/MRI-H_zu_out.txt
srun -n 27 $TEMPESTEXTREMESDIR/DetectNodes \
--in_data_list $inputfile --out_file_list $outputfile \
--searchbymin psl --closedcontourcmd "psl,200,5.5,0" \
--mergedist 6.0 \
--closedcontourcmd "psl,200.0,5.5,0;_DIFF(zg(250hPa),zg(500hPa)),-6,6.5,1.0" \
--outputcmd "psl,min,0;_VECMAG(uas,vas),max,2;_VECMAG(ua(925hPa),va(925hPa)),max,2;orog,min,0" \
--timefilter "6hr" --logdir "./TE_log"

$TEMPESTEXTREMESDIR/StitchNodes \
--in_list "./file_list/MRI-H_zu_out.txt" --out "./out_track/mrih_zu_tracks.csv" \
--in_fmt "lon,lat,MSLP,WS,WS925,ZS" \
--range 8.0 --mintime "54h" --maxgap "24h" \
--threshold "WS,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;ZS,<=,15.0,10" --out_file_format "csv"

#MRI-S
inputfile=./file_list/MRI-S_in.txt
outputfile=./file_list/MRI-S_zu_out.txt
srun -n 256 $TEMPESTEXTREMESDIR/DetectNodes \
--in_data_list $inputfile --out_file_list $outputfile \
--searchbymin psl --closedcontourcmd "psl,200,5.5,0" \
--mergedist 6.0 \
--closedcontourcmd "psl,200.0,5.5,0;_DIFF(zg(250hPa),zg(500hPa)),-6,6.5,1.0" \
--outputcmd "psl,min,0;_VECMAG(uas,vas),max,2;_VECMAG(ua(925hPa),va(925hPa)),max,2;orog,min,0" \
--timefilter "6hr" --logdir "./TE_log"

$TEMPESTEXTREMESDIR/StitchNodes \
--in_list "./file_list/MRI-S_zu_out.txt" --out "./out_track/mris_zu_tracks.csv" \
--in_fmt "lon,lat,MSLP,WS,WS925,ZS" \
--range 8.0 --mintime "54h" --maxgap "24h" \
--threshold "WS,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;ZS,<=,15.0,10" --out_file_format "csv"

