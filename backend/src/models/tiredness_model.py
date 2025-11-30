"""Tiredness model utilities.

This module estimates a user's tiredness level from EEG waves using the
formula: tiredness = (alpha + theta) / beta, where all inputs are
averaged and the result is scaled to a 0-100 integer range. Uses logger for debug information.
"""

import logging

import numpy as np


class TirednessModel:
    """Estimate tiredness from EEG alpha, theta, and beta waves.

    Attributes:
        _level (int): Cached tiredness level in the range 0-100.

    """

    def __init__(self):
        self._level = 0

    def calculate(self, tiredness_metric: list[float], dummy1: list[float] = None, dummy2: list[float] = None) -> None:
        """Calculate and update the tiredness level using relative (theta+alpha)/total power.

        Args:
            tiredness_metric: List of relative tiredness values.
            dummy1, dummy2: Unused, for compatibility.
        """
        val = np.mean(tiredness_metric)
        # Norm: map from 0..1 to 0..1
        norm = np.clip(val, 0.0, 1.0)
        self._level = int(norm * 100)
        logging.getLogger(__name__).info(
            "TirednessModel: tiredness_metric=%.3f, level=%d",
            val, self._level,
        )

    def get_value(self) -> int:
        """Return the last-computed tiredness level.

        Returns:
            int: Tiredness level scaled 0-100.

        """
        return self._level


tiredness_service = TirednessModel()
