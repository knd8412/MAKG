import requests
import threading
import time
from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID

# Alert messages
ALERTS = {
    "slouching":    "Hey! Sit up straight, you're slouching.",
    "head_forward": "Your head is too far forward. Pull it back.",
    "phone":        "Put your phone down and focus!",
    "good":         "Great posture! Keep it up."
}

ALERT_COOLDOWN = 30  # seconds between same alert to avoid spam

class VoiceAlert:
    def __init__(self):
        self.last_alert_time = {}
        self.muted = False

    def mute(self):
        self.muted = True
        print("[Voice] Muted")

    def unmute(self):
        self.muted = False
        print("[Voice] Unmuted")

    def toggle_mute(self):
        if self.muted:
            self.unmute()
        else:
            self.mute()

    def _can_alert(self, alert_type):
        now = time.time()
        last = self.last_alert_time.get(alert_type, 0)
        return (now - last) > ALERT_COOLDOWN

    def _speak(self, text):
        """Calls ElevenLabs API and plays audio in a background thread."""
        def _run():
            try:
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
                headers = {
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json"
                }
                payload = {
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
                }
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    # Save and play audio
                    with open("/tmp/alert.mp3", "wb") as f:
                        f.write(response.content)
                    import subprocess
                    subprocess.run(["mpg123", "-q", "/tmp/alert.mp3"])
                else:
                    print(f"[ElevenLabs] Error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"[ElevenLabs] Exception: {e}")

        threading.Thread(target=_run, daemon=True).start()

    def alert(self, alert_type):
        if self.muted:
            return
        if not self._can_alert(alert_type):
            return
        text = ALERTS.get(alert_type, "")
        if text:
            print(f"[Voice] Saying: {text}")
            self.last_alert_time[alert_type] = time.time()
            self._speak(text)

    def check_and_alert(self, analysis):
        """Pass in the analysis dict from PostureAnalyzer and auto alert."""
        if analysis.get("on_phone"):
            self.alert("phone")
        elif analysis.get("slouching"):
            self.alert("slouching")
        elif not analysis.get("attentive"):
            self.alert("head_forward")