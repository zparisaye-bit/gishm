# GISHM: GIS-based Hydrological Model
GISHM is a semi-distributed, high-performance hydro-informatics framework that combines an IronPython-based modeling environment with a compiled C# geoprocessing backend (`MapCalculate`). It is designed to overcome the “two-language problem” in spatial hydrology, enabling ultra-fast execution of high-resolution, continuous raster-based simulations on standard desktop computers.
## Geoscientific & Computational Features
Hybrid Architecture: Bypasses native Python memory bottlenecks by delegating cell-by-cell matrix operations to a compiled C# library.
Routing Diagnostics: Explicitly treats isochrone routing as a calibratable component by benchmarking 15 empirical Time-of-Concentration (Tc) equations to quantify epistemic uncertainty.
Subsurface Flexibility: Features both non-linear reservoir and storage-based recession methods for complex mountain aquifer drainage.
## 1. System Requirements & Dependencies
To run GISHM, your system must meet the following minimum requirements:
OS: Windows 10 or 11 (64-bit)
Framework: .NET Framework 4.5.2 (if you want to build MapCalculate solution)
Python: IronPython 2.7.9 (Embedded/Included in the release)
Hardware: Standard modern desktop CPU (e.g., Intel Core i3+ or equivalent), Minimum 4GB RAM.
## 2. Installation and Basic Usage
GISHM requires no complex compilation for the end-user. 
1. Clone or download this repository to your local machine. (Note: Ensure the path does not contain spaces or special characters).
2. Navigate to the ‘GISHM_model’ folder and run the executable ‘GISHM.exe’.
3. In the GUI, set the Working Directory to the ‘Sample Data’ folder provided in this repository.
4. The program will automatically ingest the necessary spatial maps (.asc) and time-series data (.tbl).
5. Navigate to the Parameter/Simulation tab and click Run.
6. View the generated hydrographs and performance metrics (NSE, KGE, Bias) in the Result/Display tab.
## 3. Reproducing the Study Results (Test Case)
The ‘Sample Data’ folder contains the exact spatial grids (90m resolution) and daily time-series forcing data (2003-2015) for the Arazkouseh watershed, Iran, as presented in our manuscript. 
Inputs: ‘maps’ subfolder (DEM, Soil, Land-use, Isochrone) and ‘timeseries’ subfolder (Precipitation, Temperature, Observed Streamflow).
Outputs: The model will output simulated surface runoff, baseflow, actual evapotranspiration, and total streamflow in the ‘Outputs’ directory as .tbl files.
## 4. User Guide & Documentation
For a detailed explanation of the input data formats, empirical Tc equations, and model parameters, please refer to the ‘Model Tutorial.pdf’ included in this repository. 
## License
This project is licensed under the Apache 2.0 License - see the [LICENSE] file for details.
