"""This module makes the MODIS csv results files conversion into a strandard
netCDF4 file automatic."""

import os
import toml

from MODIS_import.MODIS_nc_creation import extract_info_config_csv, result_csvs_to_dict_product_ID, create_nc, add_dims_nc, add_var_Date, add_var_pointID, add_var_latitude, add_var_longitude, add_var_MODIS_Tile, add_var_NDSI_Snow_Cover, add_var_NDSI_Snow_Cover_original_with_code_for_missing_data, add_var_LST_Day, add_var_LST_Night, add_var_Clear_day_cov, add_var_Clear_night_cov

##################################################################################
##################################################################################

def full_nc_creation(config_toml_path):
    """Converts MODIS csv results files into a strandard netCDF4 file automatic.

    Parameters
    ----------
    config_toml_path: str
        path to the TOML configuration file

    Returns
    -------
    netCDF4 file
    """

    with open(config_toml_path, 'r', encoding="utf-8") as f:
        config = toml.load(f)

    task_name = config['name']['task_name']

    dest_dir = config['directories']['dest_dir']
    config_csv_path = config['directories']['config_csv_path']
    filename = f'{task_name}_snow_cover_LST_results.nc'
    nc_path = os.path.join(dest_dir, filename)

    list_paths_csv_results = []
    list_product_ID = ['MOD10A1.061', 'MOD11A1.061']

    for product_id in list_product_ID:
        # get a stream to the bundle file
        filename = f'{task_name}_{product_id.replace('.','_')}_results.csv'
        filepath = os.path.join(dest_dir, filename)
        list_paths_csv_results.append(filepath)

    try:
        os.remove(nc_path)
    except OSError:
        pass

    list_ID, list_lat, list_lon = extract_info_config_csv(config_csv_path)
    df_dict = result_csvs_to_dict_product_ID(list_paths_csv_results, list_ID)
    create_nc(nc_path)
    add_dims_nc(nc_path, list_ID)
    add_var_Date(nc_path, df_dict)
    add_var_pointID(nc_path, list_ID)
    add_var_latitude(nc_path, list_lat)
    add_var_longitude(nc_path, list_lon)
    add_var_MODIS_Tile(nc_path, df_dict)
    add_var_NDSI_Snow_Cover(nc_path, df_dict)
    add_var_NDSI_Snow_Cover_original_with_code_for_missing_data(nc_path, df_dict)
    add_var_LST_Day(nc_path, df_dict)
    add_var_LST_Night(nc_path, df_dict)
    add_var_Clear_day_cov(nc_path, df_dict)
    add_var_Clear_night_cov(nc_path, df_dict)
