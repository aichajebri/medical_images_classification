import requests
import sys
import time

BASE_URL = "http://localhost:8000"

def wait_for_backend(url, retries=5, delay=2):
    print(f"Waiting for backend at {url}...")
    for i in range(retries):
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 200:
                print("Backend is up!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        print(f"Retry {i+1}/{retries}...")
        time.sleep(delay)
    print("Backend failed to start.")
    return False

def test_cors():
    print("\nTesting CORS...")
    # Test OPTIONS request for CORS headers
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
    }
    try:
        response = requests.options(f"{BASE_URL}/api/predict", headers=headers)
        print(f"OPTIONS Status: {response.status_code}")
        
        allow_origin = response.headers.get("access-control-allow-origin")
        print(f"Access-Control-Allow-Origin: {allow_origin}")
        
        if allow_origin == "http://localhost:3000":
            print("CORS Verification Passed!")
            return True
        else:
            print(f"CORS Verification Failed. Expected 'http://localhost:3000', got '{allow_origin}'")
            return False
    except Exception as e:
        print(f"CORS Test Failed with error: {e}")
        return False

if __name__ == "__main__":
    if not wait_for_backend(BASE_URL):
        sys.exit(1)
    
    if not test_cors():
        sys.exit(1)
    
    print("\nAll Backend Tests Passed!")
