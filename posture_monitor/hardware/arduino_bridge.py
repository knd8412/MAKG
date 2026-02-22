import serial
import threading
import time
import glob
import sys

class ArduinoBridge:
    def __init__(self, baud_rate=9600):
        self.ser = None
        self.baud_rate = baud_rate
        self.latest_command = None
        self.running = True
        self._connect()
        self._start_reader()

    def _find_port(self):
        ports = []
        if sys.platform == "darwin":
            ports = glob.glob("/dev/tty.usbmodem*") + glob.glob("/dev/tty.usbserial*")
        elif sys.platform.startswith("linux"):
            ports = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
        return ports[0] if ports else None

    def _connect(self):
        port = self._find_port()
        if port:
            try:
                self.ser = serial.Serial(port, self.baud_rate, timeout=1)
                time.sleep(3)
                print(f"[Arduino] Connected on {port}")
            except Exception as e:
                print(f"[Arduino] Failed to connect: {e}")
                self.ser = None
        else:
            print("[Arduino] No Arduino found — running in keyboard-only mode")

    def _start_reader(self):
        def _read():
            while self.running:
                if self.ser and self.ser.in_waiting:
                    try:
                        line = self.ser.readline().decode('utf-8').strip()
                        if len(line) > 2:
                            print(f"[Arduino] Received: {line}")
                            self.latest_command = line
                    except Exception as e:
                        print(f"[Arduino] Read error: {e}")
                time.sleep(0.05)
        threading.Thread(target=_read, daemon=True).start()

    def get_command(self):
        cmd = self.latest_command
        self.latest_command = None
        return cmd

    def send_posture_data(self, score, mode, is_running, notification=""):
        """
        Sends posture score, mode, session state and notification to Arduino.
        Format: SCORE:85|MODE:FOCUS|RUN:1|NOTIF:FIX POSTURE
        """
        if self.ser:
            try:
                msg = f"SCORE:{score}|MODE:{mode}|RUN:{1 if is_running else 0}|NOTIF:{notification}\n"
                self.ser.write(msg.encode('utf-8'))
            except Exception as e:
                print(f"[Arduino] Write error: {e}")

    def stop(self):
        self.running = False
        if self.ser:
            self.ser.close()