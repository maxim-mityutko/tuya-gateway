import time
import json
import hmac
import hashlib
import requests


class TuyaAuth:
    """
    Class:          TuyaAuth
    Description:    Inspired by 'tinytuya' implementation by Jason A. Cox
                    For more information see https://github.com/jasonacox/tinytuya
    """
    def __init__(
        self,
        region: str,
        client_id: str,
        client_secret: str,
        token: str = None
    ):
        self.region = region
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = token
        self.headers = None

    @staticmethod
    def _now():
        return str(int(time.time() * 1000))

    def _sign_payload(self):
        if not self.token:
            payload = f"{self.client_id}{self._now()}"
        else:
            payload = f"{self.client_id}{self.token}{self._now()}"

        # Sign Payload
        signature = hmac.new(
            self.client_secret.encode("utf-8"),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest().upper()

        # Create Header Data
        headers = {
            "client_id": self.client_id,
            "sign_method": "HMAC-SHA256",
            't': self._now(),
            'sign': signature
        }

        if self.token:
            headers["access_token"] = self.token

        self.headers = headers

    def authenticate(self):
        """Tuya IoT Platform Data Access
        Parameters:
            * region     Tuya API Server Region: us, eu, cn, in
            * apiKey     Tuya Platform Developer ID
            * apiSecret  Tuya Platform Developer secret
            * uri        Tuya Platform URI for this call
            * token      Tuya OAuth Token
        Playload Construction - Header Data:
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
        URIs:
            * Get Token = https://openapi.tuyaus.com/v1.0/token?grant_type=1
            * Get UserID = https://openapi.tuyaus.com/v1.0/devices/{DeviceID}
            * Get Devices = https://openapi.tuyaus.com/v1.0/users/{UserID}/devices
        """
        url = f"https://openapi.tuya{self.region}.com/v1.0/token?grant_type=1"

        # Get Token
        self._sign_payload()
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            response_dict = json.loads(response.content.decode())
            self.token = response_dict.get("result", {}).get("access_token")
        else:
            response_dict = None
        return response_dict

    def sign(self):
        # If token is known, update 'headers'
        if self.token:
            # Refresh headers
            self._sign_payload()
            return self.headers
        else:
            # TODO: call logger
            pass


