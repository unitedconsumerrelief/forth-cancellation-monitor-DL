#!/usr/bin/env python3
"""
Test script to send a Slack message with real body content from Gmail.
This will show us exactly what's being sent to Slack.
"""

import requests
import json
from datetime import datetime
import pytz

def create_real_message_with_body():
    """Create a message with real body content from the debug output."""
    # Get current time in Manila timezone
    tz = pytz.timezone('Asia/Manila')
    current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
    
    return {
        'id': '199584836f839251',
        'subject': 'A Client Has Cancelled - 1137007417',
        'sender': 'noreply@forthcrm.com',
        'date': current_time,
        'body': '''A client has been cancelled. Date: Sep 17, 2025 Company: United Consumer Relief Client Name: arturo orozco Record ID: 1137007417 Reason: {CANCELLED_REASON}Notes: {CANCELLED_NOTES} Agent: Tomas Londono https://client.forthcrm.com/''',
        'thread_id': 'thread_1137007417',
        'snippet': 'A client has been cancelled. Date: Sep 17, 2025 Company: United Consumer Relief Client Name: arturo orozco Record ID: 1137007417 Reason: {CANCELLED_REASON} Notes: {CANCELLED_NOTES} Agent: Tomas Londono'
    }

def create_slack_payload(message_data, gmail_query="from:noreply@forthcrm.com (subject:\"Cancellation\" OR subject:\"Cancel\" OR subject:\"cancelled\" OR subject:\"cancelled\") newer_than:7d"):
    """Create the Slack payload with real body content."""
    
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
    
    # Add body preview with the real content
    if message_data['body']:
        # Format the body for better readability
        formatted_body = message_data['body'].replace('{CANCELLED_REASON}', 'N/A').replace('{CANCELLED_NOTES}', 'N/A')
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Cancellation Details:*\n```{formatted_body}```"
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
    """Send a test message with real body content to Slack."""
    
    # Your webhook URL
    webhook_url = "YOUR_WEBHOOK_URL_HERE"
    
    print("🧪 Testing Slack Message with Real Body Content")
    print("=" * 50)
    
    # Create real message with body
    real_message = create_real_message_with_body()
    
    print("📧 Message Details:")
    print(f"   Subject: {real_message['subject']}")
    print(f"   From: {real_message['sender']}")
    print(f"   Body Length: {len(real_message['body'])} characters")
    print(f"   Body Preview: {real_message['body'][:100]}...")
    print()
    
    # Create Slack payload
    payload = create_slack_payload(real_message)
    
    print("🔧 Slack Payload Structure:")
    print(f"   Blocks: {len(payload['blocks'])}")
    for i, block in enumerate(payload['blocks']):
        print(f"   Block {i+1}: {block['type']}")
        if block['type'] == 'section' and 'text' in block:
            text_preview = block['text']['text'][:100] + "..." if len(block['text']['text']) > 100 else block['text']['text']
            print(f"     Text: {text_preview}")
    print()
    
    try:
        print("🚀 Sending test message to Slack...")
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ SUCCESS! Test message sent to Slack")
            print("📱 Check your #forth-alerts channel to see the message with body content")
            print()
            print("🎉 This should now show the full cancellation details!")
        else:
            print(f"❌ FAILED! HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def main():
    """Main function."""
    print("🔔 Test Slack Message with Real Body Content")
    print("This will send a message with the actual cancellation details\n")
    
    # Ask for confirmation
    confirm = input("Send test message with real body content to #forth-alerts? (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        send_test_message()
    else:
        print("❌ Test cancelled")

if __name__ == "__main__":
    main()
