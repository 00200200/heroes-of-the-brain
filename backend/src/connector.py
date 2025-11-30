"""EEG measurement example
Infinite Loop: Runs until Ctrl+C is pressed.
Saves CSV Snapshot every 1s.
"""

import logging
import os
import time

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from brainaccess.core.eeg_manager import EEGManager
from brainaccess.utils import acquisition
from scipy.signal import butter, sosfiltfilt

matplotlib.use("TKAgg", force=True)

# --- Setup ---
eeg = acquisition.EEG()

cap: dict = {
    0: "F3", 1: "F4", 2: "C3", 3: "C4",
    4: "P3", 5: "P4", 6: "O1", 7: "O2",
}

device_name = "BA MINI 049"

os.makedirs("./BrainAccessData", exist_ok=True)
csv_filename = f'./BrainAccessData/{time.strftime("%Y%m%d_%H%M")}-snapshot.csv'
header_str = "time," + ",".join(cap.values())


def butter_bandpass(lowcut, highcut, fs, order=2):
    """Butterworth bandpass filter design."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = butter(order, [low, high], analog=False, btype="bandpass", output="sos")
    return sos


def design_filters(sfreq):
    """Design bandpass (1-40Hz) and notch (50Hz) filters.
    
    Args:
        sfreq: Sampling frequency in Hz
    
    Returns:
        dict: Contains 'bandpass_sos' and 'notch_sos' filter coefficients

    """
    # Bandpass filter: 1-40 Hz
    bandpass_sos = butter_bandpass(1, 40, sfreq, order=2)

    # Notch filter: 50 Hz
    nyq = 0.5 * sfreq
    notch_freq = 50 / nyq
    notch_sos = butter(2, [notch_freq - 0.01, notch_freq + 0.01],
                       analog=False, btype="bandstop", output="sos")

    return {
        "bandpass_sos": bandpass_sos,
        "notch_sos": notch_sos,
    }

def preprocess_chunk(chunk, filter_state):
    """Preprocesses a chunk of EEG data.
    Steps:
      1. Remove mean from each channel
      2. Bandpass filter (1-40 Hz)
      3. Notch filter (50 Hz)
      4. Average reference (re-referencing)

    Args:
        chunk: np.ndarray, shape (n_channels, n_samples)
        filter_state: dict with 'bandpass_sos' and 'notch_sos'
    Returns:
        chunk_clean: np.ndarray, shape (n_channels, n_samples)

    """
    import numpy as np

    # 1. Remove mean from each channel
    chunk_demean = chunk - np.mean(chunk, axis=1, keepdims=True)

    # 2. Bandpass filter
    chunk_band = np.zeros_like(chunk_demean)
    for ch in range(chunk.shape[0]):
        chunk_band[ch] = sosfiltfilt(filter_state["bandpass_sos"], chunk_demean[ch])

    # 3. Notch filter
    chunk_notch = np.zeros_like(chunk_band)
    for ch in range(chunk.shape[0]):
        chunk_notch[ch] = sosfiltfilt(filter_state["notch_sos"], chunk_band[ch])

    # 4. Average reference (re-referencing)
    avg = np.mean(chunk_notch, axis=0, keepdims=True)
    chunk_clean = chunk_notch - avg

    return chunk_clean


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    logger.info("Snapshot data will be saved to: %s", csv_filename)
    logger.info("Press Ctrl+C in the terminal to STOP the recording.")

    # --- Przygotuj filtry ---
    sfreq = 250
    filters = design_filters(sfreq)
    bandpass_sos = filters["bandpass_sos"]
    notch_sos = filters["notch_sos"]
    logger.info("Filters loaded: Bandpass (1-40Hz) and Notch (50Hz)")

    # --- Start ---
    with EEGManager() as mgr:
        eeg.setup(mgr, device_name=device_name, cap=cap, sfreq=sfreq)

        eeg.start_acquisition()
        logger.info("Acquisition started. Waiting 5s...")
        time.sleep(5)

        acquisition_start_time = time.time()

        # Zmienne kontrolne
        last_idx = 0
        last_save_time = time.time()
        save_interval = 2.0
        annotation = 1

        try:
            # --- NIESKOŃCZONA PĘTLA ---
            while True:
                current_time = time.time()

                # Timer: Co 3 sekundy
                if current_time - last_save_time >= save_interval:

                    logger.info("--- 5s  Tick: Annotation %d", annotation)
                    try:
                        eeg.annotate(str(annotation))
                    except Exception as exc:
                        logger.warning("Annotation error: %s", exc)
                    annotation += 1

                    # Update danych
                    eeg.get_mne()

                    if eeg.data.mne_raw is not None:
                        d, t = eeg.data.mne_raw.get_data(return_times=True)
                        current_len = d.shape[1]

                        if current_len > last_idx:
                            new_data = d[:, last_idx:]
                            new_times = t[last_idx:] + acquisition_start_time

                            # Przetwarzanie 'w locie' za pomocą preprocess_chunk
                            filtered_data = preprocess_chunk(new_data, filters)
                            chunk_to_save = np.vstack((new_times, filtered_data)).T

                            if annotation >= 2:
                                with open(csv_filename, "w") as f:
                                    np.savetxt(f, chunk_to_save, delimiter=",", header=header_str, comments="")

                                logger.info("Filtered and saved %d samples.", new_data.shape[1])
                            last_idx = current_len

                    last_save_time = current_time

                # CPU chill
                time.sleep(0.001)

        except KeyboardInterrupt:
            logger.info("\n\n!!! STOPPING (Ctrl+C detected) !!!")

        logger.info("Closing connection...")
        eeg.stop_acquisition()
        mgr.disconnect()

    # --- Koniec (zapisz FIF po przerwaniu) ---
    logger.info("Saving final FIF file...")
    eeg.data.save(f'./BrainAccessData/{time.strftime("%Y%m%d_%H%M")}-raw.fif')
    eeg.close()

    logger.info("Plotting...")
    mne_raw = eeg.data.mne_raw
    if mne_raw is not None:
        mne_raw.apply_function(lambda x: x*10**-6)
        mne_raw.filter(1, 40).plot(scalings="auto", verbose=False)
        plt.show()
