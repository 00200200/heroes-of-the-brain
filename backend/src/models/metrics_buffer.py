"""
Metrics buffer and utility functions for EEG analysis.
"""

import glob
import os
from collections import deque
import numpy as np
from src.models.focus_model import focus_service
from src.models.stress_model import stress_service
from src.models.tiredness_model import tiredness_service

# Buffer for the last 24 EEG readings (2 minutes at 5s interval)
_eeg_buffer = deque(maxlen=24)

from scipy.signal import butter, sosfiltfilt
"""
Metrics buffer and utility functions for EEG analysis.
"""

# --- EEG band definitions (Hz)
BANDS = {
    'delta': (1, 4),
    'theta': (4, 8),
    'alpha': (8, 13),
    'beta': (13, 30),
    'gamma': (30, 40),
}

def bandpower_rms(data, sfreq, band):
    """
    Calculate RMS bandpower for a given band and channel.
    Args:
        data: np.ndarray, shape (n_samples,)
        sfreq: float, sampling frequency
        band: tuple (low, high)
    Returns:
        float: RMS bandpower
    """
    sos = butter(2, [band[0]/(0.5*sfreq), band[1]/(0.5*sfreq)], btype='bandpass', output='sos')
    filtered = sosfiltfilt(sos, data)
    return np.sqrt(np.mean(filtered**2))

def mean_metrics():
    """
    Return mean metrics (focus, stress, tiredness, timestamp) from the last 2 minutes (EEG buffer).
    Uses the model singletons for normalization to ensure consistency.
    """
    import logging
    if len(_eeg_buffer) == 0:
        return None
    all_eeg = np.vstack([e for (ts, e) in _eeg_buffer])
    all_ts = [ts for (ts, e) in _eeg_buffer]
    mean_ts = float(np.mean(all_ts))
    # Assume sfreq 250 Hz (as in connector.py)
    sfreq = 250
    # Calculate bandpower for each channel and band
    n_channels = all_eeg.shape[1]
    # Calculate bandpower on the whole buffer signal (last 2 minutes)
    alpha = np.zeros(n_channels)
    beta = np.zeros(n_channels)
    theta = np.zeros(n_channels)
    for ch in range(n_channels):
        alpha[ch] = bandpower_rms(all_eeg[:, ch], sfreq, BANDS['alpha'])
        beta[ch] = bandpower_rms(all_eeg[:, ch], sfreq, BANDS['beta'])
        theta[ch] = bandpower_rms(all_eeg[:, ch], sfreq, BANDS['theta'])
    # Focus: Beta/Theta for F3,F4,C3,C4
    beta_fc = np.mean(beta[[0,1,2,3]])
    theta_fc = np.mean(theta[[0,1,2,3]])
    # Stress: FAA (alpha F4 - F3), beta/alpha F3,F4
    alpha_f3 = alpha[0]
    alpha_f4 = alpha[1]
    beta_f3f4 = np.mean(beta[[0,1]])
    alpha_f3f4 = np.mean(alpha[[0,1]])
    # Tiredness: (theta+alpha)/total for P3,P4,O1,O2
    theta_po = np.mean(theta[[4,5,6,7]])
    alpha_po = np.mean(alpha[[4,5,6,7]])
    beta_po = np.mean(beta[[4,5,6,7]])
    total_po = np.abs(alpha_po) + np.abs(beta_po) + np.abs(theta_po) + 1e-6
    # Calculate metrics
    focus_ratio = beta_fc / (theta_fc + 1e-6)
    focus_service.calculate([focus_ratio])
    faa = np.log(alpha_f4 + 1e-6) - np.log(alpha_f3 + 1e-6)
    stress_index = beta_f3f4 / (alpha_f3f4 + 1e-6)
    stress_service.calculate([faa + stress_index], [1.0])
    tiredness = (theta_po + alpha_po) / total_po
    tiredness_service.calculate([tiredness], [1.0], [1.0])
    focus = focus_service.get_value()
    stress = stress_service.get_value()
    tiredness = tiredness_service.get_value()
    logging.getLogger(__name__).info(
        "mean_metrics (true mean): focus=%d, stress=%d, tiredness=%d, ts=%.3f",
        focus, stress, tiredness, mean_ts,
    )
    return {
        "timestamp": mean_ts,
        "focus_level": focus,
        "stress_level": stress,
        "tiredness_level": tiredness,
    }

