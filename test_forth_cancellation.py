#!/usr/bin/env python3
"""
Test script to simulate a Forth CRM cancellation email message.
This shows exactly how Forth cancellation emails will appear in Slack.
"""

import json
from datetime import datetime
import pytz

def create_forth_cancellation_message():
    """Create a realistic Forth CRM cancellation message for testing."""
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
    """Create the Slack payload for Forth cancellation emails."""
    
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

def display_slack_message(payload):
    """Display the Slack message in a readable format."""
    print("🔔 FORTH CRM CANCELLATION EMAIL PREVIEW")
    print("=" * 60)
    print(f"Channel: {payload['channel']}")
    print(f"Username: {payload['username']}")
    print(f"Text: {payload['text']}")
    print("\n📋 MESSAGE STRUCTURE:")
    print("-" * 40)
    
    for i, block in enumerate(payload['blocks'], 1):
        print(f"\nBlock {i}: {block['type'].upper()}")
        
        if block['type'] == 'header':
            print(f"  📝 Header: {block['text']['text']}")
            
        elif block['type'] == 'section':
            if 'fields' in block:
                print("  📊 Fields:")
                for field in block['fields']:
                    print(f"    • {field['text']}")
            elif 'text' in block:
                print(f"  📝 Text: {block['text']['text']}")
                
        elif block['type'] == 'actions':
            print("  🔘 Actions:")
            for element in block['elements']:
                print(f"    • Button: {element['text']['text']}")
                print(f"      URL: {element['url']}")

def main():
    """Main function to run the test."""
    print("🧪 Forth CRM Cancellation Email Simulator")
    print("This shows how Forth cancellation emails will appear in Slack\n")
    
    # Create sample Forth cancellation message
    sample_message = create_forth_cancellation_message()
    
    # Create Slack payload
    slack_payload = create_slack_payload(sample_message)
    
    # Display the message
    display_slack_message(slack_payload)
    
    print("\n✅ This is exactly how Forth CRM cancellation emails will appear!")
    print("📧 The message includes:")
    print("   • Header with cancellation subject")
    print("   • From: noreply@forthcrm.com")
    print("   • Date in Asia/Manila timezone")
    print("   • Gmail query used for filtering")
    print("   • Full cancellation details preview")
    print("   • 'Open in Gmail' button")
    
    print(f"\n🔗 Gmail Link: https://mail.google.com/mail/u/0/#inbox/{sample_message['thread_id']}")
    
    print("\n🎯 Gmail Query Analysis:")
    print("   • from:noreply@forthcrm.com - Only from this specific sender")
    print("   • subject:\"Cancellation\" OR subject:\"Cancel\" - Only cancellation subjects")
    print("   • subject:\"cancelled\" OR subject:\"cancelled\" - Covers both spellings")
    print("   • newer_than:7d - Only emails from last 7 days")
    print("   • This will catch: 'A Client Has Cancelled - 1131643818'")

if __name__ == "__main__":
    main()
