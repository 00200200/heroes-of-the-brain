""" EEG measurement example
Infinite Loop: Runs until Ctrl+C is pressed.
Saves CSV Snapshot every 1s.
"""

import matplotlib.pyplot as plt
import matplotlib
import time
import os
import numpy as np
import sys
from scipy.signal import butter, sosfiltfilt

from brainaccess.utils import acquisition
from brainaccess.core.eeg_manager import EEGManager

matplotlib.use("TKAgg", force=True)

# --- Setup ---
eeg = acquisition.EEG()

cap: dict = {
 0: "F3", 1: "F4", 2: "C3", 3: "C4",
 4: "P3", 5: "P4", 6: "O1", 7: "O2",
}

device_name = "BA MINI 049"

os.makedirs('./BrainAccessData', exist_ok=True)
csv_filename = f'./BrainAccessData/{time.strftime("%Y%m%d_%H%M")}-snapshot.csv'
header_str = "time," + ",".join(cap.values())

print(f"Snapshot data will be saved to: {csv_filename}")
print("Press Ctrl+C in the terminal to STOP the recording.")

# --- Start ---
with EEGManager() as mgr:
    eeg.setup(mgr, device_name=device_name, cap=cap, sfreq=250)

    eeg.start_acquisition()
    print("Acquisition started. Waiting 5s...")
    time.sleep(5)
    
    acquisition_start_time = time.time()
    
    # Zmienne kontrolne
    last_idx = 0
    last_save_time = time.time()
    save_interval = 1.0
    annotation = 1

    try:
        # --- NIESKOŃCZONA PĘTLA ---
        while True:
            current_time = time.time()

            # Timer: Co 1 sekundę
            if current_time - last_save_time >= save_interval:
                
                print(f"--- 1s Tick: Annotation {annotation}")
                try:
                    eeg.annotate(str(annotation))
                except:
                    pass # Ignoruj błędy annotacji przy zrywaniu połączenia
                annotation += 1
                
                # Update danych
                eeg.get_mne()
                
                if eeg.data.mne_raw is not None:
                    d, t = eeg.data.mne_raw.get_data(return_times=True)
                    current_len = d.shape[1]
                    
                    if current_len > last_idx:
                        new_data = d[:, last_idx:]
                        new_times = t[last_idx:] + acquisition_start_time
                        
                        chunk_to_save = np.vstack((new_times, new_data)).T
                        
                        # Nadpisz plik
                        with open(csv_filename, 'w') as f:
                            np.savetxt(f, chunk_to_save, delimiter=',', header=header_str, comments='')
                        
                        print(f"   -> Overwritten CSV with {new_data.shape[1]} samples.")
                        last_idx = current_len

                last_save_time = current_time

            # CPU chill
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n\n!!! STOPPING (Ctrl+C detected) !!!")

    print("Closing connection...")
    eeg.stop_acquisition()
    mgr.disconnect()

# --- Koniec (zapisz FIF po przerwaniu) ---
print("Saving final FIF file...")
eeg.data.save(f'./BrainAccessData/{time.strftime("%Y%m%d_%H%M")}-raw.fif')
eeg.close()

print("Plotting...")
mne_raw = eeg.data.mne_raw
if mne_raw is not None:
    mne_raw.apply_function(lambda x: x*10**-6)
    mne_raw.filter(1, 40).plot(scalings="auto", verbose=False)
    plt.show()