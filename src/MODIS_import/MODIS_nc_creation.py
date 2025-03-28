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
    list_ID: list
    list_lat: list   
    list_lon: list
    """

    df = pd.read_csv(config_csv_path)

    list_ID = list(df['id'])
    list_lat = list(df['latitude'])
    list_lon = list(df['longitude'])

    return list_ID, list_lat, list_lon

def result_csvs_to_dict_product_ID(list_paths_csv_results, list_ID):
    """From the two csv files wher the MODIS results are stored
    (MOD10A1.061->(snow cover) and MOD11A1.061->LST), creates 
    a dictionary with 2 levels: product ('snow' or 'LST')
    and station_ID.

    Parameters
    ----------
    list_paths_csv_results: list
        list of paths to the 2 csv result files for 
        MOD10A1.061->(snow cover) and MOD11A1.061->LST
    list_ID: list
        list of station IDs returned by extract_info_config_csv()

    Returns
    -------
    df_dict: dict
        dictionary with 2 levels: product ('snow' or 'LST')
        and station_ID
    """

    df_dict_pre = {'snow': pd.read_csv(list_paths_csv_results[0]),
                'LST': pd.read_csv(list_paths_csv_results[1])}

    df_dict = {'snow': {id: df_dict_pre['snow'][df_dict_pre['snow']['ID']==id].reset_index() for id in list_ID},
            'LST': {id: df_dict_pre['LST'][df_dict_pre['LST']['ID']==id].reset_index() for id in list_ID}}
    
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
    try: ncfile.close()  #pylint: disable=used-before-assignment
    except: pass #pylint: disable=bare-except
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    ncfile.Conventions = 'CF-1.6'
    ncfile.featureType = 'timeSeries'
    ncfile.date_created = datetime.now(timezone.utc).isoformat()
    ncfile.source = 'MODIS/Terra Snow Cover Daily L3 Global 500m SIN Grid, Version 61 \n Data set id: MOD10A1.061 \n DOI: 10.5067/MODIS/MOD10A1.061 \n Layer: NDSI_Snow_Cover \n AND \n MODIS/Terra Land Surface Temperature/Emissivity Daily L3 Global 1 km SIN Grid, Version 61 \n Data set id: MOD11A1.061 \n DOI: 10.5067/MODIS/MOD11A1.061  \n Layers: LST_Day_1km, LST_Night_1km, Clear_day_cov, Clear_night_cov'

    ncfile.close()

def add_dims_nc(nc_path, list_ID):
    """Adds dimensions to the netCDF4 file.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored
    list_ID: list
        list of station IDs returned by extract_info_config_csv()

    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try: ncfile.close()  #pylint: disable=used-before-assignment
    except: pass #pylint: disable=bare-except
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    ncfile.createDimension('nchars', 32)
    ncfile.createDimension('pointID', len(list_ID))
    ncfile.createDimension('time', None) # unlimited axis (can be appended to).

    ncfile.close()

def add_var_Date(nc_path, df_dict):
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
    try: ncfile.close()  #pylint: disable=used-before-assignment
    except: pass #pylint: disable=bare-except
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    Date = ncfile.createVariable('Date', np.float64, ('time',))
    Date.units = 'days since 1800-1-1'
    Date.calendar = 'standard'
    Date.standard_name = 'time'
    Date.axis = 'T'

    df = df_dict['snow'][list(df_dict['snow'].keys())[0]]
    list_dates = list(df['Date'])

    dates = [datetime(*[int(i) for i in d.split('-')]) for d in list_dates]
    times = date2num(dates, Date.units)
    Date[:] = times

    ncfile.close()

