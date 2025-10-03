#!/usr/bin/env python3
"""
One-time script to clear the processed messages database for a fresh sweep.
This will allow all emails to be processed again for the new Slack channel.
"""

import sqlite3
import os

def clear_database():
    """Clear all processed message records from the database."""
    try:
        if os.path.exists('state.db'):
            conn = sqlite3.connect('state.db')
            cursor = conn.cursor()
            
            # Get count before clearing
            cursor.execute('SELECT COUNT(*) FROM processed')
            count_before = cursor.fetchone()[0]
            
            # Clear all processed records
            cursor.execute('DELETE FROM processed')
            conn.commit()
            
            # Get count after clearing
            cursor.execute('SELECT COUNT(*) FROM processed')
            count_after = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"✅ Database cleared successfully!")
            print(f"   Records before: {count_before}")
            print(f"   Records after: {count_after}")
            print(f"   Ready for fresh sweep!")
            
        else:
            print("ℹ️  No database file found - will be created on first run")
            
    except Exception as e:
        print(f"❌ Error clearing database: {e}")

if __name__ == "__main__":
    print("🗑️  Clearing processed messages database...")
    clear_database()
    print("\n📋 Next steps:")
    print("1. Update your Render GMAIL_QUERY to: after:2025/10/1")
    print("2. Redeploy your service")
    print("3. Monitor the logs for the sweep")
    print("4. Once confirmed, update to new Slack webhook")
    print("5. Change GMAIL_QUERY back to: newer_than:7d")
