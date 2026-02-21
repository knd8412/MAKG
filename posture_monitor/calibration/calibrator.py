import numpy as np
import json
import os

CALIBRATION_FILE = "/tmp/calibration.json"

class Calibrator:
    def __init__(self):
        self.baseline = None
        self.calibrated = False
        self._load()

    def calibrate(self, analysis):
        """
        Called when calibrate button is pressed.
        Saves current posture angles as the user's personal baseline.
        """
        self.baseline = {
            "torso_angle": analysis["torso_angle"],
            "head_forward": analysis["head_forward"]
        }
        self.calibrated = True
        self._save()
        print(f"[Calibration] Baseline set: {self.baseline}")

    def get_thresholds(self):
        """
        Returns personalised thresholds based on calibration.
        Falls back to config defaults if not calibrated.
        """
        if not self.calibrated or self.baseline is None:
            from config import SLOUCH_ANGLE_THRESH, HEAD_FORWARD_THRESH
            return SLOUCH_ANGLE_THRESH, HEAD_FORWARD_THRESH

        # Allow 15 degree wiggle room below their calibrated torso angle
        torso_thresh = self.baseline["torso_angle"] - 15
        # Allow 50% more head forward movement than their baseline
        head_thresh = self.baseline["head_forward"] * 1.5
        return torso_thresh, head_thresh

    def _save(self):
        with open(CALIBRATION_FILE, "w") as f:
            json.dump(self.baseline, f)

    def _load(self):
        if os.path.exists(CALIBRATION_FILE):
            with open(CALIBRATION_FILE, "r") as f:
                self.baseline = json.load(f)
                self.calibrated = True
                print(f"[Calibration] Loaded saved baseline: {self.baseline}")