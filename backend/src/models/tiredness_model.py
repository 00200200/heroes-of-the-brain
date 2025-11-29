"""Tiredness model utilities.

This module estimates a user's tiredness level from EEG waves using the
formula: tiredness = (alpha + theta) / beta, where all inputs are
averaged and the result is scaled to a 0-100 integer range.
"""

import numpy as np
from typing import List


class TirednessModel:
    """Estimate tiredness from EEG alpha, theta, and beta waves.

    Attributes:
        _level (int): Cached tiredness level in the range 0-100.

    Example:
        >>> m = TirednessModel()
        >>> m.calculate([10.0, 20.0], [5.0, 15.0], [8.0, 12.0])
        >>> isinstance(m.get_value(), int)
        True
    """

    def __init__(self):
        self._level = 0

    def calculate(self, alpha: List[float], theta: List[float], beta: List[float]) -> None:
        """Calculate and update the tiredness level.

        The formula used is: tiredness = (mean(alpha) + mean(theta)) / mean(beta).
        The result is scaled to a 0-100 integer range.

        Args:
            alpha: List of alpha-wave amplitude values.
            theta: List of theta-wave amplitude values.
            beta: List of beta-wave amplitude values.

        Side effects:
            Updates the internal `_level` attribute with an integer value
            between 0 and 100. If any input list is empty or falsy, the
            method does nothing.
        """
        # Tiredness = (alpha + theta) / beta
        if not alpha or not theta or not beta:
            return
        numerator = np.mean(alpha) + np.mean(theta)
        denominator = np.mean(beta) + 0.01  # Small epsilon to avoid division by zero
        self._level = min(100, abs(int((numerator / denominator / 3.0) * 100)))

    def get_value(self) -> int:
        """Return the last-computed tiredness level.

        Returns:
            int: Tiredness level scaled 0-100.
        """
        return self._level


tiredness_service = TirednessModel()