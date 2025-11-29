"""Focus model utilities.

This module estimates a user's focus level from EEG beta wave inputs.
The model averages the provided beta wave values and scales them to an
integer in the 0-100 range.
"""

import numpy as np
from typing import List


class FocusModel:
    """Estimate focus from EEG beta waves.

    Attributes:
        _level (int): Cached focus level in the range 0-100.
    """

    def __init__(self):
        self._level = 0

    def calculate(self, beta: List[float]) -> None:
        """Calculate and update the focus level.

        Args:
            beta: List of beta-wave amplitude values. If empty or falsy,
                the method does nothing.

        Side effects:
            Updates `_level` with an integer between 0 and 100.
        """
        # Focus: znormalizuj mean(beta) do zakresu 5-30uV²
        if not beta:
            return
        min_beta = 5.0
        max_beta = 30.0
        val = np.mean(beta)
        norm = (val - min_beta) / (max_beta - min_beta)
        norm = max(0.0, min(1.0, norm))
        self._level = int(norm * 100)

    def get_value(self) -> int:
        """Return the last-computed focus level.

        Returns:
            int: Focus level scaled 0-100.
        """
        return self._level


focus_service = FocusModel()