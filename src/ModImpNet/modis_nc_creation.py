"""This module takes the csv result files from MODIS and converts them to netCDF4"""

from datetime import datetime, timezone
import pandas as pd
from netCDF4 import date2num,Dataset #pylint: disable=no-name-in-module
import numpy as np

##################################################################################
##################################################################################


def extract_info_config_csv(config_csv_path):
    """From the csv configuration file, returns a list of station IDs,
    latitudes, and longitudes.

    Parameters
    ----------
    config_csv_path: str
        Path to the csv configuration file with header
        id,latitude,longitude

    Returns
    -------
    list_id: list
    list_lat: list   
    list_lon: list
    """

    df = pd.read_csv(config_csv_path)

    list_id = list(df['id'])
    list_lat = list(df['latitude'])
    list_lon = list(df['longitude'])

    return list_id, list_lat, list_lon

def result_csvs_to_dict_product_id(list_paths_csv_results, list_id):
    """From the two csv files wher the MODIS results are stored
    (MOD10A1.061->(snow cover) and MOD11A1.061->LST), creates 
    a dictionary with 2 levels: product ('snow' or 'LST')
    and station_ID.

    Parameters
    ----------
    list_paths_csv_results: list
        list of paths to the 2 csv result files for 
        MOD10A1.061->(snow cover) and MOD11A1.061->LST
    list_id: list
        list of station IDs returned by extract_info_config_csv()

    Returns
    -------
    df_dict: dict
        dictionary with 2 levels: product ('snow' or 'LST')
        and station_ID
    """

    df_dict_pre = {'snow': pd.read_csv(list_paths_csv_results[0]),
                   'LST': pd.read_csv(list_paths_csv_results[1])}

    df_dict = {'snow': {id: df_dict_pre['snow'][df_dict_pre['snow']['ID']==id].reset_index()
                        for id in list_id},
               'LST': {id: df_dict_pre['LST'][df_dict_pre['LST']['ID']==id].reset_index()
                       for id in list_id}}

    return df_dict

def create_nc(nc_path):
    """Creates a new netCDF4 file at the selected location.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored

    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try:
        ncfile.close()  #pylint: disable=used-before-assignment
    except: #pylint: disable=bare-except
        pass
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    ncfile.Conventions = 'CF-1.6'
    ncfile.featureType = 'timeSeries'
    ncfile.date_created = datetime.now(timezone.utc).isoformat()
    ncfile.source = 'MODIS/Terra Snow Cover Daily L3 Global 500m SIN Grid, Version 61 \n Data set id: MOD10A1.061 \n DOI: 10.5067/MODIS/MOD10A1.061 \n Layer: NDSI_Snow_Cover \n AND \n MODIS/Terra Land Surface Temperature/Emissivity Daily L3 Global 1 km SIN Grid, Version 61 \n Data set id: MOD11A1.061 \n DOI: 10.5067/MODIS/MOD11A1.061  \n Layers: LST_Day_1km, LST_Night_1km, Clear_day_cov, Clear_night_cov'

    ncfile.close()

def add_dims_nc(nc_path, list_id):
    """Adds dimensions to the netCDF4 file.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored
    list_id: list
        list of station IDs returned by extract_info_config_csv()

    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try:
        ncfile.close()  #pylint: disable=used-before-assignment
    except: #pylint: disable=bare-except
        pass
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    ncfile.createDimension('nchars', 32)
    ncfile.createDimension('pointID', len(list_id))
    ncfile.createDimension('time', None) # unlimited axis (can be appended to).

    ncfile.close()

def add_var_date(nc_path, df_dict):
    """Adds 'Date' variable to the netCDF4 file.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored
    df_dict: dict
        dictionary with 2 levels: product ('snow' or 'LST')
        and station_ID

    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try:
        ncfile.close()  #pylint: disable=used-before-assignment
    except: #pylint: disable=bare-except
        pass
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    var = ncfile.createVariable('Date', np.float64, ('time',))
    var.units = 'days since 1800-1-1'
    var.calendar = 'standard'
    var.standard_name = 'time'
    var.axis = 'T'

    df = df_dict['snow'][list(df_dict['snow'].keys())[0]]
    list_dates = list(df['Date'])

    dates = [datetime(*[int(i) for i in d.split('-')]) for d in list_dates]
    times = date2num(dates, var.units)
    var[:] = times

    ncfile.close()

def add_var_point_id(nc_path, list_id):
    """Adds 'pointID' variable to the netCDF4 file.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored
    list_id: list
        list of station IDs returned by extract_info_config_csv()

    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try:
        ncfile.close()  #pylint: disable=used-before-assignment
    except: #pylint: disable=bare-except
        pass
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    var = ncfile.createVariable('pointID', '|S1', ('pointID','nchars'))

    list_point_id = np.array([list([''] * 32)] * 2)
    for idx,i in enumerate(list_id):
        list_point_id[idx,:len(i)] = list(i)
    var[:,:] = list_point_id

    ncfile.close()

