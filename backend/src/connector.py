import asyncio
import csv
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
import requests
import typer

from eeg_config import (
    ACCEL_CHANNELS,
    BATTERY_MAX_MV,
    BATTERY_MIN_MV,
    DATA_FOLDER_PATH,
    NUM_ACCEL_CHANNELS,
    NUM_CHANNELS,
    PACKET_SIZE,
    PACKETS_PER_SECOND,
    SAMPLING_RATE,
)
from eeg_headset import EEGHeadset

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] BRIDGE: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("connector")

# Silence verbose logs from requests/urllib3 to avoid spam
logging.getLogger("urllib3").setLevel(logging.WARNING)

app = typer.Typer()
BACKEND_URL = "http://localhost:8000/metrics/ingest"


async def setup_device(mock: bool) -> Optional[EEGHeadset]:
    """Initializes the connection to the BrainAccess device.

    Args:
        mock: If True, use mock mode. If False, attempt real hardware connection.

    Returns:
        EEGHeadset instance if successful, None otherwise.
    """
    if mock:
        logger.info("Mock mode enabled - no hardware connection needed")
        return None

    headset = EEGHeadset(participant_id="connector_session")

    if headset.connect():
        logger.info("Successfully connected to BrainAccess Halo headset!")
        if headset.start_recording(session_name="eeg_stream"):
            logger.info("Started recording from headset")
            return headset
        else:
            logger.error("Failed to start recording")
            headset.disconnect()
            return None
    else:
        logger.error("Failed to connect to headset")
        return None


async def stream_process(mock: bool) -> None:
    """Main data streaming loop.

    Args:
        mock: If True, run in mock simulation mode.
    """
    mode = "MOCK SIMULATION" if mock else "REAL HARDWARE"
    logger.info(f"Starting Connector in mode: {mode}")

    device = await setup_device(mock)
    if not mock and device is None:
        logger.error("Failed to initialize device")
        return

    logger.info("Starting data streaming...")

    # Setup CSV logging for mock mode
    csv_file = None
    csv_writer = None
    if mock:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"mock_eeg_{timestamp_str}.csv"
        csv_path = os.path.join(DATA_FOLDER_PATH, csv_filename)
        
        # Create directory if needed
        os.makedirs(DATA_FOLDER_PATH, exist_ok=True)
        
        csv_file = open(csv_path, "w", newline="")
        
        # Create header: timestamp, ch1-ch8, accel_x/y/z, battery_level
        fieldnames = ["timestamp"] + [f"ch{i+1}" for i in range(NUM_CHANNELS)] + ACCEL_CHANNELS + ["battery_level"]
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_file.flush()
        
        logger.info(f"Mock mode CSV logging enabled: {csv_path}")

    # OPTIMIZATION: Use Session to maintain a single TCP connection (Keep-Alive)
    session = requests.Session()
    packet_delay = 1.0 / PACKETS_PER_SECOND  # 0.125 seconds for 8 packets/sec

    try:
        while True:
            try:
                data_packet: Dict = {}
                packet_timestamp = time.time()

                # --- A. DATA ACQUISITION ---
                if mock:
                    # Simulation: 8 EEG channels, 256 samples per packet
                    eeg_data = np.random.normal(0, 1, size=(NUM_CHANNELS, PACKET_SIZE)).tolist()
                    
                    # Accelerometer data (X, Y, Z) - one value per packet
                    accel_data = np.random.uniform(-10, 10, size=(NUM_ACCEL_CHANNELS,)).tolist()
                    
                    # Battery level (0-100%)
                    battery_level = np.random.uniform(20, 100)
                    
                    data_packet = {
                        "eeg": eeg_data,
                        "accel": accel_data,
                        "battery": battery_level,
                        "timestamp": packet_timestamp,
                    }
                    
                    # Log each sample to CSV (accel and battery are constant per packet)
                    if csv_writer:
                        for sample_idx in range(PACKET_SIZE):
                            row = {"timestamp": packet_timestamp}
                            # EEG channels
                            for ch_idx in range(NUM_CHANNELS):
                                row[f"ch{ch_idx+1}"] = eeg_data[ch_idx][sample_idx]
                            # Accelerometer (same for all samples in packet)
                            row["accel_x"] = accel_data[0]
                            row["accel_y"] = accel_data[1]
                            row["accel_z"] = accel_data[2]
                            # Battery level (same for all samples in packet)
                            row["battery_level"] = battery_level
                            csv_writer.writerow(row)
                        csv_file.flush()
                    
                    await asyncio.sleep(packet_delay)
                elif device:
                    # BrainAccess get_current_data returns data for the specified duration
                    chunk = device.get_current_data(duration_seconds=1.0 / PACKETS_PER_SECOND)

                    # Data validation
                    if chunk is not None and chunk.size > 0:
                        # Important: Convert NumPy -> List (for JSON serialization)
                        if hasattr(chunk, "tolist"):
                            eeg_data = chunk.tolist()
                        else:
                            eeg_data = [list(row) for row in chunk]
                        
                        # Real hardware: mock accel and battery for now
                        accel_data = [0.0, 0.0, 0.0]  # TODO: Read from actual accelerometer
                        battery_level = 85.0  # TODO: Read from actual battery sensor
                        
                        data_packet = {
                            "eeg": eeg_data,
                            "accel": accel_data,
                            "battery": battery_level,
                            "timestamp": packet_timestamp,
                        }
                    else:
                        # Empty buffer, short pause to save CPU cycles
                        await asyncio.sleep(0.005)
                        continue

                # --- B. SENDING TO DOCKER ---
                if data_packet:
                    payload = data_packet

                    # DEBUG LOGGING: Preview sent data if debug mode is on
                    if logger.isEnabledFor(logging.DEBUG):
                        try:
                            preview_eeg = [
                                round(ch[0], 2)
                                for ch in data_packet.get("eeg", [])
                                if len(ch) > 0
                            ]
                        except Exception:
                            preview_eeg = "Parse Error"

                        logger.debug(
                            f"Sending: EEG={preview_eeg} | "
                            f"Accel={[round(x, 2) for x in data_packet.get('accel', [])]} | "
                            f"Battery={round(data_packet.get('battery', 0), 1)}% | "
                            f"TS: {payload['timestamp']:.3f}"
                        )

                    try:
                        # Use session.post instead of requests.post for performance
                        resp = session.post(BACKEND_URL, json=payload, timeout=0.2)

                        if resp.status_code != 200:
                            logger.warning(f"Backend returned error: {resp.status_code}")
                        elif logger.isEnabledFor(logging.DEBUG):
                            logger.debug("Packet sent successfully (HTTP 200)")

                    except requests.exceptions.ConnectionError:
                        # Docker might be down or restarting, don't panic, just retry
                        pass
                    except Exception as req_err:
                        logger.warning(f"Send error: {req_err}")

            except KeyboardInterrupt:
                logger.info("Stopped by user.")
                break
            except Exception as e:
                logger.exception(f"Critical loop error: {e}")
                await asyncio.sleep(1)

    finally:
        # Cleanup on exit
        if csv_file:
            csv_file.close()
            logger.info("CSV file closed")

        if device and not mock:
            try:
                logger.info("Closing stream...")
                device.stop_recording()
                device.disconnect()
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")

        logger.info("Connector finished work.")


@app.command()
def start(mock: bool = False, debug: bool = False) -> None:
    """
    Starts the EEG -> Docker bridge.
    Use --mock if you don't have the cap connected.
    Use --debug to see detailed data logs.
    """
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled - verbose logging ON")

    try:
        asyncio.run(stream_process(mock))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    app()