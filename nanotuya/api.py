import json
import requests
from os import environ as env

from nanotuya.cls import auth

URL = "https://openapi.tuya{region}.com/v1.0/devices/{device_id}/{endpoint}"


def _api_request_headers() -> dict:
    tuya_auth = auth.TuyaAuth(
        region=env.get("TUYA_REGION"),
        client_id=env.get("TUYA_CLIENT_ID"),
        client_secret=env.get("TUYA_CLIENT_SECRET"),
        token=env.get("TUYA_TOKEN"),
    )
    if not tuya_auth.token:
        tuya_auth.authenticate()
        env["TUYA_TOKEN"] = tuya_auth.token

    tuya_auth.sign()
    return tuya_auth.headers


def _url_format(device_id: str, endpoint: str) -> str:
    url = URL.format(
        region=env.get('TUYA_REGION'),
        device_id=device_id,
        endpoint=endpoint,
    )
    return url


def get_device_functions(device_id: str) -> dict:
    """
    Get the list of available device functions based on its ID.
    :param device_id: Unique id of the Tuya device
    :return: Dictionary with HTTP response
    """
    response = requests.get(
        url=_url_format(device_id=device_id, endpoint="functions"),
        headers=_api_request_headers()
    )
    return json.loads(response.content.decode())


def get_device_status(device_id: str):
    """
    Get status of the device based on its ID.
    :param device_id: Unique id of the Tuya device
    :return: Dictionary with HTTP response
    """
    response = requests.get(
        url=_url_format(device_id=device_id, endpoint="status"),
        headers=_api_request_headers()
    )
    return json.loads(response.content.decode())


def post_device_commands(device_id: str, payload: dict) -> dict:
    """
    Send dictionary of commands to specific device in the request body.
    Body:
        {
            "commands": [
                {"code": "bright_value", "value": 125}
            ]
        }
    :param device_id: Unique id of the Tuya device
    :param payload: Request body in JSON format
    :return: Dictionary with HTTP response
    """
    response = requests.post(
        url=_url_format(device_id=device_id, endpoint="commands"),
        headers=_api_request_headers(),
        data=json.dumps(payload)
    )

    return json.loads(response.content.decode())