def add_var_latitude(nc_path, list_lat):
    """Adds 'latitude' variable to the netCDF4 file.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored
    list_lat: list
        list of latitudes returned by extract_info_config_csv()

    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try:
        ncfile.close()  #pylint: disable=used-before-assignment
    except: #pylint: disable=bare-except
        pass
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    var = ncfile.createVariable('latitude', np.float64, ('pointID',))
    var.long_name = 'latitude'
    var.units = 'degrees_north'
    var.standard_name = 'latitude'
    var.axis = 'Y'

    var[:] = list_lat

    ncfile.close()

def add_var_longitude(nc_path, list_lon):
    """Adds 'longitude' variable to the netCDF4 file.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored
    list_lon: list
        list of longitude returned by extract_info_config_csv()

    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try:
        ncfile.close()  #pylint: disable=used-before-assignment
    except: #pylint: disable=bare-except
        pass
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    var = ncfile.createVariable('longitude', np.float64, ('pointID',))
    var.long_name = 'longitude'
    var.units = 'degrees_east'
    var.standard_name = 'longitude'
    var.axis = 'X'

    var[:] = list_lon

    ncfile.close()

def add_var_modis_tile(nc_path, df_dict):
    """Adds 'MODIS_Tile' variable to the netCDF4 file.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored
    df_dict: dict
        dictionary with 2 levels: product ('snow' or 'LST')
        and station_ID


    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try:
        ncfile.close()  #pylint: disable=used-before-assignment
    except: #pylint: disable=bare-except
        pass
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    var = ncfile.createVariable('MODIS_Tile', '|S1', ('pointID','nchars'), fill_value= '')
    var.long_name = 'MODIS_Tile'
    var.standard_name = 'MODIS_Tile'

    df_list = df_dict['snow']

    list_tile = np.array([list([''] * 32)] * 2)
    for indx,id_station in enumerate(list(df_list.keys())):
        list_tile[indx,:len(df_list[id_station].loc[0,'MODIS_Tile'])] = list(df_list[id_station].loc[0,'MODIS_Tile'])
    var[:] = list_tile

    ncfile.close()

def add_var_ndsi_snow_cover(nc_path, df_dict):
    """Adds 'NDSI_Snow_Cover' variable to the netCDF4 file.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored
    df_dict: dict
        dictionary with 2 levels: product ('snow' or 'LST')
        and station_ID


    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try:
        ncfile.close()  #pylint: disable=used-before-assignment
    except: #pylint: disable=bare-except
        pass
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    var = ncfile.createVariable('NDSI_Snow_Cover', np.float64, ('pointID', 'time'))
    var.long_name = 'Snow-covered land typically has very high reflectance in visible bands and very low reflectance in shortwave infrared bands. The Normalized Difference Snow Index (NDSI) reveals the magnitude of this difference. The snow cover algorithm calculates NDSI for all land and inland water pixels in daylight using Terra MODIS band 4 (visible green) and band 6 (shortwave near-infrared).'
    var.units = '%, normalized between 0 and 100'
    var.comments = '0-100 NDSI snow cover, all flags are treated as NaN'

    var[:,:] = [[(j if j<=100 else np.nan) for j in i.loc[:,'MOD10A1_061_NDSI_Snow_Cover']] for i in df_dict['snow'].values()]

    ncfile.close()

