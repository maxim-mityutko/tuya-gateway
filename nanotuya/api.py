import json
import requests
import logging
from os import environ as env

from nanotuya.cls import auth

URL = "https://openapi.tuya{region}.com/v1.0/devices/{device_id}/{endpoint}"


def _logger(response: requests.Response):
    logger = logging.getLogger(__name__)
    logger.debug(f"Response status code: ({response.status_code})")
    logger.debug(f"Response content: {response.content.decode()}")


def _api_request_headers() -> dict:
    tuya_auth = auth.TuyaAuth(
        region=env.get("TUYA_REGION"),
        client_id=env.get("TUYA_CLIENT_ID"),
        client_secret=env.get("TUYA_CLIENT_SECRET"),
    )

    return tuya_auth.headers


def _url_format(device_id: str, endpoint: str) -> str:
    url = URL.format(
        region=env.get("TUYA_REGION"),
        device_id=device_id,
        endpoint=endpoint,
    )

    return url


async def get_device_functions(device_id: str) -> dict:
    """
    Get the list of available device functions based on its ID.
    :param device_id: Unique id of the Tuya device
    :return: Dictionary with HTTP response
    """
    response = requests.get(
        url=_url_format(device_id=device_id, endpoint="functions"),
        headers=_api_request_headers(),
    )
    _logger(response=response)
    return json.loads(response.content.decode())


async def get_device_status(device_id: str):
    """
    Get status of the device based on its ID.
    :param device_id: Unique id of the Tuya device
    :return: Dictionary with HTTP response
    """
    response = requests.get(
        url=_url_format(device_id=device_id, endpoint="status"),
        headers=_api_request_headers(),
    )
    _logger(response=response)
    return json.loads(response.content.decode())


async def post_device_commands(device_id: str, payload: dict) -> dict:
    # fmt: off
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
    # fmt: on
    response = requests.post(
        url=_url_format(device_id=device_id, endpoint="commands"),
        headers=_api_request_headers(),
        data=json.dumps(payload),
    )
    _logger(response=response)
    return json.loads(response.content.decode())
