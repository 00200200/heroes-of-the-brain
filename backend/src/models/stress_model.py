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

    def calculate(self, stress_metric: list[float], dummy: list[float] = None) -> None:
        """Calculate and update the stress level using FAA + beta/alpha.

        Args:
            stress_metric: List of stress index values (FAA + beta/alpha).
            dummy: Unused, for compatibility.
        """
        val = np.mean(stress_metric)
        # Normalizacja: typowo FAA+beta/alpha w okolicach 0-5, mapujemy 0-5 na 0-100
        norm = np.clip((val + 2.5) / 5.0, 0.0, 1.0)
        if not np.isfinite(norm):
            self._level = 0
        else:
            self._level = int(norm * 100)
        logging.getLogger(__name__).info(
            "StressModel: stress_metric=%.3f, level=%d",
            val, self._level,
        )

    def get_value(self) -> int:
        """Return the last-computed stress level.

        Returns:
            int: Stress level scaled 0-100.

        """
        return self._level


stress_service = StressModel()
