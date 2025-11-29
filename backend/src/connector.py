"""EEG data connector bridge - acquires data from BrainAccess device and sends to backend API.

This module handles the main streaming loop that:
1. Connects to BA MINI 049 hardware device
2. Acquires 4-channel EEG + accelerometer + battery data
3. Logs all data to CSV file
4. Sends packets to backend API for metrics computation
5. Optionally plots metrics in real-time
"""

import asyncio
import csv
import logging
import os
import threading
import time
from datetime import datetime
from typing import Dict, Optional

import numpy as np
import requests
import typer

from eeg_config import (
    ACCEL_CHANNELS,
    DATA_FOLDER_PATH,
    DEVICE_NAME,
    NUM_ACCEL_CHANNELS,
    NUM_CHANNELS,
    PACKET_SIZE,
    PACKETS_PER_SECOND,
    SAMPLING_RATE,
)
from eeg_headset import EEGHeadset

# --- MATPLOTLIB SETUP ---
try:
    import matplotlib
    matplotlib.use('Agg')  # Use Agg for non-interactive rendering
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] CONNECTOR: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("connector")

# Silence verbose logs from requests/urllib3
logging.getLogger("urllib3").setLevel(logging.WARNING)

app = typer.Typer()
BACKEND_URL = "http://localhost:8000/metrics/ingest"


async def stream_eeg_data(debug: bool = False) -> None:
    """Main EEG data streaming loop.
    
    Connects to BA MINI 049, acquires data in real-time, logs to CSV,
    and sends packets to backend API for mental metrics computation.
    
    Args:
        debug: If True, enable verbose debug logging.
    """
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled - verbose logging ON")
    
    logger.info(f"Starting EEG Connector for {DEVICE_NAME}...")
    
    # --- INITIALIZE HEADSET ---
    headset = EEGHeadset(participant_id="connector_session")
    
    if not headset.connect():
        logger.error("Failed to connect to headset. Exiting.")
        return
    
    if not headset.start_recording(session_name="streaming"):
        logger.error("Failed to start recording. Exiting.")
        headset.disconnect()
        return
    
    logger.info("Successfully connected and started recording")
    
    # --- SETUP CSV LOGGING ---
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"eeg_data_{timestamp_str}.csv"
    csv_path = os.path.join(DATA_FOLDER_PATH, csv_filename)
    
    os.makedirs(DATA_FOLDER_PATH, exist_ok=True)
    
    csv_file = open(csv_path, "w", newline="")
    fieldnames = (
        ["timestamp"] 
        + [f"ch{i+1}" for i in range(NUM_CHANNELS)] 
        + ACCEL_CHANNELS 
        + ["battery_level"]
    )
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    csv_file.flush()
    
    logger.info(f"CSV logging enabled: {csv_path}")
    
    # --- SETUP HTTP SESSION ---
    session = requests.Session()
    packet_delay = 1.0 / PACKETS_PER_SECOND  # 0.125 seconds for 8 packets/sec
    
    try:
        logger.info("Starting data acquisition loop...")
        while True:
            try:
                packet_timestamp = time.time()
                
                # --- GET DATA FROM HEADSET ---
                chunk = headset.get_current_data(duration_seconds=1.0 / PACKETS_PER_SECOND)
                
                if chunk is None or chunk.size == 0:
                    logger.warning("Empty data chunk received")
                    await asyncio.sleep(0.01)
                    continue
                
                # Convert to list for JSON serialization
                if hasattr(chunk, "tolist"):
                    eeg_data = chunk.tolist()
                else:
                    eeg_data = [list(row) for row in chunk]
                
                # Get accelerometer data from headset
                accel_data = headset.get_accelerometer()
                battery_level = 85.0  # TODO: read from actual battery sensor
                
                # --- LOG TO CSV ---
                if len(eeg_data) > 0 and len(eeg_data[0]) > 0:
                    for sample_idx in range(len(eeg_data[0])):
                        row = {"timestamp": packet_timestamp}
                        # EEG channels
                        for ch_idx in range(NUM_CHANNELS):
                            if ch_idx < len(eeg_data) and sample_idx < len(eeg_data[ch_idx]):
                                row[f"ch{ch_idx+1}"] = eeg_data[ch_idx][sample_idx]
                        # Accelerometer
                        row["accel_x"] = accel_data[0]
                        row["accel_y"] = accel_data[1]
                        row["accel_z"] = accel_data[2]
                        # Battery
                        row["battery_level"] = battery_level
                        csv_writer.writerow(row)
                    csv_file.flush()
                
                # --- SEND TO BACKEND ---
                data_packet = {
                    "eeg": eeg_data,
                    "accel": accel_data,
                    "battery": battery_level,
                    "timestamp": packet_timestamp,
                }
                
                # Debug preview
                if logger.isEnabledFor(logging.DEBUG):
                    try:
                        preview_eeg = [
                            round(ch[0], 2) if len(ch) > 0 else 0
                            for ch in eeg_data
                        ]
                        logger.debug(
                            f"EEG={preview_eeg} | "
                            f"Accel={[round(x, 2) for x in accel_data]} | "
                            f"Battery={round(battery_level, 1)}%"
                        )
                    except Exception:
                        pass
                
                try:
                    resp = session.post(BACKEND_URL, json=data_packet, timeout=0.5)
                    if resp.status_code != 200:
                        logger.warning(f"Backend error: {resp.status_code}")
                except requests.exceptions.ConnectionError:
                    # Backend might be restarting, just continue
                    pass
                except Exception as e:
                    logger.warning(f"Send error: {e}")
                
                await asyncio.sleep(packet_delay)
                
            except KeyboardInterrupt:
                logger.info("Stopped by user (Ctrl+C)")
                break
            except Exception as e:
                logger.exception(f"Loop error: {e}")
                await asyncio.sleep(0.5)
    
    finally:
        # --- CLEANUP ---
        logger.info("Closing connections...")
        
        if csv_file:
            csv_file.close()
            logger.info("CSV file closed")
        
        try:
            headset.stop_recording()
            headset.disconnect()
            logger.info("Headset disconnected")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
        
        logger.info("Connector finished")


@app.command()
def main(debug: bool = False) -> None:
    """Start the EEG data acquisition connector.
    
    Args:
        debug: Enable verbose debug logging (use --debug flag)
    """
    try:
        asyncio.run(stream_eeg_data(debug=debug))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")


if __name__ == "__main__":
    app()
