# Camera
CAMERA_INDEX = 0
FRAME_WIDTH, FRAME_HEIGHT = 320, 240
FPS_TARGET = 10

# Posture thresholds (overridden by calibration if set)
SLOUCH_ANGLE_THRESH = 160
HEAD_FORWARD_THRESH = 0.08

# Gemini
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
GEMINI_CHECK_INTERVAL = 5  # seconds between Gemini API calls (save quota)

# ElevenLabs
ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"
ELEVENLABS_VOICE_ID = "YOUR_VOICE_ID"  # get from elevenlabs.io dashboard

# Backend
BACKEND_URL = "http://45.76.137.251"
DEVICE_ID = "focuspal-device-001"

# Debug
DEBUG_MODE = True