def add_var_pointID(nc_path, list_ID):
    """Adds 'pointID' variable to the netCDF4 file.

    Parameters
    ----------
    nc_path: str
        path where the netCDF4 file is stored
    list_ID: list
        list of station IDs returned by extract_info_config_csv()

    Returns
    -------
    ncfile: netCDF4 file
    """

    # just to be safe, make sure dataset is not already open.
    try: ncfile.close()  #pylint: disable=used-before-assignment
    except: pass #pylint: disable=bare-except
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4')

    ##################################################################################

    pointID = ncfile.createVariable('pointID', '|S1', ('pointID','nchars'))

    list_pointID = np.array([list([''] * 32)] * 2)
    for idx,i in enumerate(list_ID):
        list_pointID[idx,:len(i)] = list(i)
    pointID[:,:] = list_pointID

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
    try: ncfile.close()  #pylint: disable=used-before-assignment
    except: pass #pylint: disable=bare-except
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4') 

    ##################################################################################

    latitude = ncfile.createVariable('latitude', np.float64, ('pointID',))
    latitude.long_name = 'latitude'
    latitude.units = 'degrees_north'
    latitude.standard_name = 'latitude'
    latitude.axis = 'Y'

    latitude[:] = list_lat

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
    try: ncfile.close()  #pylint: disable=used-before-assignment
    except: pass #pylint: disable=bare-except
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4') 

    ##################################################################################

    longitude = ncfile.createVariable('longitude', np.float64, ('pointID',))
    longitude.long_name = 'longitude'
    longitude.units = 'degrees_east'
    longitude.standard_name = 'longitude'
    longitude.axis = 'X'

    longitude[:] = list_lon

    ncfile.close()

def add_var_MODIS_Tile(nc_path, df_dict):
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
    try: ncfile.close()  #pylint: disable=used-before-assignment
    except: pass #pylint: disable=bare-except
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4') 

    ##################################################################################

    MODIS_Tile = ncfile.createVariable('MODIS_Tile', '|S1', ('pointID','nchars'), fill_value= '')
    MODIS_Tile.long_name = 'MODIS_Tile'
    MODIS_Tile.standard_name = 'MODIS_Tile'

    df_list = df_dict['snow']

    list_tile = np.array([list([''] * 32)] * 2)
    for indx,id_station in enumerate(list(df_list.keys())):
        list_tile[indx,:len(df_list[id_station].loc[0,'MODIS_Tile'])] = list(df_list[id_station].loc[0,'MODIS_Tile'])
    MODIS_Tile[:] = list_tile

    ncfile.close()

def add_var_NDSI_Snow_Cover(nc_path, df_dict):
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
    try: ncfile.close()  #pylint: disable=used-before-assignment
    except: pass #pylint: disable=bare-except
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4') 

    ##################################################################################

    NDSI_Snow_Cover = ncfile.createVariable('NDSI_Snow_Cover', np.float64, ('pointID', 'time'))
    NDSI_Snow_Cover.long_name = 'Snow-covered land typically has very high reflectance in visible bands and very low reflectance in shortwave infrared bands. The Normalized Difference Snow Index (NDSI) reveals the magnitude of this difference. The snow cover algorithm calculates NDSI for all land and inland water pixels in daylight using Terra MODIS band 4 (visible green) and band 6 (shortwave near-infrared).'
    NDSI_Snow_Cover.units = '%, normalized between 0 and 100'
    NDSI_Snow_Cover.comments = '0-100 NDSI snow cover, all flags are treated as NaN'

    NDSI_Snow_Cover[:,:] = [[(j if j<=100 else np.nan) for j in i.loc[:,'MOD10A1_061_NDSI_Snow_Cover']] for i in df_dict['snow'].values()]

    ncfile.close()

