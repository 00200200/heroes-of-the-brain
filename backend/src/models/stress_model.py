"""Stress model utilities.

This module provides a simple stress estimator based on the ratio of
beta to alpha EEG waves. The ratio is normalized and scaled to a 0-100
integer range. Uses logger for debug information.
"""

import logging

import numpy as np


class StressModel:
    """Estimate stress using beta/alpha ratio.

    Attributes:
        _level (int): Cached stress level scaled 0-100.

    """

    def __init__(self):
        self._level = 0

    def calculate(self, alpha: list[float], beta: list[float]) -> None:
        """Calculate and update the stress level (logarithmic scaling)."""
        if not alpha or not beta:
            return
        ratio = np.mean(beta) / (np.mean(alpha) + 0.01)
        # Logarithmic scaling for robustness
        log_ratio = np.log(ratio + 1)
        # log(4) ~ 1.386, so ratio=3 maps to 100
        level = min(100, max(0, int((log_ratio / np.log(4)) * 100)))
        self._level = level
        logging.getLogger(__name__).info(
            "StressModel: alpha=%.3f, beta=%.3f, ratio=%.3f, log_ratio=%.3f, level=%d",
            np.mean(alpha), np.mean(beta), ratio, log_ratio, level,
        )

    def get_value(self) -> int:
        """Return the last-computed stress level.

        Returns:
            int: Stress level scaled 0-100.

        """
        return self._level


stress_service = StressModel()
