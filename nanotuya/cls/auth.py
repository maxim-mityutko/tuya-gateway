import time
import json
import hmac
import hashlib
import requests
import logging
from os import environ as env


class TuyaAuth:
    # fmt: off
    """
    Class:          TuyaAuth
    Description:    Inspired by 'tinytuya' implementation by Jason A. Cox
                    For more information see https://github.com/jasonacox/tinytuya

    Tuya IoT Platform Data Access
    Parameters:
        * region     Tuya API Server Region: us, eu, cn, in
        * apiKey     Tuya Platform Developer ID
        * apiSecret  Tuya Platform Developer secret
        * uri        Tuya Platform URI for this call
        * token      Tuya OAuth Token
    Payload Construction - Header Data:
        Parameter 	  Type    Required	Description
        client_id	  String     Yes	client_id
        signature     String     Yes	HMAC-SHA256 Signature (see below)
        sign_method	  String	 Yes	Message-Digest Algorithm of the signature: HMAC-SHA256.
        t	          Long	     Yes	13-bit standard timestamp (now in milliseconds).
        lang	      String	 No	    Language. It is zh by default in China and en in other areas.
        access_token  String     *      Required for service management calls
    Signature Details:
        * OAuth Token Request: signature = HMAC-SHA256(KEY + t, SECRET).toUpperCase()
        * Service Management: signature = HMAC-SHA256(KEY + access_token + t, SECRET).toUpperCase()
    URI:
        * Get Token = https://openapi.tuyaus.com/v1.0/token?grant_type=1
    """
    # fmt: on
    def __init__(
        self,
        region: str,
        client_id: str,
        client_secret: str,
    ):
        self.region = region
        self.client_id = client_id
        self.client_secret = client_secret

        self.token = None
        self.refresh_token = None
        self.token_expire = 0
        self.auth_time = 0

        self.headers = None

        self._auth_file = "/tmp/tuya-gateway.json"
        self._uri = f"https://openapi.tuya{self.region}.com/v1.0"

        self._logger = self._get_logger()

        # Restore last authorisation details
        self._parse_auth_response(auth_response=self._load_auth())

        if not self.token:
            self._logger.warning("No token, starting authentication...")
            self._authenticate()
        elif self.auth_time + self.token_expire * 1000 <= int(self._now()):
            self._logger.warning("Token expired, refreshing...")
            self._authenticate(is_refresh=True)
        elif self.token:  # If token is known, update 'headers'
            self._logger.info("Valid token found. Updating headers...")

        self._set_headers()

    @staticmethod
    def _now():
        return str(int(time.time() * 1000))

    @staticmethod
    def _get_logger():
        if 'LOGGING_LEVEL' in env:
            level = logging.getLevelName(env['LOGGING_LEVEL'])
        else:
            level = logging.INFO

        logging.basicConfig(
            level=level, format='%(levelname)-7s %(name)-22s %(message)s', style='%'
        )
        return logging.getLogger(__name__)

    def _save_auth(self, auth_response: dict):
        self._logger.info(f"Saving authentication details to '{self._auth_file}'...")
        with open(self._auth_file, "w") as f:
            json.dump(auth_response, f)

    def _load_auth(self):
        self._logger.info(f"Loading authentication details from '{self._auth_file}'...")
        try:
            with open(self._auth_file) as f:
                auth_response = json.load(f)
        except FileNotFoundError:
            self._logger.warning("Authentication details file is not available!")
            auth_response = None

        return auth_response

    def _parse_auth_response(self, auth_response: dict):
        if auth_response:
            self.auth_time = auth_response.get("t")

            result_dict = auth_response.get("result", {})
            self.token = result_dict.get("access_token")
            self.token_expire = result_dict.get("expire_time")
            self.refresh_token = result_dict.get("refresh_token")

    def _set_headers(self):
        if not self.token:
            payload = f"{self.client_id}{self._now()}"
        else:
            payload = f"{self.client_id}{self.token}{self._now()}"

        # Sign Payload
        signature = (
            hmac.new(
                self.client_secret.encode("utf-8"),
                msg=payload.encode("utf-8"),
                digestmod=hashlib.sha256,
            )
            .hexdigest()
            .upper()
        )

        # Create Header Data
        headers = {
            "client_id": self.client_id,
            "sign_method": "HMAC-SHA256",
            "t": self._now(),
            "sign": signature,
        }

        if self.token:
            headers["access_token"] = self.token

        self._logger.debug(f"Headers: {headers}")
        self.headers = headers

    def _authenticate(self, is_refresh: bool = False):
        if is_refresh is True:
            url = f"{self._uri}/token/{self.refresh_token}"
            self.token = None
        else:
            url = f"{self._uri}/token?grant_type=1"

        # Get Token
        self._set_headers()

        response = requests.get(url, headers=self.headers)
        self._logger.debug(f"Auth response: {response} {response.content.decode()}")

        if response.status_code == 200:
            response_dict = json.loads(response.content.decode())
            self._parse_auth_response(auth_response=response_dict)
            self._save_auth(auth_response=response_dict)
        else:
            response_dict = None

        return response_dict
