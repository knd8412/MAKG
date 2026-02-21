import cv2
import time
from config import *
from camera.camera_source import CameraSource
from pose_detector.pose_estimator import PoseEstimator
from posture_analyzer.posture_metrics import PostureAnalyzer
from posture_analyzer.phone_detector import PhoneDetector
from utils.visualisation import draw_metrics
from alerts.voice_alert import VoiceAlert
from calibration.calibrator import Calibrator
from backend.sender import BackendSender

# ── Button GPIO setup (via Arduino serial or direct GPIO) ──────────────────
# Uncomment if using GPIO directly on Pi
# import RPi.GPIO as GPIO
# BTN_MODE       = 17
# BTN_CALIBRATE  = 27
# BTN_ONOFF      = 22
# BTN_SONG       = 23
# GPIO.setmode(GPIO.BCM)
# for pin in [BTN_MODE, BTN_CALIBRATE, BTN_ONOFF, BTN_SONG]:
#     GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def main():
    cam        = CameraSource(CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT)
    pose_est   = PoseEstimator()
    analyzer   = PostureAnalyzer()
    phone_det  = PhoneDetector()       # now uses Gemini
    voice      = VoiceAlert()          # ElevenLabs
    calibrator = Calibrator()          # personalised baseline
    backend    = BackendSender()       # sends to MongoDB via Vultr

    ptime      = 0
    running    = True
    send_every = 3   # send event to backend every N seconds
    last_send  = 0

    print("FocusPal started. Press Q to quit.")
    if calibrator.calibrated:
        print("Calibration loaded from previous session.")
    else:
        print("No calibration found — using defaults. Press CALIBRATE button to set baseline.")

    while running:
        ret, frame = cam.read()
        if not ret:
            break

        # ── Pose estimation ────────────────────────────────────────────────
        poses      = pose_est.estimate_poses(frame)
        num_people = len(poses)

        analyses = []
        for i, pose in enumerate(poses):
            # Get personalised thresholds from calibrator
            torso_thresh, head_thresh = calibrator.get_thresholds()

            analysis = analyzer.analyze_pose(
                pose['landmarks'], frame,
                torso_thresh=torso_thresh,
                head_thresh=head_thresh
            )

            # Gemini phone detection (throttled internally)
            analysis['on_phone'] = phone_det.detect_phone_use(frame, pose['landmarks'])
            analyses.append(analysis)

            # ── Voice alerts ───────────────────────────────────────────────
            voice.check_and_alert(analysis)

            # ── Send to backend every N seconds ───────────────────────────
            now = time.time()
            if now - last_send > send_every:
                backend.send_event(analysis)
                last_send = now

            if DEBUG_MODE:
                lm = pose['landmarks']
                print(f"Person {i+1}: Nose={lm[0][:2]}, "
                      f"Torso={analysis['torso_angle']:.1f}°, "
                      f"Phone={analysis['on_phone']}")

        # ── Button handling (keyboard fallback for dev/testing) ────────────
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            running = False
        elif key == ord('c'):   # C = calibrate
            if analyses:
                calibrator.calibrate(analyses[0])
                print("Calibrated to current posture.")
        elif key == ord('m'):   # M = mute toggle
            voice.toggle_mute()

        # ── Visualise ─────────────────────────────────────────────────────
        frame = pose_est.draw_poses(frame, poses)
        frame = draw_metrics(frame, num_people, analyses)

        # FPS counter
        ctime = time.time()
        fps   = 1 / max(ctime - ptime, 0.001)
        ptime = ctime
        cv2.putText(frame, f"FPS: {int(fps)}", (10, FRAME_HEIGHT - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        cv2.imshow("FocusPal (Q=quit, C=calibrate, M=mute)", frame)

    cam.release()
    cv2.destroyAllWindows()
    # GPIO.cleanup()  # uncomment if using GPIO

if __name__ == "__main__":
    main()