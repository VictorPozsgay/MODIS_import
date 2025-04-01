"""This module makes the MODIS csv results files conversion into a strandard
netCDF4 file automatic."""

import os
import toml

from ModImpNet.modis_nc_creation import extract_info_config_csv, result_csvs_to_dict_product_id, create_nc, add_dims_nc, add_var_date, add_var_point_id, add_var_latitude, add_var_longitude, add_var_modis_tile, add_var_ndsi_snow_cover, add_var_ndsi_snow_cover_original_with_code_for_missing_data, add_var_lst_day, add_var_lst_night, add_var_clear_day_cov, add_var_clear_night_cov

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
    list_product_id = ['MOD10A1.061', 'MOD11A1.061']

    for product_id in list_product_id:
        # get a stream to the bundle file
        filename = f'{task_name}_{product_id.replace(".","_")}_results.csv'
        filepath = os.path.join(dest_dir, filename)
        list_paths_csv_results.append(filepath)

    try:
        os.remove(nc_path)
    except OSError:
        pass

    list_id, list_lat, list_lon = extract_info_config_csv(config_csv_path)
    df_dict = result_csvs_to_dict_product_id(list_paths_csv_results, list_id)
    create_nc(nc_path)
    add_dims_nc(nc_path, list_id)
    add_var_date(nc_path, df_dict)
    add_var_point_id(nc_path, list_id)
    add_var_latitude(nc_path, list_lat)
    add_var_longitude(nc_path, list_lon)
    add_var_modis_tile(nc_path, df_dict)
    add_var_ndsi_snow_cover(nc_path, df_dict)
    add_var_ndsi_snow_cover_original_with_code_for_missing_data(nc_path, df_dict)
    add_var_lst_day(nc_path, df_dict)
    add_var_lst_night(nc_path, df_dict)
    add_var_clear_day_cov(nc_path, df_dict)
    add_var_clear_night_cov(nc_path, df_dict)
