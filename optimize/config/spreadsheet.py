from __future__ import print_function

import os.path
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from utils.logger import logger

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '16Xxl754P2D33Ca1fEZzIDmlooJSCwN-XOUeWMsJWEcs'
SAMPLE_RANGE_NAME = 'Config!A2:H'

# Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=66061455128-2lpvm8j8faqdhc8tqt5f1uf4sqspk033.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A49898%2F&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fspreadsheets.readonly&state=zD5rYkXYjs4VGS1Rf1HeJsuxPFyTbh&access_type=offline
# <HttpError 403 when requesting https://sheets.googleapis.com/v4/spreadsheets/16Xxl754P2D33Ca1fEZzIDmlooJSCwN-XOUeWMsJWEcs/values/Class%20Data%21A2%3AE?alt=json returned "Google Sheets API has not been used in project 66061455128 before or it is disabled. Enable it by visiting https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=66061455128 then retry. If you enabled this API recently, wait a few minutes for the action to propagate to our systems and retry.". Details: "[{'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Google developers console API activation', 'url': 'https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=66061455128'}]}, {'@type': 'type.googleapis.com/google.rpc.ErrorInfo', 'reason': 'SERVICE_DISABLED', 'domain': 'googleapis.com', 'metadata': {'consumer': 'projects/66061455128', 'service': 'sheets.googleapis.com'}}]">
# 
# https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=66061455128
# 


class Spreadsheet:
    def __init__(self, config):
        self._oauth_credentials = None
        self._sheets_service = None
        self._config = config
        self._oauth_credentials = Credentials(
            token=config['access_token'],
            refresh_token=config['refresh_token'],
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            token_uri='https://accounts.google.com/o/oauth2/token',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )

    def _get_sheet_service(self):
        if not self._sheets_service:
            try:
                service = build('sheets', 'v4', credentials=self._oauth_credentials)
                self._sheets_service = service.spreadsheets()

            except Exception as ex:
                raise ex
        return self._sheets_service
    

    #TODO make columns dynamic on spreadsheet_range
    def get_range(self, spreadsheet_id, spreadsheet_tab_name = "Config", spreadsheet_range = "A1:H"):
        return self._get_sheet_service().values().get(spreadsheetId=spreadsheet_id, range=spreadsheet_tab_name + "!" + spreadsheet_range).execute()

    def get_value(self, sheet_id, spreadsheet_tab_name = "Config", range = "A1:H"):
        try:
          range = self.get_range(sheet_id, spreadsheet_tab_name, range)
        except Exception:
          return None
        if range.get('values') is None:
          return None
        return range['values']
    
    def process_spreadsheet_configuration(self):
        logger(self.__class__.__name__).info("Attempting to read spreadsheet_id: " + self._config['spreadsheet_id'])
        try:
            configuration = self.get_value(self._config['spreadsheet_id'])
            result = []
            for i in range(1, len(configuration)):
                transform_dict = {}
                for j, values in enumerate(configuration[i]):
                    transform_dict.update(dict({configuration[0][j]: values}))
                result.append(transform_dict)
            logger(self.__class__.__name__).info("Reading was sucessfull")
            logger(self.__class__.__name__).debug("Spreadsheet Configuration: " + str(result))
            return result
        except Exception as ex:
            raise ex