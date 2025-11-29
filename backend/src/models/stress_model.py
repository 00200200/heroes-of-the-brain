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

        The method computes the mean of beta divided by mean of alpha (with
        a small epsilon to avoid division by zero), normalizes the ratio,
        and clamps the result to the 0-100 integer range.

        Args:
            alpha: Sequence of alpha-wave amplitudes.
            beta: Sequence of beta-wave amplitudes.

        Side effects:
            Updates the internal `_level` attribute.
        """
        # Beta/Alpha ratio for stress estimation
        if not alpha or not beta:
            return
        ratio = np.mean(beta) / (np.mean(alpha) + 0.01)
        self._level = min(100, int((ratio / 3.0) * 100))

    def get_value(self) -> int:
        """Return the last-computed stress level.

        Returns:
            int: Stress level scaled 0-100.
        """
        return self._level


stress_service = StressModel()