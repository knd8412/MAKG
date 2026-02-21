import requests
import threading
import time
from config import BACKEND_URL, DEVICE_ID

class BackendSender:
    def __init__(self):
        self.session_start = time.time()
        self.queue = []
        self._start_worker()

    def send_event(self, analysis):
        """
        Queues a posture event to send to the backend.
        Non-blocking — runs in background thread.
        """
        event = {
            "device_id": DEVICE_ID,
            "timestamp": time.time(),
            "session_start": self.session_start,
            "slouching": analysis.get("slouching", False),
            "on_phone": analysis.get("on_phone", False),
            "attentive": analysis.get("attentive", True),
            "torso_angle": round(analysis.get("torso_angle", 0), 2),
            "head_forward": round(analysis.get("head_forward", 0), 3),
            "posture_score": self._calculate_score(analysis)
        }
        self.queue.append(event)

    def _calculate_score(self, analysis):
        """Simple 0-100 focus/posture score."""
        score = 100
        if analysis.get("slouching"):
            score -= 40
        if analysis.get("on_phone"):
            score -= 40
        if not analysis.get("attentive"):
            score -= 20
        return max(0, score)

    def _start_worker(self):
        """Background thread that drains the queue every 5 seconds."""
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