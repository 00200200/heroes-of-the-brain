import os
import glob
import numpy as np
from src.models.focus_model import focus_service
from src.models.stress_model import stress_service
from src.models.tiredness_model import tiredness_service

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
	# EEG: kolumny 1:9 (8 kanałów)
	eeg = arr[:, 1:9]
	logging.info(f"Wycięte EEG: {eeg}")
	# Demo: beta = mean z kanałów 0,1,2; alpha = mean z kanałów 3,4,5; theta = mean z kanałów 6,7
	beta = np.mean(eeg[:, :3], axis=1)
	alpha = np.mean(eeg[:, 3:6], axis=1)
	theta = np.mean(eeg[:, 6:8], axis=1)
	logging.info(f"beta: {beta}, alpha: {alpha}, theta: {theta}")
	# Uśrednij po czasie
	beta_val = beta.mean()
	alpha_val = alpha.mean()
	theta_val = theta.mean()
	logging.info(f"beta_val: {beta_val}, alpha_val: {alpha_val}, theta_val: {theta_val}")
	# Aktualizuj modele
	focus_service.calculate([beta_val])
	stress_service.calculate([alpha_val], [beta_val])
	tiredness_service.calculate([alpha_val], [theta_val], [beta_val])
	logging.info(f"focus: {focus_service.get_value()}, stress: {stress_service.get_value()}, tiredness: {tiredness_service.get_value()}")
