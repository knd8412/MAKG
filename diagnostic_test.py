"""
Posture Brain - Hardware Diagnostic Tool
Use this to verify physical wiring before launching cloud services.
"""

import board
from digitalio import DigitalInOut, Direction, Pull
import time

pins = [board.D17, board.D27, board.D22, board.D23]
labels = ["BTN1 (Start)", "BTN2 (Calib)", "BTN3 (Alert)", "BTN4 (Reset)"]
btns = []

for p in pins:
    b = DigitalInOut(p)
    b.direction = Direction.INPUT
    b.pull = Pull.UP
    btns.append(b)

print("--- HARDWARE TEST MODE ---")
print("Press buttons to verify wiring...")

try:
    while True:
        states = []
        for i, b in enumerate(btns):
            if not b.value:
                print(f"✅ DETECTED: {labels[i]} on GPIO {pins[i]}")
        time.sleep(0.2)
except KeyboardInterrupt:
    print("Test ended.")