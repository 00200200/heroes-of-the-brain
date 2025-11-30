"""
Pomodoro session model for adaptive focus and tiredness tracking.
"""

import time
from src.models.metrics_buffer import mean_metrics

class PomodoroSession:
    def __init__(self, min_baseline_minutes=10, min_session=15, max_session=40, min_break=5, max_break=20, threshold=0.7):
        """
        Args:
            min_baseline_minutes (int): How many minutes to collect baseline.
            min_session (int): Minimal session length (minutes).
            max_session (int): Maximal session length (minutes).
            min_break (int): Minimal break length (minutes).
            max_break (int): Maximal break length (minutes).
            threshold (float): Fraction (0-1) below which session should be cut short.
        """
        self.min_baseline_minutes = min_baseline_minutes
        self.min_session = min_session
        self.max_session = max_session
        self.min_break = min_break
        self.max_break = max_break
        self.threshold = threshold
        self.start_time = None
        self.baseline_focus = []
        self.baseline_tiredness = []
        self.active = False
        self.unlocked = False
        self.history = []  # (timestamp, focus, tiredness, pomodoro_score)

    def collect_baseline(self):
        """Collect baseline metrics for the first N minutes."""
        metrics = mean_metrics()
        if metrics is not None:
            self.baseline_focus.append(metrics["focus_level"])
            self.baseline_tiredness.append(metrics["tiredness_level"])
        # Unlock after min_baseline_minutes
        if len(self.baseline_focus) >= self.min_baseline_minutes:
            self.unlocked = True
            self.baseline_focus_val = int(sum(self.baseline_focus) / len(self.baseline_focus))
            self.baseline_tiredness_val = int(sum(self.baseline_tiredness) / len(self.baseline_tiredness))

    def start(self):
        """Start a new pomodoro session after baseline is collected."""
        if not self.unlocked:
            raise RuntimeError("Baseline not collected yet. Wait for baseline period to finish.")
        self.start_time = time.time()
        self.active = True
        self.history = [(self.start_time, self.baseline_focus_val, self.baseline_tiredness_val, self.pomodoro_score(self.baseline_focus_val, self.baseline_tiredness_val))]

    def check(self):
        """Check current metrics and compare to baseline. Returns True if session should continue, False if should be cut short."""
        if not self.active:
            raise RuntimeError("Session not started.")
        metrics = mean_metrics()
        if metrics is None:
            return True  # Not enough data, keep going
        focus = metrics["focus_level"]
        tiredness = metrics["tiredness_level"]
        score = self.pomodoro_score(focus, tiredness)
        self.history.append((time.time(), focus, tiredness, score))
        # If focus or score drops below threshold of baseline, suggest to cut session
        if (focus < self.baseline_focus_val * self.threshold) or (score < self.pomodoro_score(self.baseline_focus_val, self.baseline_tiredness_val) * self.threshold):
            return False
        return True

    def get_session_length(self):
        """Return session length in minutes, scaled by baseline focus (higher focus = longer session)."""
        if not self.unlocked:
            return None
        # Linear scaling between min_session and max_session
        focus_norm = self.baseline_focus_val / 100
        return int(self.min_session + (self.max_session - self.min_session) * focus_norm)

    def get_break_length(self):
        """Return break length in minutes, scaled by baseline tiredness (higher tiredness = longer break)."""
        if not self.unlocked:
            return None
        tired_norm = self.baseline_tiredness_val / 100
        return int(self.min_break + (self.max_break - self.min_break) * tired_norm)

    @staticmethod
    def pomodoro_score(focus, tiredness):
        """Simple score: focus minus tiredness."""
        return focus - tiredness

def generate_pomodoro_schedule(
    session_length=25, break_length=5, long_break_length=20, cycles=4, start_time=None
):
    """
    Generate a classic Pomodoro schedule as a list of dicts (JSON-ready).
    Args:
        session_length (int): Length of a single work session in minutes.
        break_length (int): Length of a short break in minutes.
        long_break_length (int): Length of a long break after 4 sessions.
        cycles (int): Number of work/break cycles before long break.
        start_time (float): Optional, epoch seconds for schedule start (default: now).
    Returns:
        list[dict]: List of schedule events (type, start, end, length_min).
    """
    if start_time is None:
        start_time = time.time()
    schedule = []
    current = start_time
    for i in range(1, cycles + 1):
        # Work session
        session_start = current
        session_end = current + session_length * 60
        schedule.append({
            "type": "work",
            "number": i,
            "start": session_start,
            "end": session_end,
            "length_min": session_length,
        })
        current = session_end
        # Break
        if i < cycles:
            break_end = current + break_length * 60
            schedule.append({
                "type": "break",
                "number": i,
                "start": current,
                "end": break_end,
                "length_min": break_length,
            })
            current = break_end
        else:
            # Long break after last session
            long_break_end = current + long_break_length * 60
            schedule.append({
                "type": "long_break",
                "number": i,
                "start": current,
                "end": long_break_end,
                "length_min": long_break_length,
            })
            current = long_break_end
    return schedule

class PomodoroStepper:
    """
    Stepper for classic Pomodoro cycles. Allows progressing through steps and returning a single step in JSON format.
    """
    def __init__(self, session_length=25, break_length=5, long_break_length=20, cycles=4):
        self.session_length = session_length
        self.break_length = break_length
        self.long_break_length = long_break_length
        self.cycles = cycles
        self.current_step = 0  # 0 = pierwszy work
        self.steps = self._build_steps()

    def _build_steps(self):
        steps = []
        for i in range(1, self.cycles + 1):
            steps.append({
                "type": "work",
                "number": i,
                "length_min": self.session_length,
            })
            if i < self.cycles:
                steps.append({
                    "type": "break",
                    "number": i,
                    "length_min": self.break_length,
                })
            else:
                steps.append({
                    "type": "long_break",
                    "number": i,
                    "length_min": self.long_break_length,
                })
        return steps

    def next_step(self):
        """Return the next step in the Pomodoro cycle, or None if finished."""
        if self.current_step >= len(self.steps):
            return None
        step = self.steps[self.current_step]
        self.current_step += 1
        return step

    def reset(self):
        self.current_step = 0
