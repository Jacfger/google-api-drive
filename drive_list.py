from __future__ import print_function

from googleapiclient import discovery
from googleapiclient.http import MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools
import io

SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_id.json', SCOPES)
    creds = tools.run_flow(flow, store)
DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))

page_token = None
while True:
    response = DRIVE.files().list(q="name contains 'pkl'",
                                          spaces='drive',
                                          fields='nextPageToken, files(id, name)',
                                          pageToken=page_token).execute()
    for file in response.get('files', []):
        # Process change
        print ('Found file: %s (%s)' % (file.get('name'), file.get('id')))
        request = DRIVE.files().get_media(fileId=file.get('id'))
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print ('Download {}%.'.format(status.progress() * 100))
        fh.seek(0)
        with open(file.get('name'), 'wb') as f:
            f.write(fh.read())
    
    page_token = response.get('nextPageToken', None)
    if page_token is None:
        break