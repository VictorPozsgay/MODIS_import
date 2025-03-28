"""This module makes the MODIS download automatic"""

from datetime import datetime
import os
import toml

from MODIS_requests import get_credential_MODIS, create_log, write_product_metadata, request_token, create_task_json, submit_task, check_if_status_done, download_bundle, write_csv_files_local, delete_task, log_out


##################################################################################
##################################################################################

def download_MODIS(config_toml_path, max_wait=86400, time_sleep=30):
    """Downloads the MODIS results in csv form, saves them to a directory, and writes a text log.

    Parameters
    ----------
    config_toml_path: str
                      path to the TOML configuration file
    max_wait: int
              maximum amount of waiting time in second, default 86400s=1day
    time_sleep: int
                time between two status checks in second, default 30s

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

    # Dates are stored in format '%Y/%m/%d' but we need '%m-%d-%Y' for download
    # silly Americans...
    startDate = datetime.strptime(config['config']['startDate'], '%Y/%m/%d').strftime('%m-%d-%Y')
    endDate = datetime.strptime(config['config']['endDate'], '%Y/%m/%d').strftime('%m-%d-%Y')

    list_product_id = ['MOD10A1.061', 'MOD11A1.061']
    os.makedirs(dest_dir, exist_ok=True)
    logfilepath = create_log(dest_dir)
    for product_id in list_product_id:
        write_product_metadata(logfilepath, product_id)
    username, pwd = get_credential_MODIS(credential_dir)
    token = request_token(username, pwd, logfilepath)

    if type(token)==int:
        list_paths_csv_results=[]
    else:
        task = create_task_json(config_csv_path, task_name, startDate, endDate, logfilepath)
        task_id = submit_task(task, token, logfilepath)

        if type(task_id)==int:
            list_paths_csv_results=[]
        else:
            check_if_status_done(task_id, token, logfilepath, max_wait, time_sleep)
            # here we should retrieve two csv results files
            # we get a dict in the form
            # {'MOD10A1.061': '<file_id0>',
            #  'MOD11A1.061': '<file_id1>'}
            dic_files_results = download_bundle(task_id, token, list_product_id, logfilepath)
            list_paths_csv_results = write_csv_files_local(dest_dir, dic_files_results, task_id, task_name, token, logfilepath)
            delete_task(task_id, token, logfilepath)

        log_out(token, logfilepath)

    return list_paths_csv_results