# config.py
#
# Copyright (C) 2024-2030 Yun Liu
# University of Chicago
#
# Set configuration options based on environment
#
##
__author__ = 'Yun Liu <yunliuu@uchicago.edu>'

import os
import json
import boto3
import base64
from botocore.exceptions import ClientError

class Config(object):
    BASE_DIR = os.path.expanduser("/Users/summersane/Desktop/RA/Radiology/ROC_Analysis")  # home dir
    DATA_DIR_PATH = os.path.join(BASE_DIR, 'Data')
    USER_FOLDER = os.path.join(DATA_DIR_PATH, 'User')
    LOG_FOLDER = os.path.join(DATA_DIR_PATH, 'Log')

    SETTINGS_FILE = os.path.join(LOG_FOLDER, 'settings.json')
    LOG_FILE_PATH = os.path.join(LOG_FOLDER, 'user_log.txt')

    MAX_MEMORY_USAGE = 200 * 1024 * 1024 * 1024  # 200 GB in bytes
    ADMIN_EMAILS = ['yunliuu@uchicago.edu']
