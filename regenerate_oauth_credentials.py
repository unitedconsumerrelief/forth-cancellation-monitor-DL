#!/usr/bin/env python3
"""
Script to regenerate OAuth credentials for Render deployment.
This will help you get fresh credentials to update in your environment variables.
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def regenerate_credentials():
    """Regenerate OAuth credentials and extract them for environment variables."""
    
    print("🔄 Regenerating OAuth credentials...")
    print("This will help you get fresh credentials for your Render environment variables.")
    print()
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ Error: credentials.json not found!")
        print("Please make sure you have downloaded it from Google Cloud Console.")
        return
    
    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save to token.json
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        
        print("✅ OAuth flow completed successfully!")
        print("✅ Credentials saved to token.json")
        print()
        
        # Extract credentials for environment variables
        print("🔑 Here are your credentials for Render environment variables:")
        print("=" * 60)
        
        # Read the credentials.json to get client info
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        client_id = creds_data['installed']['client_id']
        client_secret = creds_data['installed']['client_secret']
        refresh_token = creds.token
        
        print(f"GOOGLE_CLIENT_ID={client_id}")
        print(f"GOOGLE_CLIENT_SECRET={client_secret}")
        print(f"GOOGLE_REFRESH_TOKEN={refresh_token}")
        print("=" * 60)
        print()
        
        print("📋 Next steps:")
        print("1. Copy the above values")
        print("2. Go to your Render dashboard")
        print("3. Update your environment variables with these new values")
        print("4. Redeploy your service")
        print()
        
        # Test the credentials
        print("🧪 Testing credentials...")
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        print(f"✅ Gmail API test successful! Found {len(labels)} labels.")
        
    except Exception as e:
        print(f"❌ Error during OAuth flow: {e}")
        print("Please check your credentials.json file and try again.")

if __name__ == "__main__":
    regenerate_credentials()
