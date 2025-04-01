"""This module downloads the MODIS data and converts it to
netCDF4 file automatically."""


from ModImpNetTest.modis_download_all import download_modis

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

    download_modis(config_toml_path)
