import os
from dotenv import load_dotenv
load_dotenv()

# Camera
CAMERA_INDEX  = 0
FRAME_WIDTH   = 320
FRAME_HEIGHT  = 240
FPS_TARGET    = 10

# vdo.ninja (set USE_VDO_NINJA = True and paste your stream URL)
USE_VDO_NINJA = True
VDO_NINJA_URL = os.getenv("VDO_NINJA_URL", "")
# Example URL format:
# "https://vdo.ninja/?view=YOUR_ROOM_ID&codec=mjpeg&quality=0"

# Posture thresholds (overridden by calibration if set)
SLOUCH_ANGLE_THRESH = 15
HEAD_FORWARD_THRESH = 0.08

# Gemini — loaded from .env file
GEMINI_API_KEY       = os.getenv("GEMINI_API_KEY", "")
GEMINI_CHECK_INTERVAL = 5

# ElevenLabs — loaded from .env file
ELEVENLABS_API_KEY  = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")

# Backend
BACKEND_URL = os.getenv("BACKEND_URL", "http://45.76.137.251")
DEVICE_ID   = "focuspal-device-001"

# Debug
DEBUG_MODE = True