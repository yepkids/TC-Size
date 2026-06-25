# TC size calculator and analysis

Author:  Yushan Han  
Email:   yshhan@ucdavis.edu

Copyright 2026 Yushan Han

Preprint: [The Evolution of Tropical Cyclone Intensity and Size in Observations and HighResMIP Models](https://doi.org/10.22541/essoar.177038847.73410174/v1)


Introduction
=====

This repository contains software for detecting and calculating the size of tropical cyclones (TCs) in atmospheric reanalysis products and model outputs. This software was used to produce the results presented in our paper (see above for the preprint link). The repository also contains the tools and Jupyter notebooks used to create the figures in the paper. Data produced for the paper can be downloaded via the links provided in the corresponding subfolders. 

Details of how we define and calcualte TC size can be found in Section 2.5 and supporting information text S5 of the paper.

Dependencies
=====

Wind profile detection requires the installation of TempestExtremes (TE) software, which is available at: [https://github.com/ClimateGlobalChange/tempestextremes]

Some additional Python packages may be required. Please refer to the relevant Python/Jupyter notebook script for more information.

Usage
=====

To calculate TC size in model outputs, first have your objectively detected TC tracks ready in the `classified_track` folder, then Run:

```python
python TC_size_calculator.py
```
This program generates the nodefile used by TE to calculate wind radii and ultimately output the calculated TC size for each model. Run `python TC_size_calculator.py --help` to view the customization options, which includes mode, output directory, worker numbers for running TE, etc.

Adjust the parameters and file paths in the first section of the `TC_size_calculator.py` according to your needs.

Other useful tools used in our study are available in the `tools` folder. These include:

1. `assign_basin.py`: This tool assigns basin labels to each TC or low-pressure system (LPS) record based on the basin mask file (`basin_mask_05deg.nc`), and output files to the `final_track_file` directory.

2. `obs_track_type.py`: Assign a precursor type and a posterior scenario label to each observed IBTrACS TC track, based on the ERA5 LPS tracks that are classified by SyCLoPS. Details on the definition of track type can be found in Section 2.4 of the paper.

3. `processing_IB.py`: Preprocesses the raw IBTrACS file to meet the needs of the study.

4. `TC_detection_skill_node.py`: Computes TC detection skills (hit rate, false alarm rate, and CSI) at the node level of an objective TC dataset.

Publications
============
If you use this software please cite our publications:

[https://doi.org/10.1029/2024JD041287] Han, Y. and P.A. Ullrich (2025) "The System for Classification of Low-Pressure Systems (SyCLoPS): An all-in-one objective framework for large-scale datasets" J. Geophys. Res. Atm. 130 (1), e2024JD041287, doi: 10.1029/2024JD041287.

[https://dx.doi.org/10.5194/gmd-14-5023-2021] Ullrich, P.A., C.M. Zarzycki, E.E. McClenny, M.C. Pinheiro, A.M. Stansfield and K.A. Reed (2021) "TempestExtremes v2.1: A community framework for feature detection, tracking and analysis in large datasets" Geosci. Model. Dev. 14, pp. 5023–5048, doi: 10.5194/gmd-14-5023-2021.

[http://dx.doi.org/10.5194/gmd-2016-217] Ullrich, P.A. and C.M. Zarzycki (2017) "TempestExtremes v1.0: A framework for scale-insensitive pointwise feature tracking on unstructured grids" Geosci. Model. Dev. 10, pp. 1069-1090, doi: 10.5194/gmd-10-1069-2017. 
