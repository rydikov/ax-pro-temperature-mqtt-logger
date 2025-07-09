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


def log(result: dict):

    # logger.info(f'{name}: {temperature}°C', extra={'sensor': name, 'temperature': temperature, 'humidity': humidity})

    msgs = []

    for k, v in result.items():
        
        name = v['name']
        temperature = v['temperature']
        humidity = v.get('humidity')
        logger.info(f'{name}: {temperature}°C', extra={'sensor': name, 'temperature': temperature, 'humidity': humidity})

        msgs.append((f'ax-pro/sensors/{k}/meta', json.dumps(v)))
    
    publish.multiple(
        msgs,
        hostname=os.environ.get('MQTT_HOSTNAME', 'host.docker.internal'),
        port=int(os.environ.get('MQTT_PORT', 1880)),
    )


def check_devices():

    result = {}

    resp = axpro.zone_status()
    for zone in resp['ZoneList']:
        item = zone['Zone']
        result[item['deviceNo']] = item
        
        
    resp = axpro.siren_status()
    for siren in resp['SirenList']:
        item = siren['Siren']
        result[item['deviceNo']] = item

    log(result)


schedule.every(POLL_TIME_IN_MINUTES).minutes.do(check_devices)

while True:
    schedule.run_pending()
    time.sleep(1)