def add_var_NDSI_Snow_Cover_original_with_code_for_missing_data(nc_path, df_dict):
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
    try: ncfile.close()  #pylint: disable=used-before-assignment
    except: pass #pylint: disable=bare-except
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4') 

    ##################################################################################

    NDSI_Snow_Cover_original_with_code_for_missing_data = ncfile.createVariable('NDSI_Snow_Cover_original_with_code_for_missing_data', np.int32, ('pointID', 'time'))
    NDSI_Snow_Cover_original_with_code_for_missing_data.long_name = 'Snow-covered land typically has very high reflectance in visible bands and very low reflectance in shortwave infrared bands. The Normalized Difference Snow Index (NDSI) reveals the magnitude of this difference. The snow cover algorithm calculates NDSI for all land and inland water pixels in daylight using Terra MODIS band 4 (visible green) and band 6 (shortwave near-infrared).'
    NDSI_Snow_Cover_original_with_code_for_missing_data.units = '%, normalized between 0 and 100'
    NDSI_Snow_Cover_original_with_code_for_missing_data.comments = '0-100 NDSI snow cover, 200: missing data, 201: no decision, 211: night, 237: inland water, 239: ocean, 250: cloud, 254: detector saturated, 255: fill '

    NDSI_Snow_Cover_original_with_code_for_missing_data[:,:] = [i.loc[:,'MOD10A1_061_NDSI_Snow_Cover'] for i in df_dict['snow'].values()]

    ncfile.close()

def add_var_LST_Day(nc_path, df_dict):
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
    try: ncfile.close()  #pylint: disable=used-before-assignment
    except: pass #pylint: disable=bare-except
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4') 

    ##################################################################################

    LST_Day = ncfile.createVariable('LST_Day', np.float64, ('pointID', 'time'))
    LST_Day.long_name = 'Day Land Surface Temperature'
    LST_Day.units = 'C'
    LST_Day.comments = 'Any data that was originally lower than 150K~= -123.15C is set to 0 by MODIS, and to NaN by me'

    LST_Day[:,:] = [[(j-273.15 if j>=150 else np.nan) for j in i.loc[:,'MOD11A1_061_LST_Day_1km']] for i in df_dict['LST'].values()]

    ncfile.close()

def add_var_LST_Night(nc_path, df_dict):
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
    try: ncfile.close()  #pylint: disable=used-before-assignment
    except: pass #pylint: disable=bare-except
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4') 

    ##################################################################################

    LST_Night = ncfile.createVariable('LST_Night', np.float64, ('pointID', 'time'))
    LST_Night.long_name = 'Night Land Surface Temperature'
    LST_Night.units = 'C'
    LST_Night.comments = 'Any data that was originally lower than 150K~= -123.15C is set to 0 by MODIS, and to NaN by me'

    LST_Night[:,:] = [[(j-273.15 if j>=150 else np.nan) for j in i.loc[:,'MOD11A1_061_LST_Night_1km']] for i in df_dict['LST'].values()]

    ncfile.close()

def add_var_Clear_day_cov(nc_path, df_dict):
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
    try: ncfile.close()  #pylint: disable=used-before-assignment
    except: pass #pylint: disable=bare-except
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4') 

    ##################################################################################

    Clear_day_cov = ncfile.createVariable('Clear_day_cov', np.float64, ('pointID', 'time'))
    Clear_day_cov.long_name = 'Day clear-sky coverage'
    Clear_day_cov.units = '%'
    Clear_day_cov.comments = 'I believe the units are fractions, but values sometimes exceed 1. LST is computed if >0.0005000000237. Max is apparently 32.76750183.'

    Clear_day_cov[:,:] = [i.loc[:,'MOD11A1_061_Clear_day_cov'] for i in df_dict['LST'].values()]

    ncfile.close()

def add_var_Clear_night_cov(nc_path, df_dict):
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
    try: ncfile.close()  #pylint: disable=used-before-assignment
    except: pass #pylint: disable=bare-except
    ncfile = Dataset(nc_path,mode='a',format='NETCDF4') 

    ##################################################################################

    Clear_night_cov = ncfile.createVariable('Clear_night_cov', np.float64, ('pointID', 'time'))
    Clear_night_cov.long_name = 'Night clear-sky coverage'
    Clear_night_cov.units = '%'
    Clear_night_cov.comments = 'I believe the units are fractions, but values sometimes exceed 1. LST is computed if >0.0005000000237. Max is apparently 32.76750183.'

    Clear_night_cov[:,:] = [i.loc[:,'MOD11A1_061_Clear_night_cov'] for i in df_dict['LST'].values()]

    ncfile.close()