# TNP-Automation

## Set-up

 - A google cloud project created.

 - Sheets and Drive API enabled for the project at - https://console.cloud.google.com/apis/dashboard

 - Create an OAuth 2.0 web client with redirection URIs set to `http://127.0.0.1:5500`

 - Create a service account and generate a json key. Store the key as an environment variable `KEY`
 
 - Get IDs of the spreadsheet and folder. They are usually the bunch of alpha numeric characters at the end of shareable link.
 
 - Update everything in `app.py` IN YOUR LOCAL MACHINE, PLEASE DO NOT COMMIT THESE CHANGES.
 
