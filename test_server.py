import requests

SERVER_URL = "http://localhost:8000/move"

payload = {
    "pgn": "",
    "possible_moves": ["e2e4", "d2d4", "g1f3", "b1c3"],
    "context": "Player vs Agent game. It's your turn."
}

try:
    response = requests.post(SERVER_URL, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
