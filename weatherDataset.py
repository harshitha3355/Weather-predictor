import numpy as np
import requests
import time

CHANNEL_ID = "3003731"
WRITE_API_KEY = "2ILFSOB3VVA5D69A"

# Simulate 1000 entries of realistic weather data
def generate_fake_data(n=1000):
    temps = np.random.normal(25, 5, n)          # Mean 25°C, ±5°C
    humidity = np.random.normal(60, 15, n)       # Mean 60%, ±15%
    pressure = np.random.normal(1013, 10, n)     # Mean 1013 hPa, ±10
    rain = np.random.randint(0, 1024, n)         # Rain sensor (0-1023)
    return temps, humidity, pressure, rain

# Upload to ThingSpeak
def upload_to_thingspeak(temp, humidity, pressure, rain):
    url = f"https://api.thingspeak.com/update?api_key={WRITE_API_KEY}"
    params = {
        "field1": temp,
        "field2": humidity,
        "field3": pressure,
        "field4": rain
    }
    response = requests.get(url, params=params)
    return response.status_code == 200

# Main loop
temps, humidity, pressure, rain = generate_fake_data(1000)
for i in range(1000):
    success = upload_to_thingspeak(temps[i], humidity[i], pressure[i], rain[i])
    print(f"Entry {i+1}/1000: {'Success' if success else 'Failed'}")
    time.sleep(0.01)  # Respect ThingSpeak's 15-sec limit