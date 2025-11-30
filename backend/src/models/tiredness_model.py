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

    def calculate(self, alpha: list[float], theta: list[float], beta: list[float]) -> None:
        """Calculate and update the tiredness level (logarithmic scaling)."""
        if not alpha or not theta or not beta:
            return
        numerator = np.mean(alpha) + np.mean(theta)
        denominator = np.mean(beta) + 0.01  # Small epsilon to avoid division by zero
        tiredness = numerator / denominator
        log_tiredness = np.log(tiredness + 1)
        # log(4) ~ 1.386, so tiredness=3 maps to 100
        level = min(100, max(0, int((log_tiredness / np.log(4)) * 100)))
        self._level = level
        logging.getLogger(__name__).info(
            "TirednessModel: alpha=%.3f, theta=%.3f, beta=%.3f, numerator=%.3f, denominator=%.3f, tiredness=%.3f, log_tiredness=%.3f, level=%d",
            np.mean(alpha), np.mean(theta), np.mean(beta), numerator, denominator, tiredness, log_tiredness, level,
        )

    def get_value(self) -> int:
        """Return the last-computed tiredness level.

        Returns:
            int: Tiredness level scaled 0-100.

        """
        return self._level


tiredness_service = TirednessModel()
