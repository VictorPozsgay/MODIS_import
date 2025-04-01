"""This module has functions that allow for authentication, task submission, download"""

import time
from datetime import datetime
import os
import requests
import pandas as pd

##################################################################################
##################################################################################

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
