# MODIS_import

**MODIS_import** is a package that allows for automatic import of Snow cover NDSI and Land Surface Temperature (LST)
from MODIS and produces a netCDF file from configuration files. The user only needs to provide a .toml and a .csv
configuration files. Furthermore, credentials to AppEARS API (https://appeears.earthdatacloud.nasa.gov/api/) need
to be specified in a .netrc file.

Thanks to this tool, the user will get snow cover and land surface temperature time series for any point location
into a standardized netCDF format.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install **MODIS_import** (find the PyPi page here: https://pypi.org/project/MODIS_import/).

```bash
pip install MODIS_import
```

Install all the required packages (dependencies) from the *requirements.txt*  file.


```bash
pip install -r requirements.txt
```

Place *requirements.txt* in the directory where you plan to run the command. If the file is in a different directory, specify its path, for example, *path/to/requirements.txt*.

## Usage

The package is better used directly on the command line with the built-in CLI

```bash
MODIS_import -f /<path>/<folder_name>/par/MODIS_config.toml
```

It is recommended to stick to the folder structure adopted in the folder *MODIS_import/examples/MODIS_test_Martha*.
Simply create a folder for each application, and within it, create a *par/* folder. This will hold two configuration
files. Create the following directory structure::

    /<folder_name>
        /par
            MODIS_config.toml
            MODIS_stations.csv
    

The two files are:

1. **MODIS_config.toml**: downloads and scales reanalysis data to produce meteorological time series at any point location:

```
[name]
task_name = <task_name>

[directories]
# this is the home directory that will contain par/ and download/
home_dir        = '<path>/<folder_name>'
# this is the download destination directory
dest_dir        = '<path>/<folder_name>/download'
# directory where the .netrc credential file is stored
credential_dir  = '<path_to_credential_directory>'
# path to the csv configuration file 
config_csv_path = '<path>/<folder_name>/par/MODIS_stations.csv'

[config]
# in the format YYYY/MM/DD to match with GlobSim
startDate  = '<YYYY/MM/DD>'
endDate    = '<YYYY/MM/DD>'

[download]
# how long shall we wait (in seconds) between submitting a task and giving up, suggested 1day=86400s
max_wait   = 86400
# time between two status checks (in seconds), suggested 30s
time_sleep = 30
```

2. **MODIS_stations.csv**: Land surface model of the mass and energy balance of the hydrological cycle which simulates ground thermal properties:

```
id,latitude,longitude
Site_name_1,lat_1,lon_1
...
Site_name_n,lat_n,lon_n
```

Once the package is run, a new *download/* foilder is automatically created, and is populated with two csv files
containing the snow cover and land surface temperature data, together with a text log file. Finally, when the
conversion is done too, the final netCDF file is also created.
We get the following directory structure::

    /<folder_name>
        /par
            MODIS_config.toml
            MODIS_stations.csv
        /download
            <task_name>_MOD10A1_061_results.csv
            <task_name>_MOD11A1_061_results.csv
            MODIS_log_<datetime>.txt


## Examples

The user can find some inspiration on how to use **MODIS_import** by looking at the examples provided.

## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
