# MAKG
Assistance device that monitor your posture, study's session and lots of other features

# Posture Brain (IoT Component)
**Built for Raspberry Pi 5**

### Hardware Specifications
- **Controller:** Raspberry Pi 5 (8GB)
- **Input:** 4x Tactile Buttons (GPIO 17, 27, 22, 23)
- **Communication:** REST API via Python Requests
- **Logic:** Active Low with Internal Pull-Ups

### Installation
1. Enable I2C via `raspi-config`.
2. Install dependencies:
   `pip install requests adafruit-circuitpython-ssd1306 Pillow`
3. Run: `python3 main_pi.py`