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
        # Focus mainly depends on beta waves
        if not beta:
            return
        self._level = min(100, int((np.mean(beta) / 50.0) * 100))

    def get_value(self) -> int:
        """Return the last-computed focus level.

        Returns:
            int: Focus level scaled 0-100.
        """
        return self._level


focus_service = FocusModel()