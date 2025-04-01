"""This module has functions that allow for authentication, task submission, download"""

import time
from datetime import datetime
import os
import requests
import pandas as pd

##################################################################################
##################################################################################


def get_credential_modis(credential_dir):
    """Returns login and password from credential file for MODIS.

    Parameters
    ----------
    credential_dir: str
        A directory that holds the login and password
        information, in the form
        'machine urs.earthdata.nasa.gov login <login>
        password <password>'
        with a space between each field

    Returns
    -------
    username: str
    pwd: str        
    """

    username = ''
    pwd = ''

    f=open(os.path.join(credential_dir, '.netrc'),'r', encoding="utf-8")
    lines=f.readlines()
    for l in lines:
        # skip commented lines
        if l[0]=='#':
            pass
        else:
            lvec=l.split(' ')
            username=[lvec[i+1] for i in range(len(lvec)) if lvec[i]=='login'][0]
            pwd=[lvec[i+1] for i in range(len(lvec)) if lvec[i]=='password'][0]
    f.close()

    return username, pwd

def create_log(dest_dir):
    """Creates a .txt log for MODIS task request submission and download.

    Parameters
    ----------
    dest_dir: str
        A directory that where the log file will be created.

    Returns
    -------
    logfilepath: str
        path to the log file
    """
    datetime_now = datetime.now().strftime('%Y%m%d%H%M%S')
    logfile = f'MODIS_log_{datetime_now}.txt'
    logfilepath = os.path.join(dest_dir, logfile)

    with open(logfilepath,'a+', encoding="utf-8") as _:
        pass

    return logfilepath

def write_product_metadata(logfilepath, product_id):
    """Writes product (MODIS) metadata to .txt log file.

    Parameters
    ----------
    logfilepath: str
        path to the log file
    product_id: str
    """

    params = {'pretty': True}
    response = requests.get(
        f'https://appeears.earthdatacloud.nasa.gov/api/product/{product_id}',
        params=params, timeout=86400)
    dataset_metadata = response.text

    with open(logfilepath,'a+', encoding="utf-8") as f:
        f.write('Log file for MODIS download\n \n')
        f.write('#' * 80 + '\n')
        f.write('#' * 80 + '\n')
        f.write('\n \n')
        f.write(f'Information about the MODIS product with product_id={product_id}: \n \n')
        f.write(dataset_metadata)
        f.write('\n \n')

def request_token(username, pwd, logfilepath):
    """Requests a token from the server.

    Parameters
    ----------
    username: str
    pwd: str
    logfilepath: str
        path to the log file

    Returns
    -------
    token: str
    """

    response = requests.post('https://appeears.earthdatacloud.nasa.gov/api/login',
                             auth=(username, pwd),
                             timeout=86400)

    with open(logfilepath,'a+', encoding="utf-8") as f:
        f.write('#' * 80 + '\n')
        f.write('#' * 80 + '\n')
        f.write('\n \n')
        f.write('Full response to token request: \n')
        f.write('\n \n')
        f.write(response.text)
        f.write('\n \n')

    if response.status_code == 200:
        token_response = response.json()
        token = token_response['token']
        with open(logfilepath,'a+', encoding="utf-8") as f:
            f.write('The token has been succesfully requested and retrieved. \n')
            f.write(f'The token is: {token} \n')
            f.write('\n \n')\

        print('Token retrieved successfully.')
        return token

    elif response.status_code == 504:
        with open(logfilepath,'a+', encoding="utf-8") as f:
            f.write('Timeout Error 504 (probably on the server\'s side) \n')
            f.write('\n \n')

        print('Timeout Error 504 (probably on the server\'s side) when retrieving token.')
        return response.status_code

    else:
        with open(logfilepath,'a+', encoding="utf-8") as f:
            f.write(f'Some other error with status_code: {response.status_code} \n')
            f.write('\n \n')

        print(f'Error {response.status_code} when retrieving token.')
        return response.status_code

def create_task_json(config_csv_path, task_name, start_date, end_date, logfilepath):
    """Submits the task.

    Parameters
    ----------
    config_csv_path: str
        path to the csv configuration file
    task_name:str
    start_date: str
        format 'DD-MM-YYYY'
    end_date: str
        format 'DD-MM-YYYY'
    logfilepath: str
        path to the log file

    Returns
    -------
    task: dict
    """

    df_config = pd.read_csv(config_csv_path)

    # create the task request
    task = {'task_type': 'point',
            'task_name': task_name,
            'params': {
                'dates': [{'startDate': start_date, 'endDate': end_date}],
                'layers': [{'product': 'MOD10A1.061', 'layer': 'NDSI_Snow_Cover'},
                           {'product': 'MOD11A1.061', 'layer': 'LST_Day_1km'},
                           {'product': 'MOD11A1.061', 'layer': 'LST_Night_1km'},
                           {'product': 'MOD11A1.061', 'layer': 'Clear_day_cov'},
                           {'product': 'MOD11A1.061', 'layer': 'Clear_night_cov'}],
                'coordinates': [df_config.loc[i,:].to_dict() for i in range(len(df_config))]
                    }
    }

    with open(logfilepath,'a+', encoding="utf-8") as f:
        f.write('#' * 80 + '\n')
        f.write('#' * 80 + '\n')
        f.write('\n \n')
        f.write('Task dictionary created succesfully:')
        f.write('\n \n')
        f.write(str(task))
        f.write('\n \n')

    return task

