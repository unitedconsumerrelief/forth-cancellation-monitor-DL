#!/usr/bin/env python3
"""
Simple test script to verify the health endpoint works.
Run this after starting the server in MODE=server
"""

import requests
import json
import sys

def test_health_endpoint(url="http://localhost:10000"):
    """Test the health endpoint."""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        response.raise_for_status()
        
        data = response.json()
        print("✅ Health check passed!")
        print(f"Status: {data.get('ok', False)}")
        print(f"Time: {data.get('time', 'Unknown')}")
        print(f"Timezone: {data.get('timezone', 'Unknown')}")
        print(f"Mode: {data.get('mode', 'Unknown')}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Is the server running?")
        print("Start with: MODE=server python app.py")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:10000"
    print(f"Testing health endpoint at {url}/health")
    success = test_health_endpoint(url)
    sys.exit(0 if success else 1)

