from tuyagw import auth
import requests
import json

CLIENT_ID = "xxxxx"
CLIENT_SECRET = "XXXXXXXXXX"
DEVICE_ID = "abcd"

def get_device():
    ta = auth.TuyaAuth(
        region="eu",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    ta.authenticate()
    ta.sign()
    url = f"https://openapi.tuyaeu.com/v1.0/devices/{DEVICE_ID}/status"

    response = requests.get(url, headers=ta.headers)
    return response.content.decode()


def set_device():
    ta = auth.TuyaAuth(
        region="eu",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    ta.authenticate()
    ta.sign()

    url = f"https://openapi.tuyaeu.com/v1.0/devices/{DEVICE_ID}/commands"
    data = {
        "commands": [
            {"code": "bright_value", "value": 75}
        ]
    }
    response = requests.post(url, headers=ta.headers, data=json.dumps(data))
    return response.content.decode()