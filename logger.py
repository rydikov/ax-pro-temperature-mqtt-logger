import schedule
import logging
import os
import time
import paho.mqtt.publish as publish
import json

from axpro import AxPro
from logging import config


POLL_TIME_IN_MINUTES = float(os.environ.get('POLL_TIME_IN_MINUTES', 1))

config.fileConfig(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 
        'logger/logger.conf'
    )
)

logger = logging.getLogger('json')

axpro = AxPro(
    os.environ.get('AX_PRO_HOST'),
    os.environ.get('AX_PRO_USER'),
    os.environ.get('AX_PRO_PASSWORD')
)


def log(sensor: dict):

    sensor_id = sensor['deviceNo']
    name = sensor['name']
    temperature = sensor['temperature']
    humidity = sensor.get('humidity') # if detectorType == wirelessTemperatureHumidityDetector
    charge = sensor['charge']
    charge_value = sensor.get('chargeValue')
    signal = sensor['signal']
    status = sensor['status']
    meta = json.dumps(sensor)


    
    logger.info(f'{name}: {temperature}°C', extra={'sensor': name, 'temperature': temperature, 'humidity': humidity})

    topic_pattern = "ax-pro/sensors/{}/{}"
    msgs = [
        (topic_pattern.format(sensor_id, 'name'), name), 
        (topic_pattern.format(sensor_id, 'temperature'), temperature), 
        (topic_pattern.format(sensor_id, 'humidity'), humidity),
        (topic_pattern.format(sensor_id, 'charge'), charge),
        (topic_pattern.format(sensor_id, 'charge_value'), charge_value),
        (topic_pattern.format(sensor_id, 'signal'), signal),
        (topic_pattern.format(sensor_id, 'status'), status),
        (topic_pattern.format(sensor_id, 'meta'), meta),
        (topic_pattern.format(sensor_id, 'last_seen'), time.time())
    ]
    publish.multiple(
        msgs,
        hostname=os.environ.get('MQTT_HOSTNAME', 'host.docker.internal'),
        port=int(os.environ.get('MQTT_PORT', 1880)),
    )


def check_devices():

    resp = axpro.zone_status()
    for zone in resp['ZoneList']:
        log(zone['Zone'])
        
    resp = axpro.siren_status()
    for siren in resp['SirenList']:
        log(siren['Siren'])


schedule.every(POLL_TIME_IN_MINUTES).minutes.do(check_devices)

while True:
    schedule.run_pending()
    time.sleep(1)