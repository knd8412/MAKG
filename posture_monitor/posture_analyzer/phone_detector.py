from google import genai
from google.genai import types
import cv2
import base64
import time
from config import GEMINI_API_KEY, GEMINI_CHECK_INTERVAL


class PhoneDetector:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.last_check = 0
        self.last_result = False
        print("[Gemini] PhoneDetector ready")

    def _frame_to_base64(self, frame):
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        return base64.b64encode(buffer).decode('utf-8')

    def detect_phone_use(self, frame, landmarks=None):
        now = time.time()
        if now - self.last_check < GEMINI_CHECK_INTERVAL:
            return self.last_result

        try:
            img_data = self._frame_to_base64(frame)
            image_part = types.Part.from_bytes(
                data=base64.b64decode(img_data),
                mime_type="image/jpeg"
            )
            prompt = (
                "Look at this image. Is the person holding a phone, looking at a phone, "
                "or has a phone near their face or hands? "
                "Reply with only YES or NO."
            )
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, image_part]
            )
            result = "YES" in response.text.upper()
            self.last_result = result
            self.last_check = now
            print(f"[Gemini] Phone detected: {result}")
            return result

        except Exception as e:
            print(f"[Gemini] Error: {e}")
            self.last_check = now  # still update timer so we don't spam on error
            return self.last_result