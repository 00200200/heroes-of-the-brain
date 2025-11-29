"""EEG Headset interface for BrainAccess MINI 049.

This module handles connection and data acquisition from the BrainAccess
MINI 049 4-channel headset with robust error handling and data buffering.
"""

import os
import time
from typing import Any, Dict, List, Optional

import numpy as np

from eeg_config import DATA_FOLDER_PATH, DEVICE_NAME, NUM_CHANNELS, SAMPLING_RATE, USED_DEVICE

# --- HARDWARE IMPORTS SECTION ---
BRAINACCESS_AVAILABLE = False
try:
    from brainaccess.utils import acquisition
    from brainaccess.core.eeg_manager import EEGManager
    import brainaccess.core as bacore
    BRAINACCESS_AVAILABLE = True
except Exception as e:
    # brainaccess requires libbacore.so native library
    # This is expected to fail on systems without the hardware drivers
    print(f"[INFO] BrainAccess library not available: {e}")
    print("[INFO] This is expected if libbacore.so (hardware driver) is not installed")


class EEGHeadset:
    """Handle connection and data acquisition from BrainAccess MINI 049 4-channel headset."""

    def __init__(self, participant_id: str = "test_user") -> None:
        """Initialize the EEG headset interface.

        Args:
            participant_id: ID to use as folder name for saved data.
        """
        self._is_connected: bool = False
        self._is_recording: bool = False
        self._participant_id: str = participant_id
        self._save_dir_path: str = os.path.join(DATA_FOLDER_PATH, participant_id)
        self._connection_attempts: int = 0
        self._max_attempts: int = 3
        self._buffer: List[np.ndarray] = []
        self._annotations: List[Dict[str, Any]] = []
        self._eeg_manager: Optional[Any] = None
        self._eeg_acquisition: Optional[Any] = None
        self._recording_start_time: float = 0

        if BRAINACCESS_AVAILABLE:
            try:
                print("Initializing BrainAccess library...")
                bacore.init(bacore.Version(2, 0, 0))
                print("BrainAccess library initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize BrainAccess: {e}")
                BRAINACCESS_AVAILABLE = False
        else:
            print("BrainAccess library import failed - check dependencies")

        # Create directories for data storage
        self._create_dir_if_not_exist(DATA_FOLDER_PATH)
        self._create_dir_if_not_exist(self._save_dir_path)

    def connect(self) -> bool:
        """Connect to the BrainAccess MINI 049 headset over Bluetooth.

        Returns:
            True if connection was successful, False otherwise.
        """
        if self._is_connected:
            print("Already connected to the headset.")
            return True

        if not BRAINACCESS_AVAILABLE:
            print("BrainAccess library not available.")
            return False

        print(f"Attempting to connect to {DEVICE_NAME} over Bluetooth...")

        while self._connection_attempts < self._max_attempts:
            try:
                # Create EEG manager and acquisition objects
                self._eeg_manager = EEGManager()
                self._eeg_acquisition = acquisition.EEG()

                # Setup EEG acquisition with BA MINI 049 device
                # The cap parameter maps channel indices to electrode names
                self._eeg_acquisition.setup(
                    self._eeg_manager,
                    device_name=DEVICE_NAME,
                    cap=USED_DEVICE,
                    sfreq=SAMPLING_RATE,
                )

                # Check connection
                if self._eeg_manager.is_connected():
                    self._is_connected = True
                    print(f"Successfully connected to {DEVICE_NAME}!")
                    print(f"Sampling rate: {SAMPLING_RATE} Hz")
                    print(f"Channels: {list(USED_DEVICE.values())}")
                    return True

            except Exception as e:
                self._connection_attempts += 1
                print(
                    f"Connection attempt {self._connection_attempts} failed: {str(e)}"
                )
                print(f"Retrying in {self._connection_attempts} seconds...")
                time.sleep(self._connection_attempts)

        print(f"Failed to connect to {DEVICE_NAME} after multiple attempts.")
        print("Please check that:")
        print("1. The device is turned on and charged")
        print("2. The device is paired via Bluetooth")
        print("3. The device name is correct (currently: {})".format(DEVICE_NAME))
        return False

    def disconnect(self) -> None:
        """Disconnect from the BrainAccess MINI 049 headset."""
        if not self._is_connected:
            print("Not connected to any headset.")
            return

        if self._is_recording:
            self.stop_recording()

        try:
            if self._eeg_manager:
                self._eeg_manager.disconnect()
            self._is_connected = False
            print(f"Disconnected from {DEVICE_NAME}.")
        except Exception as e:
            print(f"Error disconnecting from the headset: {str(e)}")

    def start_recording(self, session_name: str = "default_session") -> bool:
        """Start recording EEG data.

        Args:
            session_name: Name of the recording session.

        Returns:
            True if recording started successfully, False otherwise.
        """
        if not self._is_connected:
            if not self.connect():
                print("Cannot start recording: Failed to connect to the headset.")
                return False

        if self._is_recording:
            print("Already recording data.")
            return True

        try:
            print("Starting EEG data acquisition...")
            if self._eeg_acquisition:
                self._eeg_acquisition.start_acquisition()
            self._is_recording = True
            self._session_name = session_name
            self._recording_start_time = time.time()

            self.annotate_event(f"Session started: {session_name}")

            print(f"Recording started for session: {session_name}")
            return True
        except Exception as e:
            print(f"Error starting recording: {str(e)}")
            return False

    def stop_recording(self) -> bool:
        """Stop recording and save the data.

        Returns:
            True if data was saved successfully, False otherwise.
        """
        if not self._is_recording:
            print("No active recording to stop.")
            return False

        try:
            self.annotate_event("Session ended")

            if self._eeg_acquisition:
                print("Processing recorded data...")
                mne_raw = self._eeg_acquisition.get_mne()

                file_path = os.path.join(
                    self._save_dir_path,
                    f"{self._participant_id}_{self._session_name}_{int(self._recording_start_time)}_raw.fif",
                )
                print(f"Saving EEG data to {file_path}")
                if mne_raw and hasattr(mne_raw, "save"):
                    mne_raw.save(file_path)

                self._eeg_acquisition.stop_acquisition()

                if self._eeg_manager:
                    self._eeg_manager.clear_annotations()

            self._is_recording = False

            print("Recording stopped and data saved successfully.")
            return True
        except Exception as e:
            print(f"Error stopping recording: {str(e)}")
            return False

    def annotate_event(self, annotation: str) -> None:
        """Add an annotation to the EEG data.

        Args:
            annotation: Annotation text to add.
        """
        if not self._is_connected:
            print("Cannot annotate: Not connected to the headset.")
            return

        try:
            timestamp = (
                time.time() - self._recording_start_time if self._is_recording else 0
            )
            if self._eeg_acquisition:
                self._eeg_acquisition.annotate(annotation)
            self._annotations.append({"timestamp": timestamp, "annotation": annotation})
            print(f"Annotation added: '{annotation}' at {timestamp:.2f}s")
        except Exception as e:
            print(f"Error adding annotation: {str(e)}")

    def get_channel_names(self) -> List[str]:
        """Get the names of the EEG channels.

        Returns:
            List of channel names.
        """
        return list(USED_DEVICE.keys())

    def get_current_data(self, duration_seconds: float = 1.0) -> np.ndarray:
        """Get the most recent EEG data.

        Args:
            duration_seconds: Amount of data to return in seconds.

        Returns:
            Array of EEG data with shape (channels, samples).
        """
        if not self._is_recording:
            print("Cannot get data: Not currently recording.")
            return np.zeros((NUM_CHANNELS, int(duration_seconds * SAMPLING_RATE)))

        try:
            if not self._eeg_acquisition:
                return np.zeros((NUM_CHANNELS, int(duration_seconds * SAMPLING_RATE)))

            mne_raw_latest = self._eeg_acquisition.get_mne(
                tim=duration_seconds, annotations=False
            )

            if mne_raw_latest and hasattr(mne_raw_latest, "get_data"):
                data = mne_raw_latest.get_data()
                return data
            else:
                return np.zeros((NUM_CHANNELS, int(duration_seconds * SAMPLING_RATE)))

        except Exception as e:
            print(f"Error getting current data: {str(e)}")
            return np.zeros((NUM_CHANNELS, int(duration_seconds * SAMPLING_RATE)))

    def _create_dir_if_not_exist(self, path: str) -> None:
        """Create a directory if it does not exist.

        Args:
            path: Directory path to create.
        """
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created directory: {path}")
