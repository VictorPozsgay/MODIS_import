"""This module downloads the MODIS data and converts it to
netCDF4 file automatically."""


from MODIS_import.MODIS_download_all import download_MODIS
from MODIS_import.MODIS_full_nc_creation import full_nc_creation

##################################################################################
##################################################################################

def download_conversion_nc(config_toml_path):
    """Downloads MODIS data and converts csv results files into a strandard netCDF4 file automatic.

    Parameters
    ----------
    config_toml_path: str
        path to the TOML configuration file

    Returns
    -------
    netCDF4 file
    """

    download_MODIS(config_toml_path)
    full_nc_creation(config_toml_path)