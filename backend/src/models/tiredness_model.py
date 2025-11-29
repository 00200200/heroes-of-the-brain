"""Tiredness model utilities.

This module provides a lightweight model to estimate a user's tiredness
level based on EEG alpha wave measurements.

The implementation is intentionally simple: it averages the provided
alpha wave values and scales the result to a 0-100 integer range.
"""

import numpy as np
from typing import List


class TirednessModel:
    """Estimate tiredness from EEG alpha waves.

    Attributes:
        _level (int): Cached tiredness level in the range 0-100.

    Example:
        >>> m = TirednessModel()
        >>> m.calculate([10.0, 20.0])
        >>> isinstance(m.get_value(), int)
        True
    """

    def __init__(self):
        self._level = 0

    def calculate(self, alpha: List[float]) -> None:
        """Calculate and update the tiredness level.

        Args:
            alpha: A list of alpha-wave amplitude values (floats). If the
                list is empty or falsy, the method does nothing.

        Side effects:
            Updates the internal `_level` attribute with an integer value
            between 0 and 100.
        """
        # Tiredness mainly depends on alpha waves
        if not alpha:
            return
        self._level = min(100, int((np.mean(alpha) / 50.0) * 100))

    def get_value(self) -> int:
        """Return the last-computed tiredness level.

        Returns:
            int: Tiredness level scaled 0-100.
        """
        return self._level


tiredness_service = TirednessModel()