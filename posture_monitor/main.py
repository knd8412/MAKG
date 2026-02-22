import cv2
import time
import threading
import numpy as np
from flask import Flask, Response
from config import *
from camera.camera_source import CameraSource
from pose_detector.pose_estimator import PoseEstimator
from posture_analyzer.posture_metrics import PostureAnalyzer
from posture_analyzer.phone_detector import PhoneDetector
from utils.visualisation import draw_metrics
from alerts.voice_alert import VoiceAlert
from calibration.calibrator import Calibrator
from backend.sender import BackendSender
from hardware.arduino_bridge import ArduinoBridge

# Flask web stream
app = Flask(__name__)
output_frame = None
lock = threading.Lock()

def generate_frames():
    global output_frame, lock
    while True:
        with lock:
            if output_frame is None:
                continue
            ret, buffer = cv2.imencode('.jpg', output_frame)
            frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# vdo.ninja / MJPEG stream camera
class VdoNinjaSource:
    def __init__(self, url, width=320, height=240):
        self.cap = cv2.VideoCapture(url)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        print(f"[Camera] Connecting to stream: {url}")

    def read(self):
        ret, frame = self.cap.read()
        if ret and frame is not None:
            frame = cv2.flip(frame, 1)
        return ret, frame

    def release(self):
        self.cap.release()

def main():
    global output_frame, lock

    # Camera setup
    if USE_VDO_NINJA and VDO_NINJA_URL:
        cam = VdoNinjaSource(VDO_NINJA_URL, FRAME_WIDTH, FRAME_HEIGHT)
        print("[Camera] Using network stream")
    else:
        cam = CameraSource(CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT)
        print("[Camera] Using local webcam")

    pose_est        = PoseEstimator()
    analyzer        = PostureAnalyzer()
    phone_det       = PhoneDetector()
    voice           = VoiceAlert()
    calibrator      = Calibrator()
    backend         = BackendSender()
    arduino         = ArduinoBridge()

    ptime           = 0
    running         = True
    send_every      = 3
    last_send       = 0
    last_score      = 100
    current_mode    = "FOCUS"
    session_running = False
    analyses        = []

    print("FocusPal started.")
    print(f"Stream available at: http://10.170.83.17:5000/video_feed")
    print("Keyboard: S=start/stop, C=calibrate, M=mute, Q=quit")

    while running:
        ret, frame = cam.read()
        if not ret or frame is None:
            print("[Camera] No frame — check camera connection")
            time.sleep(0.1)
            continue

        # Handle Arduino button commands
        cmd = arduino.get_command()
        if cmd:
            if cmd == "CMD_START":
                session_running = True
                print("[Session] Started")
            elif cmd == "CMD_STOP":
                session_running = False
                print("[Session] Stopped")
            elif cmd == "CMD_RESET":
                session_running = False
                analyses = []
                print("[Session] Reset")
            elif cmd == "CMD_VOL_UP":
                voice.unmute()
            elif cmd == "CMD_VOL_DOWN":
                voice.mute()
            elif cmd == "CMD_MUSIC_PP":
                print("[Music] Play/Pause")
            elif cmd == "CMD_MUSIC_SKIP":
                print("[Music] Skip")
            elif cmd.startswith("MODE_CHANGE:"):
                current_mode = cmd.split(":")[1]
                print(f"[Mode] Changed to {current_mode}")

        # AI posture analysis
        analyses = []
        notif = ""

        if session_running:
            poses      = pose_est.estimate_poses(frame)
            num_people = len(poses)

            for i, pose in enumerate(poses):
                torso_thresh, head_thresh = calibrator.get_thresholds()
                analysis = analyzer.analyze_pose(
                    pose['landmarks'], frame,
                    torso_thresh=torso_thresh,
                    head_thresh=head_thresh
                )
                analysis['on_phone'] = phone_det.detect_phone_use(frame, pose['landmarks'])
                analyses.append(analysis)

                voice.check_and_alert(analysis)

                now = time.time()
                if now - last_send > send_every:
                    backend.send_event(analysis)
                    last_send = now

                last_score = backend._calculate_score(analysis)

            # Build OLED notification
            if analyses:
                a = analyses[0]
                if a.get("on_phone"):
                    notif = "GET OFF PHONE"
                elif a.get("slouching"):
                    notif = "FIX POSTURE"
                elif not a.get("attentive"):
                    notif = "HEAD FORWARD"

            frame = pose_est.draw_poses(frame, poses)
            frame = draw_metrics(frame, num_people, analyses)

        # Send data to Arduino for OLED
        arduino.send_posture_data(last_score, current_mode, session_running, notif)

        # Update web stream
        with lock:
            output_frame = frame.copy()

        # Keyboard controls
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            running = False
        elif key == ord('s'):
            session_running = not session_running
            print(f"[Session] {'Started' if session_running else 'Stopped'}")
        elif key == ord('c'):
            if analyses:
                calibrator.calibrate(analyses[0])
                print("[Calibration] Baseline set")
        elif key == ord('m'):
            voice.toggle_mute()

        # FPS
        ctime = time.time()
        fps   = 1 / max(ctime - ptime, 0.001)
        ptime = ctime
        if DEBUG_MODE:
            cv2.putText(frame, f"FPS:{int(fps)} Mode:{current_mode} Score:{last_score} Run:{session_running}",
                       (10, FRAME_HEIGHT - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

    arduino.stop()
    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    main()