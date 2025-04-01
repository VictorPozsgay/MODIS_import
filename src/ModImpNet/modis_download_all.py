"""This module makes the MODIS download automatic"""

from datetime import datetime
import os
import toml

from ModImpNet.modis_requests import get_credential_modis, create_log, write_product_metadata, request_token, create_task_json, submit_task, check_if_status_done, download_bundle, write_csv_files_local, delete_task, log_out


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

    task_name = config['name']['task_name']

    dest_dir = config['directories']['dest_dir']
    credential_dir = config['directories']['credential_dir']
    config_csv_path = config['directories']['config_csv_path']

    max_wait = config['download']['max_wait']
    time_sleep = config['download']['time_sleep']

    # Dates are stored in format '%Y/%m/%d' but we need '%m-%d-%Y' for download
    # silly Americans...
    start_date = datetime.strptime(config['config']['startDate'], '%Y/%m/%d').strftime('%m-%d-%Y')
    end_date = datetime.strptime(config['config']['endDate'], '%Y/%m/%d').strftime('%m-%d-%Y')

    list_product_id = ['MOD10A1.061', 'MOD11A1.061']
    os.makedirs(dest_dir, exist_ok=True)
    logfilepath = create_log(dest_dir)
    for product_id in list_product_id:
        write_product_metadata(logfilepath, product_id)
    username, pwd = get_credential_modis(credential_dir)
    token = request_token(username, pwd, logfilepath)

    if isinstance(token, int):
        list_paths_csv_results=[]
    else:
        task = create_task_json(config_csv_path, task_name, start_date, end_date, logfilepath)
        task_id = submit_task(task, token, logfilepath)

        if isinstance(task_id, int):
            list_paths_csv_results=[]
        else:
            check_if_status_done(task_id, token, logfilepath, max_wait, time_sleep)
            # here we should retrieve two csv results files
            # we get a dict in the form
            # {'MOD10A1.061': '<file_id0>',
            #  'MOD11A1.061': '<file_id1>'}
            dic_files_results = download_bundle(task_id, token, list_product_id, logfilepath)
            args = [dest_dir, dic_files_results, task_id, task_name, token, logfilepath]
            list_paths_csv_results = write_csv_files_local(*args)
            delete_task(task_id, token, logfilepath)

        log_out(token, logfilepath)

    return list_paths_csv_results
