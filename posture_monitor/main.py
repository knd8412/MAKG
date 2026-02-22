import cv2
import time
import threading
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

# --- WEB STREAMING SETUP ---
app = Flask(__name__)
output_frame = None
lock = threading.Lock()

def generate_frames():
    global output_frame, lock
    while True:
        with lock:
            if output_frame is None:
                continue
            # Encode the frame so the browser can display it
            ret, buffer = cv2.imencode('.jpg', output_frame)
            frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_flask():
    # Run Flask on port 5000
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# --- MAIN LOGIC ---
def main():
    global output_frame, lock
    
    cam        = CameraSource(CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT)
    pose_est   = PoseEstimator()
    analyzer   = PostureAnalyzer()
    phone_det  = PhoneDetector()       
    voice      = VoiceAlert()          
    calibrator = Calibrator()          
    backend    = BackendSender()       

    ptime      = 0
    running    = True
    send_every = 3   
    last_send  = 0

    print("FocusPal started. Stream available at http://192.168.137.1:5000/video_feed")

    while running:
        ret, frame = cam.read()
        if not ret:
            break

        # 1. AI Analysis
        poses      = pose_est.estimate_poses(frame)
        num_people = len(poses)
        analyses   = []

        for i, pose in enumerate(poses):
            torso_thresh, head_thresh = calibrator.get_thresholds()
            analysis = analyzer.analyze_pose(
                pose['landmarks'], frame,
                torso_thresh=torso_thresh,
                head_thresh=head_thresh
            )

            analysis['on_phone'] = phone_det.detect_phone_use(frame, pose['landmarks'])
            analyses.append(analysis)

            # 2. Alerts & Cloud Sync
            voice.check_and_alert(analysis)
            now = time.time()
            if now - last_send > send_every:
                backend.send_event(analysis)
                last_send = now

        # 3. Drawing (Visuals)
        frame = pose_est.draw_poses(frame, poses)
        frame = draw_metrics(frame, num_people, analyses)

        # 4. Update Web Stream
        with lock:
            output_frame = frame.copy()

        # Keyboard controls (if running with a screen attached)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            running = False
        elif key == ord('c'):
            if analyses:
                calibrator.calibrate(analyses[0])

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Start Web Streamer in background
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Run Main AI loop
    main()