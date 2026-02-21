from utils.angle_calc import calculate_angle
import numpy as np

# Landmark indices (MediaPipe Pose) [web:17]
SHOULDER_L, SHOULDER_R = 11, 12
HIP_L, HIP_R = 23, 24
EAR_L, EAR_R = 7, 8
NOSE = 0
EYE_L, EYE_R = 1, 2

class PostureAnalyzer:
    def __init__(self):
        self.good_posture_frames = 0
        
    def analyze_pose(self, landmarks, frame):
        points = np.array(landmarks)
        frame_w = frame.shape[1]
        
        shoulder_avg = ((points[11][0] + points[12][0])/2, (points[11][1] + points[12][1])/2)
        hip_avg = ((points[23][0] + points[24][0])/2, (points[23][1] + points[24][1])/2)
        nose = points[0][:2]
        
        # FIXED: Vertical = same X, top of frame (0 Y)
        vertical_top = (shoulder_avg[0], 0)
        torso_angle = calculate_angle(hip_avg, shoulder_avg, vertical_top)
        
        head_offset = abs(nose[0] - shoulder_avg[0]) / frame_w
        
        print(f"Torso: {torso_angle:.1f}° | Head: {head_offset:.3f}")
        
        return {
            'slouching': torso_angle < 160,
            'torso_angle': torso_angle,
            'attentive': head_offset < 0.08,
            'head_forward': head_offset,
            'nose': nose,
            'shoulder_avg': shoulder_avg,
            'hip_avg': hip_avg
        }


