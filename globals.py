from google_auth_oauthlib.flow      import InstalledAppFlow
from google.oauth2.credentials      import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery      import build

import os


name = True
creds = None


SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.announcements.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
    'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
    'https://www.googleapis.com/auth/classroom.topics.readonly'
]


creds = Credentials.from_authorized_user_file('token.json', SCOPES)


if creds and creds.expired and creds.refresh_token:
    creds.refresh(Request())

'''
if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port = 8080)

    with open('token.json', 'w') as token:
        token.write(creds.to_json())
'''

service = build('classroom', 'v1', credentials = creds).courses()
courses = service.list(pageSize = 15, courseStates = ['ACTIVE']).execute()['courses']

messages = []

hnews = None

lnu = None
max_news = 70

lineno = 0
