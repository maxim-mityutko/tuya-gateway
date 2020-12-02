# Tuya Gateway

```commandline
docker-compose build
docker-compose up

docker image ls
docker ps

docker exec -it tuya-gateway_gateway_1 /bin/sh
TUYA_TOKEN=<<token>>
export TUYA_TOKEN
echo $TUYA_TOKEN

```

* Functions: http://host:65080/device/status?device_id=51003425bcddc2a0b429
* Functions: http://host:65080/device/functions?device_id=51003425bcddc2a0b429
* Commands: http://host:65080/device/commands?device_id=51003425bcddc2a0b429
```json
{
	"commands": [
		{"code": "bright_value", "value": 125}
	]
}
```