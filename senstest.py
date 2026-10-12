import bme680
import time

sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

for _ in range(10):
    if sensor.get_sensor_data():
        print(sensor.data.temperature, sensor.data.humidity, sensor.data.heat_stable)
    else:
        print("no data")
    time.sleep(2)