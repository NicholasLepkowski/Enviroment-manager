import asyncio
from io import StringIO
from datetime import datetime, timedelta

import js
import pandas as pd
import matplotlib.pyplot as plt
from pyodide.http import pyfetch
from pyscript import display

refresh_seconds = 5

#grabs the csv
async def fetch_csv_text():
    response = await pyfetch("/data")
    return await response.string()
# grabs the singular readings
async def fetch_latest():
    response = await pyfetch("/latest")
    return await response.json()
#graphing code
def plot_series(df, column, title, ylabel, target_id):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(df["timestamp"], df[column])
    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_ylabel(ylabel)
    ax.grid(True)
    fig.autofmt_xdate()

    display(fig, target=target_id, append=False)
    plt.close(fig)
#readout code
async def render_readouts():
    latest = await fetch_latest()
    if "error" in latest:
        js.document.getElementById("readouts").innerText = "Waiting for first sensor reading..."
        return

    js.document.getElementById("pressure-readout").innerText = f'{latest["pressure_Kpa"]:.1f} Kpa'
    js.document.getElementById("gas-readout").innerText = f'{latest["gas_resistance_ohm"]:.0f} ohms'
    js.document.getElementById("updated-at").innerText = f'Last updated: {latest["timestamp"]}'
#graph rendering
async def render_graphs():
    csv_text = await fetch_csv_text()
    df = pd.read_csv(StringIO(csv_text))
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    cutoff = datetime.now() - timedelta(days=30)
    df = df[df["timestamp"] >= cutoff]

    if df.empty:
        js.document.getElementById("temp-graph").innerText = "No data recorded yet."
        js.document.getElementById("humidity-graph").innerText = ""
        return

    plot_series(df, "temp_f", "Temperature - Last 30 Days", "\u00b0F", "temp-graph")
    plot_series(df, "humidity", "Humidity - Last 30 Days", "%", "humidity-graph")
#refreshing
async def refresh_all():
    await render_graphs()
    await render_readouts()
async def main():
    while True:
        await refresh_all()
        await asyncio.sleep(refresh_seconds)


asyncio.ensure_future(main())