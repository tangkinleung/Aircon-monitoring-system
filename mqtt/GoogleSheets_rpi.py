from __future__ import print_function

from googleapiclient.discovery import build

from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'service.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1oXMZIQ7aM5AMpi--Icke5dIja2AGac12zf020ZukH3c'


SPREADSHEET_RANGE = "AirconPi!A:D"

service = build('sheets', 'v4', credentials=creds)
#Call sheets API
sheet = service.spreadsheets()

def push(data):
    insert = [data]
    request=service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range=SPREADSHEET_RANGE,
                                                     valueInputOption="USER_ENTERED", body={"values": insert}).execute()
    print(request)
    print("inserted")
