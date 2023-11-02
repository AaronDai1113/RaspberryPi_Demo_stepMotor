import Adafruit_DHT
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import RPi.GPIO as GPIO
import time

# Sensor Configuration
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4  # GPIO4
STEPPER_PINS = [17, 18, 27, 22]

# Setup GPIO
GPIO.setmode(GPIO.BCM)
for pin in STEPPER_PINS:
    GPIO.setup(pin, GPIO.OUT)

# Steps sequence for half-step drive (8 steps per revolution)
STEP_SEQUENCE = [
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1]
]

def step_motor(steps):
    for _ in range(steps):
        for step in STEP_SEQUENCE:
            for pin, value in zip(STEPPER_PINS, step):
                GPIO.output(pin, value)
            time.sleep(0.005)

# InfluxDB Configuration
url = "http://localhost:8086"
token = "CCytHUChfIEGCcczyz-fr3eAbwVLetZd6domxi39TNPTFA2hWfm3ltJXvs6dSJHYZ_SrRmrRFBtYT0hTFEAr7g==" 
org = "aaron"  
bucket = "aaron"  

client = InfluxDBClient(url=url, token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if temperature is not None:
        print(f'Temperature: {temperature} C')
        point = Point("temperature").field("value", temperature)
        write_api.write(bucket, org, point)

        if temperature >= 29.5:
            step_motor(512)
    time.sleep(0.8)
