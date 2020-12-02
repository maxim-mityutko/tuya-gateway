# Tuya Gateway
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

## Tuya Setup
**WIP**

## API
* Status    (GET):  http://host:65080/device/status?device_id=xxxxxxx
* Functions (GET):  http://host:65080/device/functions?device_id=xxxxxxx
* Commands  (POST): http://host:65080/device/commands?device_id=xxxxxxx
    ```json
    {
        "commands": [
            {"code": "bright_value", "value": 125}
        ]
    }
    ```

## Deployment
The best approach is to spin up a docker container with `docker-compose`.

NOTE: Update secrets.env before building the containers, 'access key' and 'key secret' are available as the

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

docker exec -it tuya-gateway_gateway_1 /bin/sh
```

## License
[MIT](https://choosealicense.com/licenses/mit/)