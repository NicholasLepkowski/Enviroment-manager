import random

class _FakeData:
    def __init__(self):
        self.temperature = round(random.uniform(20, 26), 2)
        self.humidity = round(random.uniform(40, 60), 2)
        self.pressure = round(random.uniform(1000, 1020), 2)
        self.gas_resistance = round(random.uniform(50000, 90000), 0)
        self.heat_stable = True

class BME680:
    def __init__(self, *args, **kwargs):
        self.data = _FakeData()

    def set_humidity_oversample(self, *a, **k): pass
    def set_pressure_oversample(self, *a, **k): pass
    def set_temperature_oversample(self, *a, **k): pass
    def set_filter(self, *a, **k): pass
    def set_gas_status(self, *a, **k): pass
    def set_gas_heater_temperature(self, *a, **k): pass
    def set_gas_heater_duration(self, *a, **k): pass
    def select_gas_heater_profile(self, *a, **k): pass

    def get_sensor_data(self):
        self.data = _FakeData()
        return True

I2C_ADDR_PRIMARY = 0x76
I2C_ADDR_SECONDARY = 0x77
OS_2X = OS_4X = OS_8X = None
FILTER_SIZE_3 = None
ENABLE_GAS_MEAS = None