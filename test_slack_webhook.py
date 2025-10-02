#!/usr/bin/env python3
"""
Test script to send an actual test message to your Slack webhook.
This verifies that your webhook URL is working correctly.
"""

import requests
import json
import os
from datetime import datetime
import pytz

def create_test_message():
    """Create a test message for Slack."""
    # Get current time in Manila timezone
    tz = pytz.timezone('Asia/Manila')
    current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
    
    return {
        'id': 'test_message_' + str(int(datetime.now().timestamp())),
        'subject': '🧪 Test Message - Gmail Monitor Setup',
        'sender': 'test@forth.com',
        'date': current_time,
        'body': 'This is a test message from the Gmail → Slack Monitor setup. If you can see this message, your webhook is working correctly!\n\n✅ Slack webhook: Working\n✅ Message formatting: Working\n✅ Gmail query: from:noreply@forthcrm.com (subject:"Cancellation" OR subject:"Cancel" OR subject:"cancelled" OR subject:"cancelled") newer_than:7d\n\nYou can now proceed with the full deployment.',
        'thread_id': 'test_thread_123',
        'snippet': 'This is a test message from the Gmail → Slack Monitor setup...'
    }

def create_slack_payload(message_data, gmail_query="from:noreply@forthcrm.com (subject:\"Cancellation\" OR subject:\"Cancel\" OR subject:\"cancelled\" OR subject:\"cancelled\") newer_than:7d"):
    """Create the Slack payload."""
    
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
        "channel": "forth-alerts",
        "username": "Gmail Monitor",
        "text": text,
        "blocks": blocks
    }
    
    return payload

def send_test_message():
    """Send a test message to Slack."""
    
    # Your webhook URL
    webhook_url = "YOUR_WEBHOOK_URL_HERE"
    
    print("🧪 Testing Slack Webhook")
    print("=" * 40)
    print(f"Webhook URL: {webhook_url}")
    print(f"Target Channel: forth-alerts")
    print()
    
    # Create test message
    test_message = create_test_message()
    print("📧 Test Message Created:")
    print(f"   Subject: {test_message['subject']}")
    print(f"   From: {test_message['sender']}")
    print(f"   Date: {test_message['date']}")
    print()
    
    # Create Slack payload
    payload = create_slack_payload(test_message)
    
    try:
        print("🚀 Sending test message to Slack...")
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ SUCCESS! Test message sent to Slack")
            print("📱 Check your #forth-alerts channel to see the message")
            print()
            print("🎉 Your Slack webhook is working correctly!")
            print("   You can now proceed with the full Gmail monitoring setup.")
        else:
            print(f"❌ FAILED! HTTP {response.status_code}")
            print(f"Response: {response.text}")
            print()
            print("🔧 Troubleshooting:")
            print("   • Check your webhook URL is correct")
            print("   • Verify the Slack app has permission to post to #forth-alerts")
            print("   • Make sure the channel exists and the bot is added")
            
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
    print("🔔 Gmail → Slack Webhook Tester")
    print("This will send a test message to your Slack channel\n")
    
    # Ask for confirmation
    confirm = input("Do you want to send a test message to #forth-alerts? (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        send_test_message()
    else:
        print("❌ Test cancelled")
        print("Run this script again when you're ready to test")

if __name__ == "__main__":
    main()

