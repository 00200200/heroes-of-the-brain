"""EEG configuration constants for BrainAccess Halo headset.

This module defines all configuration parameters for EEG data acquisition,
including sampling rate, number of channels, device setup, and data storage paths.
"""

import os

# --- SAMPLING & ACQUISITION ---
SAMPLING_RATE: int = 1000  # Hz (samples per second) - native rate
NUM_CHANNELS: int = 8  # Number of EEG channels
NUM_ACCEL_CHANNELS: int = 3  # Accelerometer channels (X, Y, Z)
PACKET_SIZE: int = 256  # Samples per packet
PACKETS_PER_SECOND: int = 8  # Packets per second (8 * 256 = 2048 Hz effective, resampled from 1000 Hz)

# --- DATA STORAGE ---
DATA_FOLDER_PATH: str = os.path.join(os.path.dirname(__file__), "..", "data", "eeg_recordings")

# --- HARDWARE CONNECTION ---
DEVICE_NAME: str = "BA MINI 049"  # BrainAccess device name
PORT: str = "COM3"  # Serial port (adjust for your system: /dev/ttyUSB0 on Linux, COM3 on Windows)

# --- CHANNEL MAPPING ---
# 8 channels
USED_DEVICE: dict = {
    0: "Ch0",
    1: "Ch1",
    2: "Ch2",
    3: "Ch3",
    4: "Ch4",
    5: "Ch5",
    6: "Ch6",
    7: "Ch7",
}

# --- ACCELEROMETER ---
ACCEL_CHANNELS: list = ["accel_x", "accel_y", "accel_z"]

# --- BATTERY ---
BATTERY_MIN_MV: int = 3000  # Minimum battery voltage (mV)
BATTERY_MAX_MV: int = 4200  # Maximum battery voltage (mV)

