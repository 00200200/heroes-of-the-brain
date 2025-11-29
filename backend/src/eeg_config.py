"""EEG configuration constants for BrainAccess Halo headset.

This module defines all configuration parameters for EEG data acquisition,
including sampling rate, number of channels, device setup, and data storage paths.
"""

import os

# --- SAMPLING & ACQUISITION ---
SAMPLING_RATE: int = 1000  # Hz (samples per second) - BA MINI 049 native rate
NUM_CHANNELS: int = 4  # Number of EEG channels (BA MINI 049 has 4 channels)
NUM_ACCEL_CHANNELS: int = 3  # Accelerometer channels (X, Y, Z)
PACKET_SIZE: int = 256  # Samples per packet
PACKETS_PER_SECOND: int = 8  # Packets per second (8 * 256 = 2048 Hz effective, resampled from 1000 Hz)

# --- DATA STORAGE ---
DATA_FOLDER_PATH: str = os.path.join(os.path.dirname(__file__), "..", "data", "eeg_recordings")

# --- HARDWARE CONNECTION ---
DEVICE_NAME: str = "BA MINI 049"  # BrainAccess MINI device name
PORT: str = "COM3"  # Serial port (adjust for your system: /dev/ttyUSB0 on Linux, COM3 on Windows)

# --- CHANNEL MAPPING ---
# 4 channels: Fp1, Fp2, O1, O2 (standard placement for BA MINI 049)
USED_DEVICE: dict = {
    0: "Fp1",
    1: "Fp2",
    2: "O1",
    3: "O2",
}

# --- ACCELEROMETER ---
ACCEL_CHANNELS: list = ["accel_x", "accel_y", "accel_z"]

# --- BATTERY ---
BATTERY_MIN_MV: int = 3000  # Minimum battery voltage (mV)
BATTERY_MAX_MV: int = 4200  # Maximum battery voltage (mV)

