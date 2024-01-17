from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Gmail
import os
from transformers import pipeline
from rest_framework.decorators import api_view, renderer_classes
from django.conf import settings
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
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
import datetime
import re

creds = None


def convertDate(timestamp):
    date_object = datetime.datetime.fromtimestamp(timestamp / 1000) 
    formatted_date = date_object.strftime("%Y-%m-%d %H:%M:%S")
    return str(formatted_date)

def SetupGmail():
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
    return service


class InboxView(APIView):
    def get(self,request):
        try:
            service = SetupGmail()
            results = service.users().messages().list(userId='me', q='label:inbox',maxResults=1).execute()
        except errors.HttpError as error:
            return JsonResponse({'error': str(error)}, status=400)
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
            date = convertDate(int(txt["internalDate"]))
            email_dict = {
                'id': message['id'],
                'sender':sender,
                'subject': subject,
                'snippet':txt['snippet'],
                'date':  date
            }
           
            emails.append(email_dict)
            
        return Response(emails)

def remove_urls(email_text):
    email_text = re.sub(r'\([^)]*\)', '', email_text)
    email_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', email_text)
    email_text = re.sub(r'[^a-zA-Z0-9\s.,!-]', '', email_text)
    email_text = ' '.join(email_text.split())
    return email_text
    
def get_plain_text(message):
    payload = message['payload']
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                plain_text = base64.urlsafe_b64decode(data).decode('utf-8')
                return remove_urls(plain_text)
    return None

@api_view(('GET',))
def detailEmailView(request,pk):
    try:
        service = SetupGmail()
        txt = service.users().messages().get(userId='me', id=pk).execute() 
    except errors.HttpError as error:
        return JsonResponse({'error': str(error)}, status=400)

    payload = txt['payload'] 
    headers = payload['headers'] 
    for d in headers: 
        if d['name'] == 'Subject': 
            subject = d['value'] 
        if d['name'] == 'From': 
            sender = d['value'] 
        
    plain_text = get_plain_text(txt)
    email = []
    date = convertDate(int(txt["internalDate"]))
    email_dict = {
        'id': pk,
        'sender':sender,
        'subject': subject,
        'body':plain_text,
        'date':date,

    }
    print(plain_text)
    email.append(email_dict)
    return Response(email)



@api_view(('GET',))
def summarizeEmailView(request,pk):
    try:
        service = SetupGmail()
        txt = service.users().messages().get(userId='me', id=pk).execute() 
    except errors.HttpError as error:
        return JsonResponse({'error': str(error)}, status=400)

    payload = txt['payload'] 
    headers = payload['headers'] 
    for d in headers: 
        if d['name'] == 'Subject': 
            subject = d['value'] 
        if d['name'] == 'From': 
            sender = d['value'] 
        
    plain_text = 'subject - '+subject+'\n'+get_plain_text(txt)
    email = []
    summarizer = pipeline('summarization', model="sshleifer/distilbart-cnn-12-6")
    plain_text = str(summarizer(plain_text, max_length=130, min_length=30))

    email_dict = {
        'id': pk,
        'sender':sender,
        'subject': subject,
        'summarized_text':plain_text[20:-5],
    }
    email.append(email_dict)
    return Response(email)

