import requests
import time
import sys

def test_workflow():
    url = "http://localhost:5000/execute/ai_assistant"
    payload = {
        "instruction": "Test instruction from verification script"
    }
    headers = {
        "X-API-Key": "test-key" # Assuming we set this env var or run locally
    }
    
    # We need to set COMET_API_KEY env var when running backend, 
    # but for localhost requests backend.py skips auth check if 127.0.0.1
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            task_id = response.json().get('task_id')
            print(f"Task ID: {task_id}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Request failed: {e}")
        return False

if __name__ == "__main__":
    if test_workflow():
        print("✓ Workflow submission test passed")
    else:
        print("✗ Workflow submission test failed")
