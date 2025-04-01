"""This module makes the MODIS download automatic"""

from datetime import datetime
import os
import toml

from ModImpNetTest.modis_requests import create_log


##################################################################################
##################################################################################

def download_modis(config_toml_path):
    """Downloads the MODIS results in csv form, saves them to a directory, and writes a text log.

    Parameters
    ----------
    config_toml_path: str
        path to the TOML configuration file

    Returns
    -------
    .csv files with MODIS data
    .txt log file
    """

    with open(config_toml_path, 'r', encoding="utf-8") as f:
        config = toml.load(f)

    dest_dir = config['directories']['dest_dir']
    os.makedirs(dest_dir, exist_ok=True)
    create_log(dest_dir)