def submit_task(task, token, logfilepath):
    """Submits the task.

    Parameters
    ----------
    task: dict
    token: str
    logfilepath: str
        path to the log file

    Returns
    -------
    task_id: str
    """

    # submit the task request
    response = requests.post(
        'https://appeears.earthdatacloud.nasa.gov/api/task', 
        json=task,
        headers={'Authorization': f'Bearer {token}'}, timeout=86400)

    if response.status_code == 202:
        task_request_response = response.json()
        task_id = task_request_response['task_id']

        with open(logfilepath,'a+', encoding="utf-8") as f:
            f.write('#' * 80 + '\n')
            f.write('#' * 80 + '\n')
            f.write('\n \n')
            f.write(f'Task request submitted with task_id: {task_id}')
            f.write('\n \n')
            f.write(f'Full task request response: \n {task_request_response}')
            f.write('\n \n')

        print(f'Task request submitted with task_id: {task_id}')

    else:
        task_id = response.status_code
        with open(logfilepath,'a+', encoding="utf-8") as f:
            f.write('#' * 80 + '\n')
            f.write('#' * 80 + '\n')
            f.write('\n \n')
            f.write(f'FAILED task request submission with task_id: {task_id}')
            f.write('\n \n')

        print('FAILED task request submission')

    return task_id

def status_task(task_id, token, logfilepath):
    """Checks for the status of the task.

    Parameters
    ----------
    task_id: str
    token: str
    logfilepath: str
        path to the log file

    Returns
    -------
    task_status_response: str
    """

    response = requests.get(
        f'https://appeears.earthdatacloud.nasa.gov/api/task/{task_id}',
        headers={'Authorization': f'Bearer {token}'}, timeout=86400
    )
    task_status_response = response.json()['status']

    with open(logfilepath,'a+', encoding="utf-8") as f:
        f.write('#' * 80 + '\n')
        f.write('#' * 80 + '\n')
        f.write('\n \n')
        f.write(f'Task status: {task_status_response}')
        f.write('\n \n')

    print(f'status: {task_status_response}')

    return task_status_response

def check_if_status_done(task_id, token, logfilepath, max_wait, time_sleep):
    """Checks whether the status of the task is 'done'.

    Parameters
    ----------
    task_id: str
    token: str
    logfilepath: str
        path to the log file
    max_wait: int
        maximum amount of waiting time in second, default 86400s=1day
    time_sleep: int
        time between two status checks in second, default 30s
    logfilepath: str
        path to the log file
    """

    start = time.time()

    while time.time()-start<max_wait:
        time.sleep(time_sleep)
        dt = time.time()-start
        task_status_response = status_task(task_id, token, logfilepath)

        if task_status_response=='done':
            with open(logfilepath,'a+', encoding="utf-8") as f:
                f.write('#' * 80 + '\n')
                f.write('#' * 80 + '\n')
                f.write('\n \n')
                f.write('Status: done \n')
                f.write(f'{dt:.2f}s elapsed.')
                f.write('\n \n')
                f.write('Downloading can start')
                f.write('\n \n')

            print('Downloading can start')

            break
        else:
            with open(logfilepath,'a+', encoding="utf-8") as f:
                f.write('#' * 80 + '\n')
                f.write('#' * 80 + '\n')
                f.write('\n \n')
                f.write('Not done yet \n')
                f.write(f'{dt:.2f}s elapsed, next try in {time_sleep}s.')
                f.write('\n \n')

            print(f'{dt:.2f}s elapsed, next try in {time_sleep}s.')

