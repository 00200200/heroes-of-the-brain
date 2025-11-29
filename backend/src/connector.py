import asyncio
import logging
import time
from typing import List, Optional

import numpy as np
import requests
import typer

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] BRIDGE: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("connector")

# Silence verbose logs from requests/urllib3 to avoid spam
logging.getLogger("urllib3").setLevel(logging.WARNING)

# --- HARDWARE IMPORTS SECTION ---
try:
    from brainaccess.core import Core
except (ImportError, RuntimeError, OSError) as e:
    Core = None
    logger.warning(f"BrainAccess driver not found: {e}. (OK for --mock mode)")

app = typer.Typer()
BACKEND_URL = "http://localhost:8000/api/v1/eeg-stream"


async def setup_device(mock: bool) -> Optional[object]:
    """Initializes the connection to the BrainAccess device."""
    if mock:
        return None

    if Core is None:
        logger.error(
            "Error: 'brainaccess' library missing or DLL not found. "
            "Run with --mock flag or install drivers."
        )
        return None

    try:
        logger.info("Initializing BrainAccess Core driver...")
        device = Core()

        logger.info("Scanning and connecting to device...")
        # NOTE: In C++ API, 0 often means success, while >0 is an error code
        result = device.connect()

        # Handle different API versions (returning bool or int)
        is_connected = (result is True) or (result == 0)

        if is_connected:
            logger.info(f"Connected to hardware! (Code: {result})")
        else:
            logger.error(f"Failed to connect. Error code: {result}")
            return None

        # Setup: chunk_size=20 (at 250Hz -> ~12.5 packets/sec -> smooth)
        device.set_chunk_size(20)
        device.start_stream()
        return device

    except Exception as e:
        logger.error(f"Critical connection error: {e}")
        logger.warning("Tip: Ensure Bluetooth is on and the cap is charged.")
        return None


async def stream_process(mock: bool) -> None:
    """Main data streaming loop."""
    mode = "MOCK SIMULATION" if mock else "REAL HARDWARE"
    logger.info(f"Starting Connector in mode: {mode}")

    device = await setup_device(mock)
    if not mock and device is None:
        return

    logger.info("Starting data streaming...")

    # OPTIMIZATION: Use Session to maintain a single TCP connection (Keep-Alive)
    session = requests.Session()

    while True:
        try:
            data_packet: List[List[float]] = []

            # --- A. DATA ACQUISITION ---
            if mock:
                # Simulation: 8 channels, 20 samples per packet
                # Generates a standard normal distribution
                data_packet = np.random.normal(0, 1, size=(8, 20)).tolist()
                await asyncio.sleep(0.08)  # ~125Hz simulation delay
            elif device:
                # BrainAccess get_data returns data accumulated since last call
                chunk = device.get_data()

                # Data validation
                if chunk is not None and len(chunk) > 0:
                    # Important: Convert NumPy -> List (for JSON serialization)
                    if hasattr(chunk, "tolist"):
                        data_packet = chunk.tolist()
                    else:
                        data_packet = list(chunk)
                else:
                    # Empty buffer, short pause to save CPU cycles
                    await asyncio.sleep(0.005)
                    continue

            # --- B. SENDING TO DOCKER ---
            if data_packet:
                payload = {
                    "data": data_packet,
                    "timestamp": time.time(),
                }

                # DEBUG LOGGING: Preview sent data if debug mode is on
                if logger.isEnabledFor(logging.DEBUG):
                    try:
                        # LOGIC: Take the 1st sample (index 0) from EACH channel row
                        # data_packet is [n_channels][n_samples]
                        preview = [
                            round(channel[0], 2)
                            for channel in data_packet
                            if len(channel) > 0
                        ]
                    except Exception:
                        preview = "Parse Error"

                    logger.debug(
                        f"Sending {len(data_packet)} ch | "
                        f"TS: {payload['timestamp']:.3f} | "
                        f"1st Sample/Ch: {preview}"
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

    # Cleanup on exit
    if device and not mock:
        try:
            logger.info("Closing stream...")
            device.stop_stream()
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