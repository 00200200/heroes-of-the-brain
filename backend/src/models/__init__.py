import os
import glob
import numpy as np

from collections import deque
from src.models.focus_model import focus_service
from src.models.stress_model import stress_service
from src.models.tiredness_model import tiredness_service

# Bufor na 24 ostatnie odczyty EEG (2 minuty przy odczycie co 5s)
_eeg_buffer = deque(maxlen=24)
def mean_metrics():
	"""
	Zwraca uśrednione metryki (focus, stress, tiredness, timestamp) z ostatnich 2 minut (bufor EEG).
	"""
	import logging
	if len(_eeg_buffer) == 0:
		return None
	all_eeg = np.vstack([e for (ts, e) in _eeg_buffer])
	all_ts = [ts for (ts, e) in _eeg_buffer]
	mean_ts = float(np.mean(all_ts))
	beta = np.mean(all_eeg[:, :3], axis=1)
	alpha = np.mean(all_eeg[:, 3:6], axis=1)
	theta = np.mean(all_eeg[:, 6:8], axis=1)
	beta_val = beta.mean()
	alpha_val = alpha.mean()
	theta_val = theta.mean()
	# Użyj tych samych wzorów co modele
	# Focus
	min_beta = 5.0
	max_beta = 30.0
	norm_focus = (beta_val - min_beta) / (max_beta - min_beta)
	norm_focus = max(0.0, min(1.0, norm_focus))
	focus = int(norm_focus * 100)
	# Stress
	min_ratio = 0.5
	max_ratio = 2.0
	ratio = beta_val / (alpha_val + 0.01)
	norm_stress = (ratio - min_ratio) / (max_ratio - min_ratio)
	norm_stress = max(0.0, min(1.0, norm_stress))
	stress = int(norm_stress * 100)
	# Tiredness
	min_t = 1.0
	max_t = 4.0
	tired_ratio = (alpha_val + theta_val) / (beta_val + 0.01)
	norm_tired = (tired_ratio - min_t) / (max_t - min_t)
	norm_tired = max(0.0, min(1.0, norm_tired))
	tiredness = int(norm_tired * 100)
	logging.info(f"mean_metrics: focus={focus}, stress={stress}, tiredness={tiredness}, ts={mean_ts}")
	return {
		"timestamp": mean_ts,
		"focus_level": focus,
		"stress_level": stress,
		"tiredness_level": tiredness,
	}

def update_models_from_latest_csv():
	"""
	Wczytaj najnowszy plik snapshot.csv z BrainAccessData, wylicz pasma i zaktualizuj modele.
	(Wersja demo: pasma są symulowane jako proste statystyki z kanałów EEG)
	"""
	import logging
	data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../BrainAccessData')
	files = glob.glob(os.path.join(data_dir, '*-snapshot.csv'))
	logging.info(f"Znalezione pliki CSV: {files}")
	if not files:
		logging.warning("Brak plików snapshot.csv!")
		return
	latest = max(files, key=os.path.getmtime)
	logging.info(f"Używany plik: {latest}")
	arr = np.genfromtxt(latest, delimiter=',', skip_header=1)
	logging.info(f"Wczytana macierz: {arr}")
	if arr.ndim == 1:
		arr = arr[np.newaxis, :]
	timestamps = arr[:, 0]
	eeg = arr[:, 1:9]
	logging.info(f"Wycięte EEG: {eeg}")
	mean_ts = float(np.mean(timestamps))
	_eeg_buffer.append((mean_ts, eeg))
	if len(_eeg_buffer) == 0:
		logging.warning("Bufor EEG pusty!")
		return None
	# Modele aktualizujemy tylko na podstawie najnowszego pliku
	beta = np.mean(eeg[:, :3], axis=1)
	alpha = np.mean(eeg[:, 3:6], axis=1)
	theta = np.mean(eeg[:, 6:8], axis=1)
	logging.info(f"beta: {beta}, alpha: {alpha}, theta: {theta}")
	beta_val = beta.mean()
	alpha_val = alpha.mean()
	theta_val = theta.mean()
	logging.info(f"beta_val: {beta_val}, alpha_val: {alpha_val}, theta_val: {theta_val}")
	focus_service.calculate([beta_val])
	stress_service.calculate([alpha_val], [beta_val])
	tiredness_service.calculate([alpha_val], [theta_val], [beta_val])
	logging.info(f"focus: {focus_service.get_value()}, stress: {stress_service.get_value()}, tiredness: {tiredness_service.get_value()}")
	# Średni timestamp z bufora (do zwrotu w API)
	all_ts = [ts for (ts, e) in _eeg_buffer]
	mean_ts_buf = float(np.mean(all_ts))
	return mean_ts_buf
