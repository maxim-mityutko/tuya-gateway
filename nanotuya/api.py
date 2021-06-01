import json
import requests
import logging
from os import environ as env

from nanotuya.cls import auth

DEVICE_URL = "https://openapi.tuya{region}.com/v1.0/devices/{id}/{endpoint}"    # id = device_id
IR_URL = "https://openapi.tuya{region}.com/v1.0/infrareds/{id}/{endpoint}"      # id = infrared_id
USER_URL = "https://openapi.tuya{region}.com/v1.0/users/{id}/{endpoint}"        # id = uid (user_id)
HOME_URL = "https://openapi.tuya{region}.com/v1.0/homes/{id}/{endpoint}"        # id = home_id


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


def _url_format(id: str, endpoint: str, url: str = DEVICE_URL) -> str:
    url = url.format(
        region=env.get("TUYA_REGION"),
        id=id,
        endpoint=endpoint,
    )

    return url


def _request(url: str, payload: dict = None, method: str = None):
    response = None
    if payload or method == "post":
        response = requests.post(
            url=url,
            headers=_api_request_headers(),
            data=json.dumps(payload),
        )
    elif not payload:
        response = requests.get(
            url=url,
            headers=_api_request_headers()
        )

    _logger(response=response)
    return json.loads(response.content.decode())


async def get_device_functions(device_id: str) -> dict:
    """
    Get the list of available device functions based on its ID.
    :param device_id: Unique id of the Tuya device
    :return: Dictionary with HTTP response
    """
    url = _url_format(id=device_id, endpoint="functions", url=DEVICE_URL)
    response = _request(url=url)
    return response


async def get_device_status(device_id: str):
    """
    Get status of the device based on its ID.
    :param device_id: Unique id of the Tuya device
    :return: Dictionary with HTTP response
    """
    url = _url_format(id=device_id, endpoint="status", url=DEVICE_URL)
    response = _request(url=url)
    return response


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
    url = _url_format(id=device_id, endpoint="commands", url=DEVICE_URL)
    response = _request(url=url, payload=payload)
    return response


async def get_ir_device_remotes(device_id: str) -> dict:
    """
    Get the list of remotes bound to IR control, including DIY.
    :param device_id: Unique id of the Tuya device (in Tuya's API it is called 'infrared_id')
    :return: Dictionary with with HTTP response.
    """
    url = _url_format(id=device_id, endpoint="remotes", url=IR_URL)
    response = _request(url=url)
    return response


async def get_ir_remote_keys(device_id: str, remote_id: str) -> dict:
    """
    Return the list of keys bound to the remote of the IR device, includes both
    natively supported keys and learned keys.
    :param device_id: Unique id of the Tuya device (in Tuya's API it is called 'infrared_id')
    :param remote_id: Unique remote id bound to the IR device, returned by 'get_ir_device_remotes'.
    :return: Dictionary with HTTP response
    """
    keys = {}
    url = _url_format(id=device_id, endpoint='remotes', url=IR_URL)

    # Native keys and learned keys have different endpoints, call both and put the results in one dictionary.
    # If remote does not have any native keys, the response is "code:2010, msg:device not exist".
    # If learned keys do not exist, the response is an empty list.

    k_url = f"{url}/{remote_id}/keys"
    keys["native"] = _request(url=k_url)

    lc_url = f"{url}/{remote_id}/learning-codes"
    keys["custom"] = _request(url=lc_url)

    return keys


async def post_ir_remote_key(device_id: str, remote_id: str, payload: dict) -> dict:
    # fmt: off
    """
    Trigger key / code on the remote bound to IR device. There are 2 types of keys on Tuya IR
    devices:
        * native - out of the box keys, provided with remotes for different brands
        * custom - DIY keys learned by the IR device

    Body for "custom" key (e.g. DIY):
        {
            "type": "custom",
            "code": "<value>"
        }
    Body for "native" key:
        {
            "type": "custom",
            "key": "<value>"
        }

    :param device_id: Unique id of the Tuya device (in Tuya's API it is called 'infrared_id')
    :param remote_id: Unique remote id bound to the IR device, returned by 'get_ir_device_remotes'.
    :param payload: Request body in JSON format
    :return: Dictionary with HTTP response
    """
    url = _url_format(id=device_id, endpoint='remotes', url=IR_URL)

    # {"code" : <value>} for "custom", {"key": <value>} for "native"
    if payload.get("type", "native") == "custom":
        lc_url = f"{url}/{remote_id}/learning-codes"
        response = _request(url=lc_url, payload=payload)
    else:
        k_url = f"{url}/{remote_id}/command"
        response = _request(url=k_url, payload=payload)

    return response


async def get_homes(user_id: str) -> dict:
    """
    Get list of homes where user has access.
    :param user_id: ID of the user (can be obtained from Tuya IoT portal).
    :return: Dictionary with with HTTP response.
    """
    url = _url_format(id=user_id, endpoint='homes', url=USER_URL)
    response = _request(url=url)
    return response


async def get_scenes(home_id: str) -> dict:
    """
    Get list of scenes created in home.
    :param home_id: ID of the home (user who is used to "Link Devices by App Account" should be a "Home Owner")
    :return: Dictionary with with HTTP response.
    """
    url = _url_format(id=home_id, endpoint='scenes', url=HOME_URL)
    response = _request(url=url)
    return response


async def post_trigger_scene(home_id: str, scene_id: str) -> dict:
    """
    Trigger scene
    :param home_id: ID of the home (user who is used to "Link Devices by App Account" should be a "Home Owner")
    :param scene_id: Scene ID within Tuya App.
    :return: Dictionary with with HTTP response.
    """
    url = _url_format(id=home_id, endpoint='scenes', url=HOME_URL)
    response = _request(url=f"{url}/{scene_id}/trigger", method="post")
    return response
