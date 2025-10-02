#!/usr/bin/env python3
"""
Test script to send a REAL Slack message with the actual Forth CRM cancellation details
from the screenshot you provided. This will show you exactly how it will look.
"""

import requests
import json
from datetime import datetime
import pytz

def create_real_forth_cancellation_message():
    """Create the exact message from your screenshot."""
    # Get current time in Manila timezone
    tz = pytz.timezone('Asia/Manila')
    current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
    
    return {
        'id': 'forth_cancellation_1131643818',
        'subject': 'A Client Has Cancelled - 1131643818',
        'sender': 'noreply@forthcrm.com',
        'date': current_time,
        'body': '''A client has been cancelled.

Date: Sep 16, 2025
Company: United Consumer Relief
Client Name: Carlos Bogaert
Record ID: 1131643818
Reason: {CANCELLED_REASON}
Notes: {CANCELLED_NOTES}
Agent: Valentina Castano

Link: https://login.forthcrm.com/''',
        'thread_id': 'thread_1131643818',
        'snippet': 'A client has been cancelled. Date: Sep 16, 2025 Company: United Consumer Relief...'
    }

def create_slack_payload(message_data, gmail_query="from:noreply@forthcrm.com (subject:\"Cancellation\" OR subject:\"Cancel\" OR subject:\"cancelled\" OR subject:\"cancelled\") newer_than:7d"):
    """Create the Slack payload for the real Forth cancellation email."""
    
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
                "text": f"*Query:* `{gmail_query}`"
            }
        }
    ]
    
    # Add body preview with the exact details from your screenshot
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
        "channel": "forth-alerts",
        "username": "Gmail Monitor",
        "text": text,
        "blocks": blocks
    }
    
    return payload

def send_real_test_message():
    """Send the real Forth cancellation message to Slack."""
    
    # Your webhook URL
    webhook_url = "YOUR_WEBHOOK_URL_HERE"
    
    print("🧪 Testing REAL Forth CRM Cancellation Email")
    print("=" * 50)
    print("📧 Using actual data from your screenshot:")
    print("   • Subject: A Client Has Cancelled - 1131643818")
    print("   • From: noreply@forthcrm.com")
    print("   • Company: United Consumer Relief")
    print("   • Client: Carlos Bogaert")
    print("   • Agent: Valentina Castano")
    print("   • Record ID: 1131643818")
    print()
    
    # Create real message
    real_message = create_real_forth_cancellation_message()
    
    # Create Slack payload
    payload = create_slack_payload(real_message)
    
    try:
        print("🚀 Sending REAL Forth cancellation message to Slack...")
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ SUCCESS! Real Forth cancellation message sent to Slack")
            print("📱 Check your #forth-alerts channel to see the actual message")
            print()
            print("🎉 This is exactly how your Forth CRM cancellation emails will look!")
            print("   • Real client data from your screenshot")
            print("   • Proper formatting with all details")
            print("   • Gmail link for easy access")
            print("   • Only cancellation emails will be sent")
        else:
            print(f"❌ FAILED! HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR!")
        print("   • Check your internet connection")
        print("   • Verify the webhook URL is accessible")
        
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT ERROR!")
        print("   • The request took too long")
        print("   • Try again in a moment")
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

def main():
    """Main function."""
    print("🔔 REAL Forth CRM Cancellation Email Test")
    print("This will send a message with the EXACT data from your screenshot\n")
    
    # Ask for confirmation
    confirm = input("Send REAL Forth cancellation message to #forth-alerts? (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        send_real_test_message()
    else:
        print("❌ Test cancelled")
        print("Run this script again when you're ready to see the real message")

if __name__ == "__main__":
    main()
