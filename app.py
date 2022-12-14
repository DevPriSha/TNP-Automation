from __future__ import print_function
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from flask import Flask, request, jsonify, render_template
from datetime import datetime

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r"D:\Documents\GitHub\TNP-website\resume-371519-94427ed57d8b.json" #path to service account credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

folder = "1y7JTdl2qx8toMnQsB85lRCToxj3LRtYC" #folder id of drive folder where resumes are stored
data_sheet = "1S0bkIAAMrNeWxhQ4fqHkjrNVqnEcjpiI0SnIvKcOdOw" #id of google sheet where data is stored


def update_resume(enroll, filename):
    creds, _ = google.auth.default()
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
        q=f"name contains '{enroll}' and parents in '{folder}'",
        fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
            service.files().delete(fileId=item['id']).execute()
            print('File deleted')


    try:

        file_metadata = {
            'name': filename,
            'parents': [folder]
        }
        media = MediaFileUpload(filename,
                                mimetype='application/pdf', resumable=True)
        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(F'File ID: "{file.get("id")}".')

        service_sheet = build('sheets', 'v4', credentials=creds)

        # Retrieve the documents contents from the Docs service.
        sheet = service_sheet.spreadsheets()
        result = sheet.values().get(spreadsheetId=data_sheet, range="Sheet1!A1:Z1000").execute()
        values = result.get('values', [])

        # add enroll and resume link to sheet as new row
        if not values:
            print('No data found.')
        else:
            for row in values:
                print('%s, %s' % (row[0], row[1]))
                if row[0] == enroll:
                    print("found")
                    service_sheet.spreadsheets().values().update(
                        spreadsheetId=data_sheet,
                        range=f"Sheet1!A{values.index(row)+1}:Z{values.index(row)+1}",
                        valueInputOption="USER_ENTERED",
                        body={
                            "values": [
                                [
                                    f"{enroll}",
                                    f"https://drive.google.com/file/d/{file.get('id')}/view?usp=sharing"
                                ]
                            ]
                        }
                    ).execute()
                    print("updated")
                    return jsonify({'success': 'true'})
            print("not found")
            service_sheet.spreadsheets().values().append(
                spreadsheetId=data_sheet,
                range="Sheet1!A1:Z1000",
                valueInputOption="USER_ENTERED",
                body={
                    "values": [
                        [
                            enroll,
                            f"https://drive.google.com/file/d/{file.get('id')}/view?usp=sharing"
                        ]
                    ]
                }
            ).execute()
            print("added")
            return jsonify({'success': 'true'})

    except HttpError as error:
        print(F'An error occurred: {error}')
        return jsonify({'error': error})


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/update', methods=['POST'])
def upload():
    enroll = request.form.get('name')
    file = request.files['resume']
    filename = enroll+"-"+datetime.today().strftime('%d-%m-%Y')+".pdf"
    #save file to local with filename
    file.save(filename)

    return update_resume(enroll, filename)
    #search for file in drive folder
    
    # os.remove(filename)

if __name__ == '__main__':
    app.run(debug=True, port=5500)