# Tuya (Smart Life) Gateway
## Why? 

Recently I bought a bunch of *Flic* buttons to interact with my smart home devices. Unfortunately they lack *Smart Life*
integration and the work around is to use *IFTT*. Recently though *IFTT* introduced payed plan and free accounts
were left with the maximum of 3 actions. Considering that each button has also 3 possible actions: click, double click 
and hold, I would need a separate *IFTT* account for each button (what?!) or a paid subscription (no way!).

Luckily *Flic* supports sending HTTP requests, and this project is to facilitate this and act like a middle man
between the buttons and Tuya.

My goal was to make it as lightweight as possible, hence the following functionality:
* authenticate with Tuya IoT via OAuth2
* get device status
* get device functions
* send commands to the device in the HTML body (this means that those should be correctly formatted JSON, more below)

## Setup
1. Register at https://iot.tuya.com/
2. Go to *Cloud* -- *Project* -- *Create*
3. Set your "Project Name", "Description" and appropriate "Industry"
4. Go to *Cloud* -- *API Group* and apply the following groups:
    * Authorization Management
    * Device Control
    * Device Management
5. Go to *Cloud* -- *Linked Device* -- *Linked Devices by App Account* -- *Add App Account*
6. Scan the QR code with you *Smart Life* app (*Me* -- *upper right corner*) and confirm link
7. The `device_id` that is used in the API can be found on *Device List* tab (make sure to select correct region) or
in device details in *Smart Life* app
8. Go to newly created project page, where "Client ID" and "Client Secret" are available. Add environment variables on 
your machine (for development purposes) or add them to `secrets.env` file (they will be applied to the docker image 
during build).

    * LOGGING_LEVEL = WARNING
    * TUYA_REGION = us / eu / cn / in
    * TUYA_CLIENT_ID
    * TUYA_CLIENT_SECRET

## API
The following methods are available through the gateway:
* Status    (GET):  http://host:65080/api/v1/device/status?device_id=xxxxxxx
* Functions (GET):  http://host:65080/api/v1/device/functions?device_id=xxxxxxx
* Commands  (POST): http://host:65080/api/v1/device/commands?device_id=xxxxxxx

In order to figure out what commands are supported by the device, call `functions` endpoint with the desired
`device_id`. The response will look like this:
```json
{
  "result": {
    "category": "dj",
    "functions": [
      {
        "code": "switch_led",
        "desc": "[\u706f\u5177]\u5f00\u5173",
        "name": "\u5f00\u5173",
        "type": "Boolean",
        "values": "{}"
      },
      {
        "code": "bright_value",
        "desc": "[\u706f\u5177]\u4eae\u5ea6",
        "name": "\u4eae\u5ea6",
        "type": "Integer",
        "values": "{\"min\":25,\"scale\":0,\"unit\":\"\",\"max\":255,\"step\":1}"
      }
    ]
  }
}
```
In order to send command to the device, send the POST request to `commands` endpoint with the following:
* Headers: `Content-Type: application/json`
* Body: 
    * Turn device off:
        ```json
        
        {
            "commands": [
                {"code": "switch_led", "value": false}
            ]
        }
        ```
    * Change device's brightness:
        ```json
        {
            "commands": [
                {"code": "bright_value", "value": 125}
            ]
        }
        ```

## Deployment
The best approach is to spin up a docker container with `docker-compose`. *NOTE: Update secrets.env before build.*

### Balena Cloud
Currently gateway is running in Docker environment on Raspberry Pi v4 running BalenaOS. Their service handles deployment 
and the build in the cloud and the code is pushed via the Balena CLI, for more information go to:
[Balena CLI](https://github.com/balena-io/balena-cli/blob/master/INSTALL.md)

```bash
balena push <aplication_name>
```  

### Docker

```bash
docker-compose build
docker-compose up

docker image ls
docker ps

# Connect to shell in the container
docker exec -it tuya-gateway_gateway_1 /bin/sh
```

## License
[MIT](https://choosealicense.com/licenses/mit/)