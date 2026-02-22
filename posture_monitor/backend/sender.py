import requests
import threading
import time
from config import BACKEND_URL, DEVICE_ID

class BackendSender:
    def __init__(self):
        try:
            response = requests.get(f"{BACKEND_URL}/api/status", timeout=3)
            if response.status_code == 200:
                cloud_data = response.json()
                prev_seconds = cloud_data.get("session_seconds", 0)
                self.session_start = time.time() - prev_seconds
                print(f"[Backend] Resumed session from cloud: {prev_seconds}s")
            else:
                self.session_start = time.time()
        except Exception as e:
            print(f"[Backend] Could not reach cloud to resume: {e}")
            self.session_start = time.time()

        self.queue = []
        self._start_worker()

    def send_event(self, analysis):
        event = {
            "device_id":    DEVICE_ID,
            "timestamp":    float(time.time()),
            "session_start": float(self.session_start),
            "slouching":    bool(analysis.get("slouching", False)),
            "on_phone":     bool(analysis.get("on_phone", False)),
            "attentive":    bool(analysis.get("attentive", True)),
            "torso_angle":  round(float(analysis.get("torso_angle", 0)), 2),
            "head_forward": round(float(analysis.get("head_forward", 0)), 3),
            "posture_score": self._calculate_score(analysis)
        }
        self.queue.append(event)

    def _calculate_score(self, analysis):
        score = 100
        if analysis.get("slouching"):    score -= 40
        if analysis.get("on_phone"):     score -= 40
        if not analysis.get("attentive"): score -= 20
        return int(max(0, score))

    def _start_worker(self):
        def _worker():
            while True:
                time.sleep(5)
                if self.queue:
                    batch = self.queue.copy()
                    self.queue.clear()
                    self._post_batch(batch)
        threading.Thread(target=_worker, daemon=True).start()

    def _post_batch(self, events):
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/events",
                json={"events": events},
                timeout=5
            )
            if response.status_code == 200:
                print(f"[Backend] Sent {len(events)} events")
            else:
                print(f"[Backend] Error {response.status_code}")
        except Exception as e:
            print(f"[Backend] Failed to send: {e}")