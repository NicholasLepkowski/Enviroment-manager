# Enviroment-manager
a raspberry pi webserver designed to show temperature, humidity, and pressure readouts from a BME680. By Nicholas Lepkowski

this is an environment monitoring system built on a Raspberry Pi with a BME680 sensor. It measures temperature, humidity, barometric pressure and air quality (gas resistance) and logs every reading to a CSV file. A Python Flask server provides the data through JSON endpoints. A PyScript web page shows live readings, high/low/current stats for a chosen time window, and a color-coded air quality bar. Users log in through the web interface to view current and past readings from any device on the network.

it is designed to monitor the conditions inside of a industrial print press (the Acuriojet KM1/KM1e/30000) but can be used for a wide range of applications.

Documentation coming soon.
