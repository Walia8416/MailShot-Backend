from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Gmail
import os

from django.conf import settings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import textwrap
import numpy as np
import pandas as pd
from pprint import pprint
import pickle 
import os.path 
import base64 
import email 
from bs4 import BeautifulSoup 

class InboxView(APIView):
    def get(self, request):
        creds = None
        
        SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=8080,prompt='consent')
            
            with open("token.json", "w") as token:
                token.write(creds.to_json())


        service = build('gmail', 'v1', credentials=creds)

        results = service.users().messages().list(userId='me', labelIds=['INBOX'],maxResults=1).execute()
        messages = results.get('messages', [])

        emails = []
        for message in messages:
           
            test = ''
  
            txt = service.users().messages().get(userId='me', id=message['id']).execute() 
    
    
            payload = txt['payload'] 
            headers = payload['headers'] 

            for d in headers: 
                if d['name'] == 'Subject': 
                    subject = d['value'] 
                if d['name'] == 'From': 
                    sender = d['value'] 

            print(message['id'])
            parts = payload.get('parts')
            parts = parts[0]
            data = parts['body']['data'] 
            data = data.replace("-","+").replace("_","/") 
            decoded_data = base64.b64decode(data) 
            soup = BeautifulSoup(decoded_data , "lxml") 
            body = soup.body() 
            test+="Subject: "+str(subject) + '\n' + "From: "+ str(sender) + '\n' + "Message: "+ str(body)
            email_dict = {
                'id': message['id'],
                'subject': subject,
                'body': str(body),  
            }

        
            emails.append(email_dict)
            

        return Response(emails)