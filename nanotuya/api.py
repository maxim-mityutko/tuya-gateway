import json
import requests
import logging
from os import environ as env

from nanotuya.cls import auth

DEVICE_URL = "https://openapi.tuya{region}.com/v1.0/devices/{device_id}/{endpoint}"
IR_URL = "https://openapi.tuya{region}.com/v1.0/infrareds/{device_id}/{endpoint}"


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


def _url_format(device_id: str, endpoint: str, url: str = DEVICE_URL) -> str:
    url = url.format(
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


async def get_ir_device_remotes(device_id: str) -> dict:
    """
    Get the list of remotes bound to IR control, including DIY.
    :param device_id: Unique id of the Tuya device (in Tuya's API it is called 'infrared_id')
    :return: Dictionary with with HTTP response.
    """
    response = requests.get(
        url=_url_format(device_id=device_id, endpoint="remotes", url=IR_URL),
        headers=_api_request_headers(),
    )
    _logger(response=response)
    return json.loads(response.content.decode())


async def get_ir_remote_keys(device_id: str, remote_id: str) -> dict:
    """
    Return the list of keys bound to the remote of the IR device, includes both
    natively supported keys and learned keys.
    :param device_id: Unique id of the Tuya device (in Tuya's API it is called 'infrared_id')
    :param remote_id: Unique remote id bound to the IR device, returned by 'get_ir_device_remotes'.
    Returns:
    """
    keys = {}
    base_url = _url_format(device_id=device_id, endpoint='remotes', url=IR_URL)

    # Native keys and learned keys have different endpoints, call both and put the results in one dictionary.
    # If remote does not have any native keys, the response is "code:2010, msg:device not exist".
    # If learned keys do not exist, the response is an empty list.
    response = requests.get(
        url=f"{base_url}/{remote_id}/keys",
        headers=_api_request_headers(),
    )
    _logger(response=response)
    keys["native"] = json.loads(response.content.decode())

    response = requests.get(
        url=f"{base_url}/{remote_id}/learning-codes",
        headers=_api_request_headers(),
    )
    _logger(response=response)
    keys["custom"] = json.loads(response.content.decode())

    return keys


async def post_ir_remote_key(device_id: str, remote_id: str, payload: dict) -> dict:
    base_url = _url_format(device_id=device_id, endpoint='remotes', url=IR_URL)

    # {"code" : <value>} for "custom", {"key": <value>} for "native"
    if payload.get("type", "native") == "custom":
        response = requests.post(
            url=f"{base_url}/{remote_id}/learning-codes",
            headers=_api_request_headers(),
            data=json.dumps(payload),
        )
    else:
        response = requests.post(
            url=f"{base_url}/{remote_id}/command",
            headers=_api_request_headers(),
            data=json.dumps(payload),
        )

    _logger(response=response)
    return json.loads(response.content.decode())


