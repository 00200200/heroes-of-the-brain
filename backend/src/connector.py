""" EEG measurement example
Live CSV Snapshot: File contains ONLY the data from the last loop iteration.
"""

import matplotlib.pyplot as plt
import matplotlib
import time
import os
import numpy as np
import threading
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

# --- Start ---
with EEGManager() as mgr:
    eeg.setup(mgr, device_name=device_name, cap=cap, sfreq=250)

    eeg.start_acquisition()
    print("Acquisition started. Waiting 5s...")
    time.sleep(5)
    
    acquisition_start_time = time.time()
    
    # Licznik: dokąd już przetworzyliśmy dane w pamięci
    last_idx = 0
    
    start_loop = time.time()
    annotation = 1

    # Pętla (10 sekund)
    while time.time() - start_loop < 10:
        time.sleep(1) # Czekamy sekundę, zbierają się nowe dane
        
        print(f"Sending annotation {annotation}")
        eeg.annotate(str(annotation))
        annotation += 1
        
        # Pobranie stanu bufora
        eeg.get_mne()
        
        if eeg.data.mne_raw is not None:
            d, t = eeg.data.mne_raw.get_data(return_times=True)
            current_len = d.shape[1]
            
            # Jeśli przybyły nowe dane
            if current_len > last_idx:
                # Bierzemy TYLKO ten nowy kawałek (slice)
                new_data = d[:, last_idx:]
                new_times = t[last_idx:] + acquisition_start_time
                
                chunk_to_save = np.vstack((new_times, new_data)).T
                
                # 'w' - kasuje plik i wpisuje tylko ten nowy chunk
                with open(csv_filename, 'w') as f:
                    np.savetxt(f, chunk_to_save, delimiter=',', header=header_str, comments='')
                
                print(f"Overwritten CSV with {new_data.shape[1]} latest samples.")
                
                # Przesuwamy wskaźnik na koniec, żeby w następnej pętli nie brać tego samego
                last_idx = current_len

    print("Stopping...")
    eeg.stop_acquisition()
    mgr.disconnect()

# --- Koniec ---
eeg.data.save(f'./BrainAccessData/{time.strftime("%Y%m%d_%H%M")}-raw.fif')
eeg.close()

# Wykres całości
mne_raw = eeg.data.mne_raw
mne_raw.apply_function(lambda x: x*10**-6)
mne_raw.filter(1, 40).plot(scalings="auto", verbose=False)
plt.show()