import time
import requests

SERVER_URL = "http://127.0.0.1:8000/move"

payload = {
    "pgn": "",
    "possible_moves": ["e2e4", "d2d4", "g1f3", "b1c3"],
    "context": "Player vs Agent game. It's your turn."
}

def wait_for_server(url, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # check root or just try the endpoint
            # Since we don't know if root / exists, we'll try connection
            requests.get("http://127.0.0.1:8000/docs", timeout=1)
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            print("Waiting for server...")
    return False

print("Waiting for server to be ready...")
if wait_for_server(SERVER_URL):
    print("Server is ready.")
    try:
        response = requests.post(SERVER_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code != 200:
            print("Request failed.")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Server failed to start within timeout.")
