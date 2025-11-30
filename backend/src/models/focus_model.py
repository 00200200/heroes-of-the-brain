"""Focus model utilities.

This module estimates a user's focus level from EEG beta wave inputs.
The model averages the provided beta wave values and scales them to an
integer in the 0-100 range.
"""

import numpy as np


class FocusModel:
    """Estimate focus from EEG beta waves.

    Attributes:
        _level (int): Cached focus level in the range 0-100.

    """

    def __init__(self):
        self._level = 0
        # Adaptacyjny zakres normalizacji
        self._min = 0.1  # domyślny dolny zakres (bardziej czuły)
        self._max = 1.0  # domyślny górny zakres (bardziej czuły)

    def calculate(self, focus_ratio: list[float]) -> None:
        """Calculate and update the focus level using adaptive normalization (beta/theta).

        Args:
            focus_ratio: List of beta/theta values.
        """
        val = np.mean(focus_ratio)
        # Adaptacyjna aktualizacja zakresu
        if val < self._min:
            self._min = val
        if val > self._max:
            self._max = val
        # Zabezpieczenie przed zbyt małym zakresem
        eps = 1e-3
        rng = max(self._max - self._min, eps)
        norm = (val - self._min) / rng
        norm = np.clip(norm, 0.0, 1.0)
        self._level = int(norm * 100)

    def get_value(self) -> int:
        """Return the last-computed focus level.

        Returns:
            int: Focus level scaled 0-100.

        """
        return self._level


focus_service = FocusModel()
