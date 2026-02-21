import mediapipe as mp
import cv2
import numpy as np
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class PoseEstimator:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), 'pose_landmarker_lite.task')
        print(f"Loading model: {model_path}")
        
        BaseOptions = python.BaseOptions
        PoseLandmarker = vision.PoseLandmarker
        PoseLandmarkerOptions = vision.PoseLandmarkerOptions
        
        self.options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1
        )
        self.landmarker = PoseLandmarker.create_from_options(self.options)
        print("PoseLandmarker ready!")
    
    def estimate_poses(self, frame):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        timestamp_ms = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)
        results = self.landmarker.detect_for_video(mp_image, timestamp_ms)
        
        poses = []
        if results.pose_landmarks:
            h, w = frame.shape[:2]
            for pose_landmarks in results.pose_landmarks:
                landmarks = [(lm.x * w, lm.y * h, lm.z) for lm in pose_landmarks]
                bbox = self._get_bbox(landmarks)
                poses.append({'landmarks': landmarks, 'bbox': bbox})
        return poses
    
    def draw_poses(self, frame, poses):
        # Custom drawing since mp.solutions.drawing_utils is gone [web:133]
        for pose in poses:
            x, y, bw, bh = [int(v) for v in pose['bbox']]
            cv2.rectangle(frame, (x, y), (x+bw, y+bh), (0, 255, 0), 2)
            
            # Draw simplified skeleton (shoulders, hips, nose)
            landmarks = pose['landmarks']
            pts = np.array(landmarks, np.int32)
            
            # Torso line
            cv2.line(frame, (int(landmarks[11][0]), int(landmarks[11][1])),  # Left shoulder
                            (int(landmarks[23][0]), int(landmarks[23][1])), (255, 0, 0), 2)  # Left hip
            
            # Head
            cv2.circle(frame, (int(landmarks[0][0]), int(landmarks[0][1])), 5, (0, 0, 255), -1)
        
        return frame
    
    def _get_bbox(self, landmarks):
        xs, ys = zip(*[(p[0], p[1]) for p in landmarks])
        return (min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys))
