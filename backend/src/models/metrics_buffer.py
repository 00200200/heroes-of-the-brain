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
    # Calculate per-sample band powers for the buffer
    beta = np.mean(all_eeg[:, :3], axis=1)
    alpha = np.mean(all_eeg[:, 3:6], axis=1)
    theta = np.mean(all_eeg[:, 6:8], axis=1)
    # Use model singletons for normalization on the full lists
    focus_service.calculate(list(beta))
    stress_service.calculate(list(alpha), list(beta))
    tiredness_service.calculate(list(alpha), list(theta), list(beta))
    focus = focus_service.get_value()
    stress = stress_service.get_value()
    tiredness = tiredness_service.get_value()
    logging.getLogger(__name__).info(
        "mean_metrics (via models, list): focus=%d, stress=%d, tiredness=%d, ts=%.3f",
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
    # Update models only from the latest file
    beta = np.mean(eeg[:, :3], axis=1)
    alpha = np.mean(eeg[:, 3:6], axis=1)
    theta = np.mean(eeg[:, 6:8], axis=1)
    logging.getLogger(__name__).info("beta: %s, alpha: %s, theta: %s", beta, alpha, theta)
    beta_val = beta.mean()
    alpha_val = alpha.mean()
    theta_val = theta.mean()
    logging.getLogger(__name__).info("beta_val: %.3f, alpha_val: %.3f, theta_val: %.3f", beta_val, alpha_val, theta_val)
    focus_service.calculate([beta_val])
    stress_service.calculate([alpha_val], [beta_val])
    tiredness_service.calculate([alpha_val], [theta_val], [beta_val])
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