def update_models_from_latest_csv():
    """
    Load the latest snapshot.csv from BrainAccessData, calculate bands, and update models.
    Models are updated only from the latest file. Buffer is used for mean timestamp.
    """
    import logging
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "../BrainAccessData")
    files = glob.glob(os.path.join(data_dir, "*-snapshot.csv"))
    logging.getLogger(__name__).info("Found CSV files: %s", files)
    if not files:
        logging.getLogger(__name__).warning("No snapshot.csv files found!")
        return None
    latest = max(files, key=os.path.getmtime)
    logging.getLogger(__name__).info("Using file: %s", latest)
    arr = np.genfromtxt(latest, delimiter=",", skip_header=1)
    logging.getLogger(__name__).info("Loaded array shape: %s", arr.shape)
    if arr.ndim == 1:
        arr = arr[np.newaxis, :]
    timestamps = arr[:, 0]
    eeg = arr[:, 1:9]
    logging.getLogger(__name__).info("EEG shape: %s", eeg.shape)
    mean_ts = float(np.mean(timestamps))
    _eeg_buffer.append((mean_ts, eeg))
    if len(_eeg_buffer) == 0:
        logging.getLogger(__name__).warning("EEG buffer is empty!")
        return None
    sfreq = 250
    n_channels = eeg.shape[1]
    alpha = np.zeros(n_channels)
    beta = np.zeros(n_channels)
    theta = np.zeros(n_channels)
    for ch in range(n_channels):
        alpha[ch] = bandpower_rms(eeg[:, ch], sfreq, BANDS['alpha'])
        beta[ch] = bandpower_rms(eeg[:, ch], sfreq, BANDS['beta'])
        theta[ch] = bandpower_rms(eeg[:, ch], sfreq, BANDS['theta'])
    beta_fc = np.mean(beta[[0,1,2,3]])
    alpha_fc = np.mean(alpha[[0,1,2,3]])
    theta_fc = np.mean(theta[[0,1,2,3]])
    alpha_f3 = alpha[0]
    alpha_f4 = alpha[1]
    beta_f3f4 = np.mean(beta[[0,1]])
    alpha_f3f4 = np.mean(alpha[[0,1]])
    theta_po = np.mean(theta[[4,5,6,7]])
    alpha_po = np.mean(alpha[[4,5,6,7]])
    beta_po = np.mean(beta[[4,5,6,7]])
    total_po = np.abs(alpha_po) + np.abs(beta_po) + np.abs(theta_po) + 1e-6
    engagement = beta_fc / (alpha_fc + theta_fc + 1e-6)
    focus_service.calculate([engagement])
    faa = np.log(alpha_f4 + 1e-6) - np.log(alpha_f3 + 1e-6)
    stress_index = beta_f3f4 / (alpha_f3f4 + 1e-6)
    stress_service.calculate([faa + stress_index], [1.0])
    tiredness = (theta_po + alpha_po) / total_po
    tiredness_service.calculate([tiredness], [1.0], [1.0])
    logging.getLogger(__name__).info(
        "focus: %d, stress: %d, tiredness: %d",
        focus_service.get_value(),
        stress_service.get_value(),
        tiredness_service.get_value(),
    )
    # Mean timestamp from buffer (for API)
    all_ts = [ts for (ts, _) in _eeg_buffer]
    mean_ts_buf = float(np.mean(all_ts))
    return mean_ts_buf
