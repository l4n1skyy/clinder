from __future__ import print_function

import datetime
import zoneinfo
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    check_credentials()
    id = get_id()

    while True:
        action = input("input action, r (read), c (create), u (update), d (delete), e (exit): ")
        if action == 'r':
            read_event(id)
            print()
        elif action == 'c':
            create_event(id)
            print()
        elif action == 'u':
            update_event(id)
            print()
        elif action == 'd':
            delete_event(id)
            print()
        elif action == 'e':
            break
        else:
            print("not valid")


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

def get_id():
    file = open('token.json', 'r+')
    content = file.read()

    # If id in token
    if content.find("calendar_id") != -1 :
        start = content.find("calendar_id") + len("calendar_id") + 4
        id_temp = content[start:-2]
        calendar = service.calendars().get(calendarId=id_temp).execute()
        ans = input("use {}? (yes/no): ".format(calendar['summary']))

        # If using token id
        if ans in ['yes', 'y', 'Yes', 'YES']:
            write = False
            id = id_temp

        # If not using token id
        elif ans in ['no', 'n', 'No', 'NO']:
            write = True
            # remove old key
            file.seek(content.find("calendar_id") - 3)
            file.truncate()
            file.write('}')

    # If id not in token
    else:
        write = True

    if write == True:
        file.seek(0)
        content = file.read()[:-1]
        while True:
            id = input("calendar id: ")
            try:
                service.calendars().get(calendarId=id).execute()
            except:
                print("error, try again")
                continue
            break
        content = content + ', "calendar_id": "' + id + '"}'
        file.seek(0)
        file.write(content)

    file.close()
    return id

def read_event(id):
    mode = input("filter by time or summary?: ")
    # Get time range
    if mode == 'time':
        while True:
            user_input = input("Input minimum time, [DD-MM-YYYY HH:MM AM/PM]/today/tomorrow/this week/this month/this year: ")
            dt = convert_dt(id, user_input, 1)

            if dt == None:
                print("error, try again")
                continue
            
            if user_input in ["today", "tomorrow", "this week", "this year", "this month", "this year"]:
                timeMin = dt[0]
                timeMax = dt[1]
                max = False
            else:
                timeMin = dt
                max = True

            break
            
        while max == True:
            timeMax = convert_dt(id, input("Input maximum time [DD-MM-YYYY HH:MM AM/PM]: "), 1)

            if timeMax == None:
                print("error, try again")
            else:
                break

        #  Get and print events
        events_result = service.events().list(calendarId=id, timeMin=timeMin, timeMax=timeMax, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

    elif mode == 'summary':
        events = []
        summary = input("input summary: ")
        events_result = service.events().list(calendarId=id, singleEvents=True, orderBy='startTime').execute()
        temp = events_result.get('items', [])
        for event in temp:
            if event['summary'] == summary:
                events.append(event)

    if not events:
        print('No events found.')
        return

    print ("             id            |         start        |         end          | summary")
    print ("----------------------------------------------------------------------------------")
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        start = convert_dt(id, start, 2)
        end = event['end'].get('dateTime', event['end'].get('date'))
        end = convert_dt(id, end, 2)
        print(event['id'], '|', start, "|", end, "|", event['summary'])
    return

def create_event(id):

    # summary, location, description /
    # attendees, reminders, recurrence x

    timeZone = service.calendars().get(calendarId=id).execute()["timeZone"]
    start = convert_dt(id, input("Input start time [DD-MM-YYYY HH:MM AM/PM]: "), 1)
    end = convert_dt(id, input("Input end time [DD-MM-YYYY HH:MM AM/PM]: "), 1)

    print("Input details: title(summary)/location/description")
    print("example: summary= meeting, location= home, description= online meeting with client")

    event = {
    'start': {
        'dateTime': start,
        'timeZone': timeZone,
    },
    'end': {
        'dateTime': end,
        'timeZone': timeZone,
    }
    }

    details_input = input("details: ")
    details_input = details_input.split(', ')
    for detail in details_input:
        event.update({detail.split('= ')[0]:detail.split('= ')[1]})

    event = service.events().insert(calendarId=id, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
    return

def update_event(id):
    # Get event id from user
    read_event(id)
    event_id = input("event id: ")

    # Retrieve the event from the API.
    event = service.events().get(calendarId=id, eventId=event_id).execute()

    # Get update from user
    print("updateable fields: summary, description, location")
    field = input("field: ")
    content = input("change: ")

    # Update event with API
    event[field] = content
    updated_event = service.events().update(calendarId=id, eventId=event['id'], body=event).execute()

    return

def delete_event(id):
    # Get event id from user
    read_event(id)
    while True:
        event_id = input("input event id or e (exit): ")
        if event_id == 'e':
            break
        # Delete event with API
        service.events().delete(calendarId=id, eventId=event_id).execute()
    return

def convert_dt(id, dt, mode):
    # Convert timestamp to google calendar timestamp format
    timezone = service.calendars().get(calendarId=id).execute()["timeZone"]
    if mode == 1:
        if dt == "today":
            dt = datetime.datetime.now().replace(tzinfo=zoneinfo.ZoneInfo(timezone))
            min = dt
            max = dt + datetime.timedelta(days=1)
            min = min.strftime("%Y-%m-%dT00:00:00%z")
            max = max.strftime("%Y-%m-%dT00:00:00%z")
            return [min,max]

        elif dt == "tomorrow":
            dt = datetime.datetime.now().replace(tzinfo=zoneinfo.ZoneInfo(timezone))
            min = dt + datetime.timedelta(days=1)
            max = dt + datetime.timedelta(days=2)
            min = min.strftime("%Y-%m-%dT00:00:00%z")
            max = max.strftime("%Y-%m-%dT00:00:00%z")
            return [min,max]

        elif dt == "this week":
            dt = datetime.datetime.now().replace(tzinfo=zoneinfo.ZoneInfo(timezone))
            min = dt - datetime.timedelta(days=dt.weekday())
            max = dt + datetime.timedelta(days=7) - datetime.timedelta(days=dt.weekday())
            min = min.strftime("%Y-%m-%dT00:00:00%z")
            max = max.strftime("%Y-%m-%dT00:00:00%z")
            return [min,max]

        elif dt == "this month":
            dt = datetime.datetime.now()
            min = datetime.datetime(dt.year, dt.month, 1, 00, 00, 00, 00).replace(tzinfo=zoneinfo.ZoneInfo(timezone))
            max = datetime.datetime(dt.year, dt.month + 1, 1, 00, 00, 00, 00).replace(tzinfo=zoneinfo.ZoneInfo(timezone))
            min = min.strftime("%Y-%m-%dT00:00:00%z")
            max = max.strftime("%Y-%m-%dT00:00:00%z")
            return [min, max]

        elif dt == "this year":
            dt = datetime.datetime.now()
            min = datetime.datetime(dt.year, 1, 1, 00, 00, 00, 00).replace(tzinfo=zoneinfo.ZoneInfo(timezone))
            max = datetime.datetime(dt.year + 1, 1, 1, 00, 00, 00, 00).replace(tzinfo=zoneinfo.ZoneInfo(timezone))
            min = min.strftime("%Y-%m-%dT00:00:00%z")
            max = max.strftime("%Y-%m-%dT00:00:00%z")
            return [min,max]

        else:
            try:
                dt = datetime.datetime.strptime(dt,"%d-%m-%Y %I:%M %p").replace(tzinfo=zoneinfo.ZoneInfo(timezone))
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

if __name__ == '__main__':
    main()