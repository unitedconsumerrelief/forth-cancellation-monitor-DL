#!/usr/bin/env python3
"""
Gmail to Slack notification service for Forth CRM cancellations.
Monitors Gmail for specific emails and posts them to Slack.
"""

import os
import base64
import sqlite3
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from flask import Flask, jsonify
from waitress import serve

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pytz
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailSlackMonitor:
    """Monitor Gmail for specific emails and post to Slack."""
    
    def __init__(self):
        """Initialize the monitor with configuration from environment variables."""
        self.gmail_query = os.getenv('GMAIL_QUERY', 'from:noreply@forthcrm.com (subject:"Cancellation" OR subject:"Cancel" OR subject:"cancelled" OR subject:"cancelled") newer_than:7d')
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.slack_channel = os.getenv('SLACK_CHANNEL', '#forth-alerts')
        self.slack_username = os.getenv('SLACK_USERNAME', 'Gmail Monitor')
        self.poll_interval = int(os.getenv('POLL_INTERVAL_SECONDS', '60'))
        self.timezone = os.getenv('TIMEZONE', 'UTC')
        self.return_full_body = os.getenv('RETURN_FULL_BODY', 'true').lower() == 'true'
        
        # Initialize timezone
        try:
            self.tz = pytz.timezone(self.timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone: {self.timezone}, using UTC")
            self.tz = pytz.UTC
        
        # Initialize database and Gmail service
        self.init_database()
        self.init_gmail_service()
    
    def init_database(self):
        """Initialize SQLite database for tracking processed messages."""
        try:
            conn = sqlite3.connect('state.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processed (
                    id TEXT PRIMARY KEY,
                    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def init_gmail_service(self):
        """Initialize Gmail API service with Service Account authentication."""
        try:
            # Only use Service Account authentication
            if not self._load_service_account_from_env():
                logger.error("Service Account credentials are missing. Please check your environment variables:")
                logger.error("- GOOGLE_SERVICE_ACCOUNT_EMAIL")
                logger.error("- GOOGLE_PRIVATE_KEY") 
                logger.error("- GOOGLE_DELEGATED_EMAIL")
                raise Exception("Service Account credentials are missing. Please check your environment variables.")
            
            logger.info("Loading Service Account credentials from environment variables")
            creds = self._get_service_account_credentials()
            
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {e}")
            raise


    def _load_service_account_from_env(self):
        """Check if Service Account credentials are available in environment variables."""
        required_vars = [
            'GOOGLE_SERVICE_ACCOUNT_EMAIL',
            'GOOGLE_PRIVATE_KEY',
            'GOOGLE_DELEGATED_EMAIL'
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                logger.debug(f"Environment variable {var} not set")
                return False
        
        logger.debug("All required Service Account environment variables are set")
        return True

    def _get_service_account_credentials(self):
        """Create Service Account credentials from environment variables."""
        try:
            # Get the delegated email (the user to impersonate)
            delegated_email = os.getenv('GOOGLE_DELEGATED_EMAIL')
            
            # Process private key - handle newline characters and quotes
            private_key = os.getenv('GOOGLE_PRIVATE_KEY', '')
            if private_key:
                # Replace literal \n with actual newlines
                private_key = private_key.replace('\\n', '\n')
                # Remove any surrounding quotes if present
                private_key = private_key.strip('"').strip("'")
            
            # Create credentials info dict
            credentials_info = {
                "type": "service_account",
                "project_id": os.getenv('GOOGLE_PROJECT_ID', 'master-cpa-data'),
                "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID', ''),
                "private_key": private_key,
                "client_email": os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL'),
                "client_id": os.getenv('GOOGLE_CLIENT_ID', ''),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')}",
                "universe_domain": "googleapis.com"
            }
            
            # Create service account credentials
            creds = service_account.Credentials.from_service_account_info(
                credentials_info, 
                scopes=SCOPES
            )
            
            # Create delegated credentials (impersonate the user)
            delegated_creds = creds.with_subject(delegated_email)
            
            logger.info(f"Service Account credentials created for {delegated_email}")
            return delegated_creds
            
        except Exception as e:
            logger.error(f"Failed to load Service Account credentials from environment: {e}")
            raise

    def poll_gmail(self):
        """Poll Gmail for new messages matching the query."""
        try:
            logger.info(f"Polling Gmail with query: {self.gmail_query}")
            
            # Search for messages
            results = self.gmail_service.users().messages().list(
                userId='me', 
                q=self.gmail_query,
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} messages")
            
            new_messages = 0
            skipped_messages = 0
            for message in messages:
                message_id = message['id']
                
                # Check if already processed
                if self.is_message_processed(message_id):
                    logger.debug(f"Message {message_id} already processed, skipping")
                    skipped_messages += 1
                    continue
                
                # Get message details
                message_data = self.get_message_details(message_id)
                if message_data:
                    # Additional duplicate check based on Record ID or content
                    if self.is_duplicate_by_content(message_data):
                        record_id = self.extract_record_id(message_data)
                        if record_id:
                            logger.debug(f"Record ID {record_id} already processed, skipping duplicate")
                        else:
                            logger.debug(f"Message with subject '{message_data['subject']}' already processed based on content, skipping")
                        skipped_messages += 1
                        continue
                    
                    # Post to Slack
                    if self.post_to_slack(message_data):
                        # Mark as processed
                        self.mark_message_processed(message_id)
                        # Also mark by content for additional safety
                        self.mark_content_processed(message_data)
                        new_messages += 1
                        
                        # Log with Record ID if available
                        record_id = self.extract_record_id(message_data)
                        if record_id:
                            logger.info(f"Posted new message to Slack: {message_data['subject']} (Record ID: {record_id})")
                        else:
                            logger.info(f"Posted new message to Slack: {message_data['subject']}")
                    else:
                        logger.error(f"Failed to post message to Slack: {message_data['subject']}")
            
            logger.info(f"Polling complete. Processed {new_messages} new messages, skipped {skipped_messages} already processed")
            
        except Exception as e:
            logger.error(f"Error during Gmail polling: {e}")

    def is_message_processed(self, message_id: str) -> bool:
        """Check if a message has already been processed."""
        try:
            conn = sqlite3.connect('state.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM processed WHERE id = ?', (message_id,))
            result = cursor.fetchone()
            conn.close()
            is_processed = result is not None
            logger.debug(f"Message {message_id} processed status: {is_processed}")
            return is_processed
        except Exception as e:
            logger.error(f"Error checking if message is processed: {e}")
            return False

    def mark_message_processed(self, message_id: str):
        """Mark a message as processed."""
        try:
            conn = sqlite3.connect('state.db')
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO processed (id) VALUES (?)', (message_id,))
            conn.commit()
            conn.close()
            logger.debug(f"Marked message {message_id} as processed")
        except Exception as e:
            logger.error(f"Error marking message as processed: {e}")

    def is_duplicate_by_content(self, message_data: Dict[str, Any]) -> bool:
        """Check if a message with similar content has already been processed."""
        try:
            conn = sqlite3.connect('state.db')
            cursor = conn.cursor()
            
            # Create a content hash based on subject and date
            content_hash = self.create_content_hash(message_data)
            cursor.execute('SELECT id FROM processed WHERE id = ?', (content_hash,))
            result = cursor.fetchone()
            conn.close()
            
            is_duplicate = result is not None
            logger.debug(f"Content duplicate check for '{message_data['subject']}': {is_duplicate}")
            return is_duplicate
        except Exception as e:
            logger.error(f"Error checking content duplicate: {e}")
            return False

    def mark_content_processed(self, message_data: Dict[str, Any]):
        """Mark message content as processed."""
        try:
            conn = sqlite3.connect('state.db')
            cursor = conn.cursor()
            
            # Create a content hash based on subject and date
            content_hash = self.create_content_hash(message_data)
            cursor.execute('INSERT OR IGNORE INTO processed (id) VALUES (?)', (content_hash,))
            conn.commit()
            conn.close()
            logger.debug(f"Marked content as processed: {content_hash}")
        except Exception as e:
            logger.error(f"Error marking content as processed: {e}")

    def extract_record_id(self, message_data: Dict[str, Any]) -> Optional[str]:
        """Extract Record ID from email body for deduplication."""
        try:
            body = message_data.get('body', '')
            
            # Look for Record ID pattern in the body
            import re
            patterns = [
                r'Record ID:\s*(\d+)',
                r'Record\s+ID:\s*(\d+)',
                r'ID:\s*(\d+)',
                r'#(\d+)',  # In case it's formatted as #123456
            ]
            
            for pattern in patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    record_id = match.group(1)
                    logger.debug(f"Extracted Record ID: {record_id}")
                    return record_id
            
            # If no Record ID found, fall back to subject-based hash
            logger.debug("No Record ID found, using subject-based hash")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting Record ID: {e}")
            return None

    def create_content_hash(self, message_data: Dict[str, Any]) -> str:
        """Create a hash based on message content for duplicate detection."""
        import hashlib
        
        # First try to use Record ID if available
        record_id = self.extract_record_id(message_data)
        if record_id:
            return f"record_{record_id}"
        
        # Fall back to subject and date if no Record ID found
        content = f"{message_data['subject']}_{message_data['date']}"
        return hashlib.md5(content.encode()).hexdigest()

    def get_message_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific message."""
        try:
            message = self.gmail_service.users().messages().get(
                userId='me', 
                id=message_id,
                format='full'
            ).execute()
            
            payload = message['payload']
            headers = payload.get('headers', [])
            
            # Extract headers
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Parse and format date
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(date_str)
                if self.tz:
                    dt = dt.astimezone(self.tz)
                formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S %Z')
            except:
                formatted_date = date_str
            
            # Extract body
            body = self.extract_message_body(payload)
            
            return {
                'subject': subject,
                'sender': sender,
                'date': formatted_date,
                'body': body,
                'thread_id': message.get('threadId', ''),
                'snippet': message.get('snippet', '')
            }
            
        except HttpError as e:
            logger.error(f"Gmail API error for message {message_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting message details for {message_id}: {e}")
            return None

    def extract_message_body(self, payload: Dict[str, Any]) -> str:
        """Extract text body from email payload."""
        body = ""
        
        def extract_from_part(part):
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    try:
                        return base64.urlsafe_b64decode(data).decode('utf-8')
                    except Exception:
                        return ""
            elif part.get('mimeType') == 'text/html':
                data = part.get('body', {}).get('data', '')
                if data:
                    try:
                        html = base64.urlsafe_b64decode(data).decode('utf-8')
                        # Simple HTML to text conversion
                        import re
                        text = re.sub(r'<[^>]+>', '', html)
                        return text
                    except Exception:
                        return ""
            elif 'parts' in part:
                for subpart in part['parts']:
                    result = extract_from_part(subpart)
                    if result:
                        return result
            return ""
        
        # Check if this is a simple text/plain message
        if payload.get('mimeType') == 'text/plain':
            data = payload.get('body', {}).get('data', '')
            if data:
                try:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
                except Exception:
                    pass
        
        # Check if this is a simple text/html message
        elif payload.get('mimeType') == 'text/html':
            data = payload.get('body', {}).get('data', '')
            if data:
                try:
                    html = base64.urlsafe_b64decode(data).decode('utf-8')
                    # Simple HTML to text conversion
                    import re
                    text = re.sub(r'<[^>]+>', '', html)
                    return text
                except Exception:
                    pass
        
        # Check if this is a multipart message
        elif 'parts' in payload:
            for part in payload['parts']:
                result = extract_from_part(part)
                if result:
                    body = result
                    break
        
        return body or payload.get('snippet', '')

    def post_to_slack(self, message_data: Dict[str, Any]) -> bool:
        """Post message to Slack via webhook."""
        try:
            # Create Gmail link
            gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{message_data['thread_id']}"
            
            # Format message
            text = f"📧 New Email: {message_data['subject']}"
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📧 {message_data['subject']}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*From:*\n{message_data['sender']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Date:*\n{message_data['date']}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Query:* `{self.gmail_query}`"
                    }
                }
            ]
            
            # Add body preview
            if message_data['body']:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Preview:*\n```{message_data['body']}```"
                    }
                })
            
            # Add Gmail button
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Open in Gmail"
                        },
                        "url": gmail_link,
                        "action_id": "open_gmail"
                    }
                ]
            })
            
            payload = {
                "text": text,
                "channel": self.slack_channel,
                "username": self.slack_username,
                "blocks": blocks
            }
            
            response = requests.post(self.slack_webhook_url, json=payload)
            
            if response.status_code == 200:
                logger.info("Message posted to Slack successfully")
                return True
            else:
                logger.error(f"Slack API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error posting to Slack: {e}")
            return False

    def start_polling(self):
        """Start the Gmail polling loop."""
        logger.info(f"Starting Gmail polling every {self.poll_interval} seconds")
        while True:
            try:
                self.poll_gmail()
                time.sleep(self.poll_interval)
            except KeyboardInterrupt:
                logger.info("Polling stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(self.poll_interval)

# Initialize the monitor
monitor = GmailSlackMonitor()

# Flask app for health checks
app = Flask(__name__)

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'timezone': monitor.timezone,
        'mode': os.getenv('MODE', 'unknown'),
        'gmail_query': monitor.gmail_query,
        'poll_interval': monitor.poll_interval
    })

def main():
    """Main function to start the service."""
    mode = os.getenv('MODE', 'combined').lower()
    
    if mode == 'server':
        logger.info("Starting in server mode")
        port = int(os.getenv('PORT', '10000'))
        serve(app, host='0.0.0.0', port=port)
    elif mode == 'worker':
        logger.info("Starting in worker mode")
        monitor.start_polling()
    elif mode == 'combined':
        logger.info("Starting in combined mode")
        # Start polling in a separate thread
        polling_thread = threading.Thread(target=monitor.start_polling, daemon=True)
        polling_thread.start()
        
        # Start Flask server in main thread
        port = int(os.getenv('PORT', '10000'))
        serve(app, host='0.0.0.0', port=port)
    else:
        logger.error(f"Unknown mode: {mode}")
        return

if __name__ == '__main__':
    main()
