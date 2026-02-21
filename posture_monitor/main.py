import cv2
import time
from config import *
from camera.camera_source import CameraSource
from pose_detector.pose_estimator import PoseEstimator
from posture_analyzer.posture_metrics import PostureAnalyzer
from posture_analyzer.phone_detector import PhoneDetector
from utils.visualisation import draw_metrics

def main():
    cam = CameraSource(CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT)
    pose_est = PoseEstimator()
    analyzer = PostureAnalyzer()
    phone_det = PhoneDetector()
    
    ptime = 0
    while True:
        ret, frame = cam.read()
        if not ret: break
        
        # Pose estimation
        poses = pose_est.estimate_poses(frame)
        num_people = len(poses)
        
        # Analyse each
        analyses = []
        for i, pose in enumerate(poses):
            analysis = analyzer.analyze_pose(pose['landmarks'], frame)
            analysis['on_phone'] = phone_det.detect_phone_use(frame, pose['landmarks'])
            analyses.append(analysis)
            
            # DEBUG: Print raw values
            landmarks = pose['landmarks']
            print(f"Person {i+1}: Nose={landmarks[0][:2]}, LShoulder={landmarks[11][:2]}, LHip={landmarks[23][:2]}")

        
        # Visualise
        frame = pose_est.draw_poses(frame, poses)
        frame = draw_metrics(frame, num_people, analyses)
        
        # FPS
        ctime = time.time()
        fps = 1 / (ctime - ptime)
        ptime = ctime
        cv2.putText(frame, f"FPS: {int(fps)}", (10, FRAME_HEIGHT-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
        
        cv2.imshow("Posture Monitor (q=quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    
    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
