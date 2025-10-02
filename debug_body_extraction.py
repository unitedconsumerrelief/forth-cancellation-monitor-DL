#!/usr/bin/env python3
"""
Debug script to test email body extraction from Gmail API.
This will help us understand why the body content is not showing in Slack.
"""

import os
import base64
import email
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def extract_message_body(payload):
    """Extract text body from email payload."""
    body = ""
    
    def extract_from_part(part):
        print(f"Processing part with mimeType: {part.get('mimeType')}")
        if part.get('mimeType') == 'text/plain':
            data = part.get('body', {}).get('data', '')
            if data:
                try:
                    decoded = base64.urlsafe_b64decode(data).decode('utf-8')
                    print(f"Extracted plain text body: {decoded[:200]}...")
                    return decoded
                except Exception as e:
                    print(f"Error decoding plain text: {e}")
                    return ""
        elif part.get('mimeType') == 'text/html':
            data = part.get('body', {}).get('data', '')
            if data:
                try:
                    html = base64.urlsafe_b64decode(data).decode('utf-8')
                    import re
                    text = re.sub(r'<[^>]+>', '', html)
                    text = re.sub(r'\s+', ' ', text).strip()
                    print(f"Extracted HTML body: {text[:200]}...")
                    return text
                except Exception as e:
                    print(f"Error decoding HTML: {e}")
                    return ""
        elif 'parts' in part:
            print(f"Found {len(part['parts'])} subparts")
            for i, subpart in enumerate(part['parts']):
                print(f"Processing subpart {i+1}")
                result = extract_from_part(subpart)
                if result:
                    return result
        return ""
    
    print(f"Payload mimeType: {payload.get('mimeType')}")
    print(f"Payload has parts: {'parts' in payload}")
    if 'parts' in payload:
        print(f"Number of parts: {len(payload['parts'])}")
    
    # Check if payload has direct text content
    if payload.get('mimeType') == 'text/plain':
        data = payload.get('body', {}).get('data', '')
        if data:
            try:
                decoded = base64.urlsafe_b64decode(data).decode('utf-8')
                print(f"Direct plain text body: {decoded[:200]}...")
                return decoded
            except Exception as e:
                print(f"Error decoding direct plain text: {e}")
    
    # Check if payload has direct HTML content
    elif payload.get('mimeType') == 'text/html':
        data = payload.get('body', {}).get('data', '')
        if data:
            try:
                html = base64.urlsafe_b64decode(data).decode('utf-8')
                import re
                text = re.sub(r'<[^>]+>', '', html)
                text = re.sub(r'\s+', ' ', text).strip()
                print(f"Direct HTML body: {text[:200]}...")
                return text
            except Exception as e:
                print(f"Error decoding direct HTML: {e}")
    
    # Check parts recursively
    if 'parts' in payload:
        for i, part in enumerate(payload['parts']):
            print(f"Processing part {i+1}")
            result = extract_from_part(part)
            if result:
                body = result
                break
    
    # If no body found, use snippet as fallback
    if not body:
        body = payload.get('snippet', '')
        print(f"Using snippet as body: {body[:200]}...")
    
    return body

def test_gmail_connection():
    """Test Gmail connection and extract body from a sample message."""
    try:
        # Load existing credentials
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                print("No valid credentials found. Please run the main app first.")
                return
        
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)
        
        # Search for Forth cancellation emails
        query = 'from:noreply@forthcrm.com (subject:"Cancellation" OR subject:"Cancel" OR subject:"cancelled" OR subject:"cancelled") newer_than:7d'
        print(f"Searching with query: {query}")
        
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=1
        ).execute()
        
        messages = results.get('messages', [])
        if not messages:
            print("No messages found")
            return
        
        print(f"Found {len(messages)} messages")
        
        # Get the first message
        message_id = messages[0]['id']
        print(f"Analyzing message: {message_id}")
        
        # Get full message
        message = service.users().messages().get(
            userId='me', id=message_id, format='full'
        ).execute()
        
        print("\n" + "="*60)
        print("MESSAGE ANALYSIS")
        print("="*60)
        
        # Extract headers
        headers = message['payload'].get('headers', [])
        header_dict = {h['name'].lower(): h['value'] for h in headers}
        
        print(f"Subject: {header_dict.get('subject', 'No Subject')}")
        print(f"From: {header_dict.get('from', 'Unknown Sender')}")
        print(f"Date: {header_dict.get('date', 'Unknown Date')}")
        
        print(f"\nSnippet: {message.get('snippet', 'No snippet')}")
        
        print("\n" + "="*60)
        print("BODY EXTRACTION DEBUG")
        print("="*60)
        
        # Extract body
        body = extract_message_body(message['payload'])
        
        print(f"\nFinal extracted body length: {len(body)}")
        print(f"Body content:\n{body}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gmail_connection()
