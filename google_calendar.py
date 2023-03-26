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

    # id = input("calendar id: ")
    id = "6c82977aa7912c1e788a88f97946dede7dc51b7bb5b169b08e5fbb57ce9027f0@group.calendar.google.com"

    read_event(id)

# Check credentials and initialize service variable
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
        return
    
    print("authentication successful")
    return

# Convert timestamp to google calendar timestamp format
def convert_dt(id, dt, mode):
    # Convert timestamp to google calendar timestamp format
    if mode == 1:
        try:
            timezone = service.calendars().get(calendarId=id).execute()["timeZone"]
            dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M").replace(tzinfo=zoneinfo.ZoneInfo(timezone))
            dt = dt.strftime("%Y-%m-%dT%H:%M:00%z")
        except Exception as e:
            return None
        return(dt)

    # Convert google calendar timestamp format to timestamp
    elif mode == 2:
        try:
            dt = datetime.datetime.strptime(dt,"%Y-%m-%dT%H:%M:00%z")
            dt = dt.strftime("%d-%m-%Y, %I:%M %p")
        except Exception as e:
            return None
        return(dt)
        


def read_event(id):
    while True:
        timeMin = convert_dt(id, input("Input minimum time [YYYY-MM-DD HH:MM]: "), 1)

        if timeMin == None:
            print("error, try again")
        else:
            break
         
    while True:
        timeMax = convert_dt(id, input("Input maximum time [YYYY-MM-DD HH:MM]: "), 1)

        if timeMax == None:
            print("error, try again")
        else:
            break

        
    events_result = service.events().list(calendarId=id, timeMin=timeMin, timeMax=timeMax, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return

    print ("        start        |         end          | summary")
    print ("-----------------------------------------------------")
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        start = convert_dt(id, start, 2)
        end = event['end'].get('dateTime', event['end'].get('date'))
        end = convert_dt(id, end, 2)
        print(start, "|", end, "|", event['summary'])

    return

def create_event():
    return

def update_event():
    return

def delete_event():
    return

if __name__ == '__main__':
    main()