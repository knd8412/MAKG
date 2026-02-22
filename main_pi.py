"""
Posture Brain v1 - Raspberry Pi Client
Hackathons UK - Pi 5 Image
Description: Monitors physical button inputs and sends posture state 
updates to the Vultr Cloud API.
"""

import time
import requests
import board
from digitalio import DigitalInOut, Direction, Pull

# --- CONFIGURATION ---
VULTR_IP = "http://45.76.137.251"
API_BASE = f"{VULTR_IP}/api/button"

# --- HARDWARE SETUP ---
# Pin Mapping: BTN 1 (Start/Stop), BTN 2 (Calibrate), BTN 3 (Alert), BTN 4 (Reset)
BUTTON_CONFIG = [
    {"pin": board.D17, "label": "toggle", "name": "START/STOP"},
    {"pin": board.D27, "label": "calibrate", "name": "CALIBRATE"},
    {"pin": board.D22, "label": "alert-toggle", "name": "TOGGLE ALERT"},
    {"pin": board.D23, "label": "reset", "name": "SYSTEM RESET"}
]

buttons = []

for cfg in BUTTON_CONFIG:
    btn = DigitalInOut(cfg["pin"])
    btn.direction = Direction.INPUT
    btn.pull = Pull.UP # Internal resistor pulls to 3.3V
    buttons.append({"obj": btn, "label": cfg["label"], "name": cfg["name"]})

def log_event(action, result):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {action} -> {result}")

def send_to_cloud(endpoint, action_name):
    try:
        url = f"{API_BASE}/{endpoint}"
        response = requests.post(url, timeout=3)
        if response.status_code == 200:
            log_event(action_name, f"SUCCESS ({response.json().get('status')})")
        else:
            log_event(action_name, f"SERVER ERROR ({response.status_code})")
    except Exception as e:
        log_event(action_name, "CONNECTION FAILED (Check Pi Wi-Fi)")

# --- MAIN RUNTIME ---
if __name__ == "__main__":
    print("🚀 Posture Brain Client: ONLINE")
    print("Listening for hardware interrupts...")
    
    try:
        while True:
            for btn in buttons:
                # Active Low: button.value is False when pressed
                if not btn["obj"].value:
                    send_to_cloud(btn["label"], btn["name"])
                    time.sleep(0.6) # Debounce delay
            
            time.sleep(0.05) # Power saving
    except KeyboardInterrupt:
        print("\nClient safely disconnected.")