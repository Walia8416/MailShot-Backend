import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from transformers import pipeline
import textwrap
import numpy as np
import pandas as pd
from pprint import pprint
import pickle 
import os.path 
import base64 
import email 
from bs4 import BeautifulSoup 
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=8080)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    result = service.users().messages().list(userId='me',maxResults=1).execute() 

    messages = result.get('messages') 
    
 
    for msg in messages: 
        test = ''
  
        txt = service.users().messages().get(userId='me', id=msg['id']).execute() 
  
 
        payload = txt['payload'] 
        headers = payload['headers'] 

        for d in headers: 
            if d['name'] == 'Subject': 
                subject = d['value'] 
            if d['name'] == 'From': 
                sender = d['value'] 

 
        parts = payload.get('parts')[0] 
        data = parts['body']['data'] 
        data = data.replace("-","+").replace("_","/") 
        decoded_data = base64.b64decode(data) 

   
        soup = BeautifulSoup(decoded_data , "lxml") 
        body = soup.body() 
        test+="Subject: "+str(subject) + '\n' + "From: "+ str(sender) + '\n' + "Message: "+ str(body)
      
        print("Message: ", body)
        summarizer = pipeline('summarization', model="Falconsai/text_summarization")
        print(summarizer(str(test), max_length=230, min_length=30)) 
        print('\n') 
        
  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()