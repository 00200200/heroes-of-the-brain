"""BrainAccess BA MINI 049 EEG headset interface.

Handles connection, configuration, and real-time data acquisition from
the 4-channel EEG headset with accelerometer support.
"""

import os
import threading
import time
from typing import Any, Callable, Dict, List, Optional

import numpy as np

from eeg_config import DATA_FOLDER_PATH, DEVICE_NAME, NUM_CHANNELS, SAMPLING_RATE, USED_DEVICE

# --- HARDWARE IMPORTS ---
try:
    from brainaccess.core.eeg_manager import EEGManager
    import brainaccess.core as bacore
    import brainaccess.core.eeg_channel as eeg_channel
    from brainaccess.core.gain_mode import GainMode
    BRAINACCESS_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] BrainAccess not available: {e}")
    BRAINACCESS_AVAILABLE = False


class EEGHeadset:
    """Handle connection and data acquisition from BrainAccess MINI 049 headset."""

    def __init__(self, participant_id: str = "test_user") -> None:
        """Initialize EEG headset interface.
        
        Args:
            participant_id: ID to use as folder name for saved data.
        """
        self._is_connected: bool = False
        self._is_recording: bool = False
        self._participant_id: str = participant_id
        self._save_dir_path: str = os.path.join(DATA_FOLDER_PATH, participant_id)
        self._eeg_manager: Optional[EEGManager] = None
        self._device_name: Optional[str] = None
        self._recording_start_time: float = 0
        self._latest_chunk: Optional[np.ndarray] = None
        self._latest_accel: List[float] = [0.0, 0.0, 0.0]
        self._accel_start_idx: int = 0  # Will be set during connect()
        self._chunk_mutex = threading.Lock()
        self._annotations: List[Dict[str, Any]] = []
        self._brainaccess_available: bool = BRAINACCESS_AVAILABLE

        if self._brainaccess_available:
            try:
                print("Initializing BrainAccess core...")
                bacore.init()
                print("BrainAccess core initialized successfully")
            except Exception as e:
                print(f"[ERROR] Failed to initialize BrainAccess: {e}")
                self._brainaccess_available = False
        else:
            print("[ERROR] BrainAccess library not available - check dependencies")

        self._create_dir_if_not_exist(DATA_FOLDER_PATH)
        self._create_dir_if_not_exist(self._save_dir_path)

    def connect(self) -> bool:
        """Connect to BA MINI 049 headset over Bluetooth.
        
        Returns:
            True if connected, False otherwise.
        """
        if self._is_connected:
            print("Already connected to headset")
            return True

        if not self._brainaccess_available:
            print("[ERROR] BrainAccess library not available")
            return False

        try:
            print(f"[INFO] Scanning for devices...")
            devices = bacore.scan()
            print(f"[INFO] Found {len(devices)} device(s)")

            # Find target device
            device_found = None
            for device in devices:
                print(f"  - {device.name}")
                if DEVICE_NAME in device.name:
                    device_found = device.name
                    break

            if not device_found:
                print(f"[ERROR] Device '{DEVICE_NAME}' not found")
                return False

            self._device_name = device_found
            print(f"[INFO] Connecting to: {self._device_name}")

            # Create manager and connect
            self._eeg_manager = EEGManager()
            status = self._eeg_manager.connect(self._device_name)

            if status == 1:
                print("[ERROR] Connection failed (status=1)")
                return False
            elif status == 2:
                print("[ERROR] Stream incompatible - update firmware (status=2)")
                return False
            elif status != 0:
                print(f"[ERROR] Connection returned unexpected status: {status}")
                return False

            print(f"[INFO] Successfully connected to {self._device_name}")

            # Get device info
            battery_info = self._eeg_manager.get_battery_info()
            print(f"[INFO] Battery: {battery_info.level}%")

            device_features = self._eeg_manager.get_device_features()
            eeg_channels_number = device_features.electrode_count()
            print(f"[INFO] Device has {eeg_channels_number} EEG channels")

            # Configure EEG channels (start from channel 3)
            print("[INFO] Configuring EEG channels...")
            ch_nr = 0
            for i in range(3, eeg_channels_number):
                self._eeg_manager.set_channel_enabled(
                    eeg_channel.ELECTRODE_MEASUREMENT + i, True
                )
                ch_nr += 1
                self._eeg_manager.set_channel_gain(
                    eeg_channel.ELECTRODE_MEASUREMENT + i, GainMode.X8
                )
            self._eeg_manager.set_channel_bias(eeg_channel.ELECTRODE_MEASUREMENT + i, True)

            # Configure accelerometer if available
            has_accel = device_features.has_accel()
            accel_start_idx = ch_nr  # Save accel start index
            if has_accel:
                print("[INFO] Enabling accelerometer...")
                self._eeg_manager.set_channel_enabled(eeg_channel.ACCELEROMETER, True)
                ch_nr += 1
                self._eeg_manager.set_channel_enabled(eeg_channel.ACCELEROMETER + 1, True)
                ch_nr += 1
                self._eeg_manager.set_channel_enabled(eeg_channel.ACCELEROMETER + 2, True)
                ch_nr += 1

            # Enable sample number channel
            self._eeg_manager.set_channel_enabled(eeg_channel.SAMPLE_NUMBER, True)
            ch_nr += 1
            
            # Store accel index for later use in callback
            self._accel_start_idx = accel_start_idx

            # Get sample rate
            sr = self._eeg_manager.get_sample_frequency()
            print(f"[INFO] Sample frequency: {sr} Hz")

            self._is_connected = True
            return True

        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def disconnect(self) -> None:
        """Disconnect from headset."""
        if not self._is_connected:
            print("Not connected")
            return

        if self._is_recording:
            self.stop_recording()

        try:
            if self._eeg_manager:
                self._eeg_manager.disconnect()
            self._is_connected = False
            print(f"[INFO] Disconnected from {self._device_name}")
        except Exception as e:
            print(f"[ERROR] Disconnect error: {e}")

    def start_recording(self, session_name: str = "default_session") -> bool:
        """Start recording EEG data.
        
        Args:
            session_name: Name of recording session.
            
        Returns:
            True if started, False otherwise.
        """
        if not self._is_connected:
            if not self.connect():
                print("[ERROR] Cannot start recording - connection failed")
                return False

        if self._is_recording:
            print("Already recording")
            return True

        try:
            print("[INFO] Starting EEG acquisition...")

            # Define data callback - store latest chunk for retrieval
            def acq_callback(chunk, chunk_size):
                """Callback for incoming data chunks."""
                try:
                    # Convert list to numpy array if needed
                    if isinstance(chunk, list):
                        chunk_array = np.array(chunk)
                    else:
                        chunk_array = chunk
                    
                    with self._chunk_mutex:
                        # Store only EEG channels
                        if chunk_array.shape[0] > NUM_CHANNELS:
                            self._latest_chunk = chunk_array[:NUM_CHANNELS, :].copy()
                            
                            # Extract accelerometer using stored index
                            # Accel is at indices [_accel_start_idx, _accel_start_idx+1, _accel_start_idx+2]
                            if chunk_array.shape[0] > self._accel_start_idx + 2:
                                accel_x = float(np.mean(chunk_array[self._accel_start_idx, :]))
                                accel_y = float(np.mean(chunk_array[self._accel_start_idx + 1, :]))
                                accel_z = float(np.mean(chunk_array[self._accel_start_idx + 2, :]))
                                self._latest_accel = [accel_x, accel_y, accel_z]
                        else:
                            self._latest_chunk = chunk_array.copy()
                except Exception as e:
                    print(f"[ERROR] Callback error: {e}")

            if self._eeg_manager:
                self._eeg_manager.set_callback_chunk(acq_callback)
                self._eeg_manager.load_config()
                self._eeg_manager.start_stream()

            self._is_recording = True
            self._session_name = session_name
            self._recording_start_time = time.time()

            print(f"[INFO] Recording started: {session_name}")
            return True

        except Exception as e:
            print(f"[ERROR] Start recording error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def stop_recording(self) -> bool:
        """Stop recording and save data.
        
        Returns:
            True if saved, False otherwise.
        """
        if not self._is_recording:
            print("No active recording")
            return False

        try:
            if self._eeg_manager:
                print("[INFO] Stopping stream...")
                self._eeg_manager.stop_stream()
                time.sleep(0.5)

            self._is_recording = False
            print("[INFO] Recording stopped")
            return True

        except Exception as e:
            print(f"[ERROR] Stop recording error: {e}")
            self._is_recording = False
            return False

    def annotate_event(self, annotation: str) -> None:
        """Add annotation to EEG data.
        
        Args:
            annotation: Annotation text.
        """
        if not self._is_connected:
            print("Not connected - cannot annotate")
            return

        try:
            timestamp = (
                time.time() - self._recording_start_time if self._is_recording else 0
            )
            # Just store annotation locally (BrainAccess doesn't support add_annotation)
            self._annotations.append({"timestamp": timestamp, "annotation": annotation})
            print(f"[INFO] Annotation: '{annotation}' at {timestamp:.2f}s")
        except Exception as e:
            print(f"[ERROR] Annotation error: {e}")

    def get_current_data(self, duration_seconds: float = 1.0) -> np.ndarray:
        """Get most recent buffered EEG data.
        
        Args:
            duration_seconds: Duration to retrieve (ignored, returns latest chunk).
            
        Returns:
            Array of shape (NUM_CHANNELS, num_samples).
        """
        if not self._is_recording:
            print("[WARNING] Not recording - returning zero buffer")
            return np.zeros((NUM_CHANNELS, int(duration_seconds * SAMPLING_RATE)))

        try:
            with self._chunk_mutex:
                if self._latest_chunk is not None:
                    return self._latest_chunk.copy()
                else:
                    return np.zeros((NUM_CHANNELS, int(duration_seconds * SAMPLING_RATE)))
        except Exception as e:
            print(f"[ERROR] Get data error: {e}")
            return np.zeros((NUM_CHANNELS, int(duration_seconds * SAMPLING_RATE)))

    def get_accelerometer(self) -> List[float]:
        """Get most recent accelerometer data.
        
        Returns:
            List of [accel_x, accel_y, accel_z] values.
        """
        try:
            with self._chunk_mutex:
                return self._latest_accel.copy()
        except Exception as e:
            print(f"[ERROR] Get accel error: {e}")
            return [0.0, 0.0, 0.0]

    def _create_dir_if_not_exist(self, path: str) -> None:
        """Create directory if needed.
        
        Args:
            path: Directory path.
        """
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"[INFO] Created directory: {path}")

