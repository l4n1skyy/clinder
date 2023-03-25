from __future__ import print_function

import datetime
import zoneinfo
import os.path
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    check_credentials()
    id = "d2afd35591cb7e8070e99086aa586dadbf45911d3ee5ac86999375c1b35718e6@group.calendar.google.com"
    # id = input("calendar id: ")

def check_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        global service
        service = build('calendar', 'v3', credentials=creds)

    except HttpError as error:
        print('An error occurred: %s' % error)
        sys.exit()

    print("authentication successful")
    return

def read_event():
    return

# Convert timestamp to google calendar timestamp format
def convert_dt(id, dt):
    try:
        timezone = service.calendars().get(calendarId=id).execute()["timeZone"]
        dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S").replace(tzinfo=zoneinfo.ZoneInfo(timezone))
        dt = dt.strftime("%Y-%m-%dT%H:%M:%S%z")

    except Exception as e:
        print(e)
        dt = None

    return(dt)


def create_event():
    return

def update_event():
    return

def delete_event():
    return

if __name__ == '__main__':
    main()