def download_bundle(task_id, token, list_product_id, logfilepath):
    """Downloads the bundle and returns the list of result files to download.

    Parameters
    ----------
    task_id: str
    token: str
    list_product_id: list
    logfilepath: str
        path to the log file

    Returns
    -------
    dic_files_results: dict
    """

    response = requests.get(
        f'https://appeears.earthdatacloud.nasa.gov/api/bundle/{task_id}',
        headers={'Authorization': f'Bearer {token}'}, timeout=86400
    )
    bundle_response = response.json()

    with open(logfilepath,'a+', encoding="utf-8") as f:
        f.write('#' * 80 + '\n')
        f.write('#' * 80 + '\n')
        f.write('\n \n')
        f.write(f'Full bundle response: \n {bundle_response}')
        f.write('\n \n')

    # retrieve list, each entry is a dictionary with 5 fields,
    # including 'file_id', 'file_name', 'file_type'
    list_files_results = [f for f in bundle_response['files'] if 'results' in f['file_name']]
    # get dict in the form
    # {'MOD10A1.061': '<file_id0>',
    #  'MOD11A1.061': '<file_id1>'}
    dic_files_results = {i: [j['file_id']
                             for j in list_files_results if i.split('.')[0] in j['file_name']][0]
                         for i in list_product_id}

    return dic_files_results

def write_csv_files_local(dest_dir, dic_files_results, task_id, task_name, token, logfilepath):
    """Retrives the csv files and writes them locally.

    Parameters
    ----------
    dest_dir: str
        A directory that where the log file will be created.
    dic_files_results: dict
    task_id: str
    task_name: str
    token: str
    logfilepath: str
        path to the log file

    Returns
    -------
    list_paths_csv_results: list
    .csv files
    """

    list_paths_csv_results = []

    for product_id,file_id in dic_files_results.items():
        # get a stream to the bundle file
        filename = f'{task_name}_{product_id.replace(".","_")}_results.csv'
        response = requests.get(
            f'https://appeears.earthdatacloud.nasa.gov/api/bundle/{task_id}/{file_id}',
            headers={'Authorization': f'Bearer {token}'},
            allow_redirects=True,
            stream=True, timeout=86400
        )

        if response.status_code == 200:
            # create a destination directory to store the file in
            filepath = os.path.join(dest_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            list_paths_csv_results.append(filepath)

            # write the file to the destination directory
            with open(filepath, 'wb') as f:
                for data in response.iter_content(chunk_size=8192):
                    f.write(data)

            with open(logfilepath,'a+', encoding="utf-8") as f:
                f.write('#' * 80 + '\n')
                f.write('#' * 80 + '\n')
                f.write('\n \n')
                f.write(f'Created csv file at: {filepath}')
                f.write('\n \n')

            print(f'Created csv file at: {filepath}')

        else:
            with open(logfilepath,'a+', encoding="utf-8") as f:
                f.write('#' * 80 + '\n')
                f.write('#' * 80 + '\n')
                f.write('\n \n')
                f.write(f'Unexpected response with code {response.status_code}')
                f.write('\n \n')

            print(f'Unexpected response with code {response.status_code}')

    return list_paths_csv_results

def delete_task(task_id, token, logfilepath):
    """Deletes task on the server.

    Parameters
    ----------
    task_id: str
    token: str
    logfilepath: str
        path to the log file
    """

    response = requests.delete(
        f'https://appeears.earthdatacloud.nasa.gov/api/task/{task_id}',
        headers={'Authorization': f'Bearer {token}'}, timeout=86400)

    if response.status_code == 204:
        with open(logfilepath,'a+', encoding="utf-8") as f:
            f.write('#' * 80 + '\n')
            f.write('#' * 80 + '\n')
            f.write('\n \n')
            f.write(f'Task {task_id} successfully deleted.')
            f.write('\n \n')
        print(f'Task {task_id} successfully deleted.')
    else:
        with open(logfilepath,'a+', encoding="utf-8") as f:
            f.write('#' * 80 + '\n')
            f.write('#' * 80 + '\n')
            f.write('\n \n')
            f.write(f'Something went wrong when deleting task {task_id}.')
            f.write('\n \n')
        print(f'Something went wrong when deleting task {task_id}.')

def log_out(token, logfilepath):
    """Logs out and deletes the token.

    Parameters
    ----------
    token: str
    logfilepath: str
        path to the log file
    """

    logout_response = requests.post(
        'https://appeears.earthdatacloud.nasa.gov/api/logout', 
        headers={'Authorization': f'Bearer {token}'}, timeout=86400)

    if logout_response.status_code == 204:
        with open(logfilepath,'a+', encoding="utf-8") as f:
            f.write('#' * 80 + '\n')
            f.write('#' * 80 + '\n')
            f.write('\n \n')
            f.write('Succesfully logged out.')
            f.write('\n \n')
        print('Succesfully logged out.')
    else:
        with open(logfilepath,'a+', encoding="utf-8") as f:
            f.write('#' * 80 + '\n')
            f.write('#' * 80 + '\n')
            f.write('\n \n')
            f.write('Token may have already expired.')
            f.write('\n \n')
        print('Token may have already expired.')
