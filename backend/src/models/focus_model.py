"""Focus model utilities.

This module estimates a user's focus level from EEG beta and theta wave inputs.
Najczęściej stosowany wskaźnik biologiczny to stosunek beta/theta (im wyższy, tym większa koncentracja).
Model używa logarytmicznego skalowania wskaźnika beta/theta do zakresu 0-100.
"""

import numpy as np



class FocusModel:
    """Estimate focus from EEG beta and theta waves (biological index: beta/theta).

    Attributes:
        _level (int): Cached focus level in the range 0-100.
    """

    def __init__(self):
        self._level = 0

    def calculate(self, beta: list[float], theta: list[float]) -> None:
        """Calculate and update the focus level using beta/theta ratio (logarithmic scaling).

        Args:
            beta: List of beta-wave amplitude values.
            theta: List of theta-wave amplitude values.
        """
        if not beta or not theta:
            return
        ratio = np.mean(beta) / (np.mean(theta) + 0.01)
        log_ratio = np.log(ratio + 1)
        # log(4) ~ 1.386, ratio=3 maps to 100
        level = min(100, max(0, int((log_ratio / np.log(4)) * 100)))
        self._level = level
        # Optional: log info for debugging
        # import logging
        # logging.getLogger(__name__).info(
        #     "FocusModel: beta=%.3f, theta=%.3f, ratio=%.3f, log_ratio=%.3f, level=%d",
        #     np.mean(beta), np.mean(theta), ratio, log_ratio, level,
        # )

    def get_value(self) -> int:
        """Return the last-computed focus level.

        Returns:
            int: Focus level scaled 0-100.

        """
        return self._level


focus_service = FocusModel()
