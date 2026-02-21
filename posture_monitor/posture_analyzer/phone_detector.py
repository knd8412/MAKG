import google.generativeai as genai
import cv2
import base64
import time
from config import GEMINI_API_KEY, GEMINI_CHECK_INTERVAL

genai.configure(api_key=GEMINI_API_KEY)

class PhoneDetector:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.last_check = 0
        self.last_result = False  # cache result between checks

    def _frame_to_base64(self, frame):
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        return base64.b64encode(buffer).decode('utf-8')

    def detect_phone_use(self, frame, landmarks=None):
        """
        Uses Gemini Vision to detect if person is holding/looking at a phone.
        Only calls API every GEMINI_CHECK_INTERVAL seconds to save quota and speed.
        """
        now = time.time()
        if now - self.last_check < GEMINI_CHECK_INTERVAL:
            return self.last_result  # return cached result

        try:
            img_data = self._frame_to_base64(frame)
            image_part = {
                "mime_type": "image/jpeg",
                "data": img_data
            }
            prompt = (
                "Look at this image. Is the person holding a phone, looking at a phone, "
                "or has a phone near their face or hands? "
                "Reply with only YES or NO."
            )
            response = self.model.generate_content([prompt, image_part])
            result = "YES" in response.text.upper()
            self.last_result = result
            self.last_check = now
            print(f"[Gemini] Phone detected: {result}")
            return result

        except Exception as e:
            print(f"[Gemini] Error: {e}")
            return self.last_result  # fallback to last known result