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
        """Calculate and update the stress level.

        The method computes the mean of beta divided by mean of alpha (with
        a small epsilon to avoid division by zero), normalizes the ratio,
        and clamps the result to the 0-100 integer range. Logs the computed ratio and level.

        Args:
            alpha (list[float]): Sequence of alpha-wave amplitudes.
            beta (list[float]): Sequence of beta-wave amplitudes.

        Side effects:
            Updates the internal _level attribute.
            Logs the computed ratio and level.

        """
        if not alpha or not beta:
            return
        ratio = np.mean(beta) / (np.mean(alpha) + 0.01)
        level = min(100, max(0, int((ratio / 3.0) * 100)))
        self._level = level
        logging.getLogger(__name__).info(
            "StressModel: alpha=%.3f, beta=%.3f, ratio=%.3f, level=%d",
            np.mean(alpha), np.mean(beta), ratio, level,
        )

    def get_value(self) -> int:
        """Return the last-computed stress level.

        Returns:
            int: Stress level scaled 0-100.

        """
        return self._level


stress_service = StressModel()
