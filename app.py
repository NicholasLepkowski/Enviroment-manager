from flask import Flask, render_template, send_file, jsonify
import csv
import os
import time
import threading
from datetime import datetime, timedelta
import pandas as pd
import sys
app = Flask(__name__)
try:
    import bme680
except (ImportError, ModuleNotFoundError):
    import mock_bme680 as bme680
    print("bme680 not found — using mock sensor for local testing")




#sensor initialisation
try:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
    sensor.set_humidity_oversample(bme680.OS_2X)
    sensor.set_pressure_oversample(bme680.OS_4X)
    sensor.set_temperature_oversample(bme680.OS_8X)
    sensor.set_filter(bme680.FILTER_SIZE_3)
    sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
    sensor.set_gas_heater_temperature(320)
    sensor.set_gas_heater_duration(150)
    sensor.select_gas_heater_profile(0)
except (IOError, OSError, RuntimeError) as e:
    print(f"FATAL: could not initialize BME680 sensor: {e}", file=sys.stderr)
    sensor = None

#log file location and timing
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'readings.csv')
read_interval_seconds = 900
retention_days = 30


#sensor error handling
def log_sensor_error(message):
    print(f"[{datetime.now().isoformat()}] SENSOR ERROR: {message}", file=sys.stderr)

#log file code
def ensure_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'temp_f', 'humidity', 'pressure_Kpa', 'gas_resistance_ohm'])

#sensor code
def read_sensor_loop():
    loop_count = 0
    while True:
        try:
            if sensor is None:
                log_sensor_error("Sensor was never initialized — check wiring and I2C connection.")
            else:
                data = take_reading()
                if data is not None:
                    temp_f = (data.temperature * 1.8) + 32
                    pressure_Kpa = (data.pressure * .1)
                    with open(LOG_FILE, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            datetime.now().isoformat(),
                            temp_f,
                            data.humidity,
                            pressure_Kpa,
                            data.gas_resistance,
                        ])
                else:
                    log_sensor_error("Sensor did not stabilize after 5 attempts")
        except Exception as e:
            log_sensor_error(f"Unexpected error in read_sensor_loop: {e}")
        time.sleep(read_interval_seconds)
          
def take_reading():
    for attempt in range(5):
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            return sensor.data
        time.sleep(2)
    return None


#the webpage
@app.route('/')
def home():
    return render_template('home.html')

#credits, probably will delete later
@app.route('/info')
def info():
    return render_template('info.html')

#gives the file to pyscript and also doubles as a neat feature to get the csv off of the pi
#@app.route('/data')
#def data():
    # return send_file(LOG_FILE, mimetype='text/csv')
@app.route('/data')
def data():
    return send_file(LOG_FILE, mimetype='text/csv', as_attachment=True, download_name='readings.csv')
#gives readouts for pressure and gas
@app.route('/latest')
def latest():
    try:
        df = pd.read_csv(LOG_FILE)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        return jsonify({'error': 'no readings yet'}), 503

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])

    if df.empty:
        return jsonify({'error': 'no readings yet'}), 503

    row = df.iloc[-1]
    return jsonify({
        'timestamp': row['timestamp'].isoformat(),
        'temp_f': float(row['temp_f']),
        'humidity': float(row['humidity']),
        'pressure_Kpa': float(row['pressure_Kpa']),
        'gas_resistance_ohm': float(row['gas_resistance_ohm']),
    })
#page startup block
if __name__ == '__main__':
    ensure_log_file()
    print("Starting sensor thread...")
    reader_thread = threading.Thread(target=read_sensor_loop, daemon=True)
    reader_thread.start()
    print(f"Sensor thread alive: {reader_thread.is_alive()}")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)