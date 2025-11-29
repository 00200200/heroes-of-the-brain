"""Stress model utilities.

This module provides a simple stress estimator based on the ratio of
beta to alpha EEG waves. The ratio is normalized and scaled to a 0-100
integer range.
"""

import numpy as np
from typing import List


class StressModel:
    """Estimate stress using beta/alpha ratio.

    Attributes:
        _level (int): Cached stress level scaled 0-100.
    """

    def __init__(self):
        self._level = 0

    def calculate(self, alpha: List[float], beta: List[float]) -> None:
        """Calculate and update the stress level.

        Args:
            alpha: Sequence of alpha-wave amplitudes.
            beta: Sequence of beta-wave amplitudes.

        Side effects:
            Updates the internal `_level` attribute.
        """
        # Stress: znormalizuj beta/alpha do zakresu 0.5-2.0
        if not alpha or not beta:
            return
        ratio = np.mean(beta) / (np.mean(alpha) + 0.01)
        min_ratio = 0.5
        max_ratio = 2.0
        norm = (ratio - min_ratio) / (max_ratio - min_ratio)
        norm = max(0.0, min(1.0, norm))
        self._level = int(norm * 100)

    def get_value(self) -> int:
        """Return the last-computed stress level.

        Returns:
            int: Stress level scaled 0-100.
        """
        return self._level


stress_service = StressModel()