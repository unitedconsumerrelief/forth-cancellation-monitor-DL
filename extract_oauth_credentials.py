#!/usr/bin/env python3
"""
Helper script to extract OAuth credentials from credentials.json and token.json
for Render deployment. This script helps you get the environment variables needed.
"""

import json
import os
import sys

def extract_credentials():
    """Extract OAuth credentials from JSON files."""
    
    # Check for credentials.json
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("Please download it from Google Cloud Console and place it in this directory.")
        return False
    
    # Check for token.json
    if not os.path.exists('token.json'):
        print("❌ token.json not found!")
        print("Please run 'python app.py' first to generate token.json via OAuth flow.")
        return False
    
    try:
        # Load credentials.json
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        # Load token.json
        with open('token.json', 'r') as f:
            token_data = json.load(f)
        
        # Extract OAuth credentials
        client_id = creds_data['installed']['client_id']
        client_secret = creds_data['installed']['client_secret']
        refresh_token = token_data.get('refresh_token')
        
        if not refresh_token:
            print("❌ No refresh token found in token.json!")
            print("Please delete token.json and run 'python app.py' again to get a fresh token.")
            return False
        
        print("✅ OAuth credentials extracted successfully!")
        print("\n" + "="*60)
        print("RENDER ENVIRONMENT VARIABLES")
        print("="*60)
        print(f"GOOGLE_CLIENT_ID={client_id}")
        print(f"GOOGLE_CLIENT_SECRET={client_secret}")
        print(f"GOOGLE_REFRESH_TOKEN={refresh_token}")
        print("="*60)
        print("\n📋 Copy these environment variables to your Render deployment:")
        print("1. Go to your Render service dashboard")
        print("2. Navigate to Environment tab")
        print("3. Add each variable above")
        print("4. Deploy your service")
        
        return True
        
    except KeyError as e:
        print(f"❌ Error extracting credentials: Missing key {e}")
        print("Please check your credentials.json and token.json files.")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function."""
    print("🔐 Gmail OAuth Credentials Extractor")
    print("This script extracts OAuth credentials for Render deployment.\n")
    
    if extract_credentials():
        print("\n✅ All done! Your app is ready for Render deployment.")
    else:
        print("\n❌ Please fix the issues above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()

