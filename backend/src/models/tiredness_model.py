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
        """Calculate and update the tiredness level.

        The formula used is: tiredness = (mean(alpha) + mean(theta)) / mean(beta).
        The result is scaled to a 0-100 integer range. Logs the computed numerator, denominator, and level.

        Args:
            alpha (list[float]): List of alpha-wave amplitude values.
            theta (list[float]): List of theta-wave amplitude values.
            beta (list[float]): List of beta-wave amplitude values.

        Side effects:
            Updates the internal _level attribute with an integer value
            between 0 and 100. If any input list is empty or falsy, the
            method does nothing. Logs the computation.

        """
        if not alpha or not theta or not beta:
            return
        numerator = np.mean(alpha) + np.mean(theta)
        denominator = np.mean(beta) + 0.01  # Small epsilon to avoid division by zero
        level = min(100, max(0, int((numerator / denominator / 3.0) * 100)))
        self._level = level
        logging.getLogger(__name__).info(
            "TirednessModel: alpha=%.3f, theta=%.3f, beta=%.3f, numerator=%.3f, denominator=%.3f, level=%d",
            np.mean(alpha), np.mean(theta), np.mean(beta), numerator, denominator, level,
        )

    def get_value(self) -> int:
        """Return the last-computed tiredness level.

        Returns:
            int: Tiredness level scaled 0-100.

        """
        return self._level


tiredness_service = TirednessModel()
