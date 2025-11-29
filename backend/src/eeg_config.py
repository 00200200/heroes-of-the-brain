"""EEG configuration constants for BrainAccess Halo headset.

This module defines all configuration parameters for EEG data acquisition,
including sampling rate, number of channels, device setup, and data storage paths.
"""

import os

# --- SAMPLING & ACQUISITION ---
SAMPLING_RATE: int = 256  # Hz (samples per second)
NUM_CHANNELS: int = 8  # Number of EEG channels
NUM_ACCEL_CHANNELS: int = 3  # Accelerometer channels (X, Y, Z)
PACKET_SIZE: int = 256  # Samples per packet
PACKETS_PER_SECOND: int = 8  # Packets per second (8 * 256 = 2048 Hz effective)

# --- DATA STORAGE ---
DATA_FOLDER_PATH: str = os.path.join(os.path.dirname(__file__), "..", "data", "eeg_recordings")

# --- HARDWARE CONNECTION ---
PORT: str = "COM3"  # Serial port (adjust for your system: /dev/ttyUSB0 on Linux, COM3 on Windows)

# --- CHANNEL MAPPING ---
# 8 channels: Fp1, Fp2, F7, F8, T3, T4, O1, O2 (standard 10-20 placement subset)
USED_DEVICE: dict = {
    "Fp1": "EEG Fp1",
    "Fp2": "EEG Fp2",
    "F7": "EEG F7",
    "F8": "EEG F8",
    "T3": "EEG T3",
    "T4": "EEG T4",
    "O1": "EEG O1",
    "O2": "EEG O2",
}

# --- ACCELEROMETER ---
ACCEL_CHANNELS: list = ["accel_x", "accel_y", "accel_z"]

# --- BATTERY ---
BATTERY_MIN_MV: int = 3000  # Minimum battery voltage (mV)
BATTERY_MAX_MV: int = 4200  # Maximum battery voltage (mV)
