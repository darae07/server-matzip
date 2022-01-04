import json
import pickle
import os
from datetime import datetime

from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request


def create_service(api_name, api_version, *scopes):
    CLIENT_SECRET_CONFIG = json.loads(os.environ.get('GOOGLE_CREDENTIALS'))
    print(CLIENT_SECRET_CONFIG)
    API_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]

    cred = None

    pickle_file = f'token_{API_NAME}_{API_VERSION}.pickle'

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(CLIENT_SECRET_CONFIG, SCOPES)
            cred = flow.run_local_server(port=0)
        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_NAME, API_VERSION, credentials=cred)
        print(API_NAME, 'service created successfully')
        return service
    except Exception as e:
        print(e)
        return None


def convert_to_rfc_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt
