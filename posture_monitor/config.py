# Tune these for your setup
CAMERA_INDEX = 0  # Laptop: 0 (built-in), Pi: 0 (USB) or 1 (Pi Cam CSI)
FRAME_WIDTH, FRAME_HEIGHT = 320, 240  # Low res for Pi speed
FPS_TARGET = 10
SLOUCH_ANGLE_THRESH = 160  # Degrees (higher = more upright)
HEAD_FORWARD_THRESH = 0.8  # Normalised offset
DEBUG_MODE = True  # Toggle prints