def add_var_ndsi_snow_cover_original_with_code_for_missing_data(nc_path, df_dict):
    """Adds 'NDSI_Snow_Cover_original_with_code_for_missing_data' variable to the netCDF4 file.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored
    df_dict: dict
        dictionary with 2 levels: product ('snow' or 'LST')
        and station_ID


    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try:
        ncfile.close()  #pylint: disable=used-before-assignment
    except: #pylint: disable=bare-except
        pass
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    var = ncfile.createVariable('NDSI_Snow_Cover_original_with_code_for_missing_data', np.int32, ('pointID', 'time'))
    var.long_name = 'Snow-covered land typically has very high reflectance in visible bands and very low reflectance in shortwave infrared bands. The Normalized Difference Snow Index (NDSI) reveals the magnitude of this difference. The snow cover algorithm calculates NDSI for all land and inland water pixels in daylight using Terra MODIS band 4 (visible green) and band 6 (shortwave near-infrared).'
    var.units = '%, normalized between 0 and 100'
    var.comments = '0-100 NDSI snow cover, 200: missing data, 201: no decision, 211: night, 237: inland water, 239: ocean, 250: cloud, 254: detector saturated, 255: fill '

    var[:,:] = [i.loc[:,'MOD10A1_061_NDSI_Snow_Cover'] for i in df_dict['snow'].values()]

    ncfile.close()

def add_var_lst_day(nc_path, df_dict):
    """Adds 'LST_Day' variable to the netCDF4 file.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored
    df_dict: dict
        dictionary with 2 levels: product ('snow' or 'LST')
        and station_ID


    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try:
        ncfile.close()  #pylint: disable=used-before-assignment
    except: #pylint: disable=bare-except
        pass
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    var = ncfile.createVariable('LST_Day', np.float64, ('pointID', 'time'))
    var.long_name = 'Day Land Surface Temperature'
    var.units = 'C'
    var.comments = 'Any data that was originally lower than 150K~= -123.15C is set to 0 by MODIS, and to NaN by me'

    var[:,:] = [[(j-273.15 if j>=150 else np.nan) for j in i.loc[:,'MOD11A1_061_LST_Day_1km']] for i in df_dict['LST'].values()]

    ncfile.close()

def add_var_lst_night(nc_path, df_dict):
    """Adds 'LST_Night' variable to the netCDF4 file.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored
    df_dict: dict
        dictionary with 2 levels: product ('snow' or 'LST')
        and station_ID


    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try:
        ncfile.close()  #pylint: disable=used-before-assignment
    except: #pylint: disable=bare-except
        pass
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    var = ncfile.createVariable('LST_Night', np.float64, ('pointID', 'time'))
    var.long_name = 'Night Land Surface Temperature'
    var.units = 'C'
    var.comments = 'Any data that was originally lower than 150K~= -123.15C is set to 0 by MODIS, and to NaN by me'

    var[:,:] = [[(j-273.15 if j>=150 else np.nan) for j in i.loc[:,'MOD11A1_061_LST_Night_1km']] for i in df_dict['LST'].values()]

    ncfile.close()

def add_var_clear_day_cov(nc_path, df_dict):
    """Adds 'Clear_day_cov' variable to the netCDF4 file.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored
    df_dict: dict
        dictionary with 2 levels: product ('snow' or 'LST')
        and station_ID


    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try:
        ncfile.close()  #pylint: disable=used-before-assignment
    except: #pylint: disable=bare-except
        pass
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    var = ncfile.createVariable('Clear_day_cov', np.float64, ('pointID', 'time'))
    var.long_name = 'Day clear-sky coverage'
    var.units = '%'
    var.comments = 'I believe the units are fractions, but values sometimes exceed 1. LST is computed if >0.0005000000237. Max is apparently 32.76750183.'

    var[:,:] = [i.loc[:,'MOD11A1_061_Clear_day_cov'] for i in df_dict['LST'].values()]

    ncfile.close()

def add_var_clear_night_cov(nc_path, df_dict):
    """Adds 'Clear_night_cov' variable to the netCDF4 file.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored
    df_dict: dict
        dictionary with 2 levels: product ('snow' or 'LST')
        and station_ID


    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try:
        ncfile.close()  #pylint: disable=used-before-assignment
    except: #pylint: disable=bare-except
        pass
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    var = ncfile.createVariable('Clear_night_cov', np.float64, ('pointID', 'time'))
    var.long_name = 'Night clear-sky coverage'
    var.units = '%'
    var.comments = 'I believe the units are fractions, but values sometimes exceed 1. LST is computed if >0.0005000000237. Max is apparently 32.76750183.'

    var[:,:] = [i.loc[:,'MOD11A1_061_Clear_night_cov'] for i in df_dict['LST'].values()]

    ncfile.close()
