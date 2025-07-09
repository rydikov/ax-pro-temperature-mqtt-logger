import schedule
import logging
import os
import time
import paho.mqtt.publish as publish

from axpro import AxPro
from datetime import datetime
from logging import config


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


def log_temperature(name: str, temperature: str, humidity: str = None):
    logger.info(f'{name}: {temperature}°C', extra={'sensor': name, 'temperature': temperature, 'humidity': humidity})

    topic_pattern = "ax-pro/sensors/{}/{}"
    msgs = [
        (topic_pattern.format(name, 'temperature'), temperature), 
        (topic_pattern.format(name, 'humidity'), humidity),
        (topic_pattern.format(name, 'last_seen'), datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    ]
    publish.multiple(
        msgs,
        hostname=os.environ.get('MQTT_HOSTNAME', 'host.docker.internal'),
        port=int(os.environ.get('MQTT_PORT', 1880)),
    )


def check_devices():

    resp = axpro.zone_status()
    for zone in resp['ZoneList']:
        name = zone['Zone']['name']
        temperature = zone['Zone']['temperature']
        if zone['Zone']['detectorType'] == 'wirelessTemperatureHumidityDetector':
            humidity = zone['Zone']['humidity']
        else:
            humidity = None
        log_temperature(name, temperature, humidity)
        

    resp = axpro.siren_status()
    for siren in resp['SirenList']:
        name = siren['Siren']['name']
        temperature = siren['Siren']['temperature']
        log_temperature(name, temperature, humidity=None)


schedule.every(0.1).minutes.do(check_devices)

while True:
    schedule.run_pending()
    time.sleep(1)