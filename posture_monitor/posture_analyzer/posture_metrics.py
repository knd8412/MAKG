import math
import numpy as np
from utils.angle_calc import calculate_angle

SHOULDER_L, SHOULDER_R = 11, 12
HIP_L, HIP_R = 23, 24
EAR_L, EAR_R = 7, 8
NOSE = 0

class PostureAnalyzer:
    def __init__(self):
        self.good_posture_frames = 0

    def analyze_pose(self, landmarks, frame, torso_thresh=15, head_thresh=0.08):
        points = np.array(landmarks)
        frame_w = frame.shape[1]

        shoulder_avg = ((points[11][0] + points[12][0])/2, (points[11][1] + points[12][1])/2)
        hip_avg      = ((points[23][0] + points[24][0])/2, (points[23][1] + points[24][1])/2)
        ear_avg      = ((points[7][0]  + points[8][0])/2,  (points[7][1]  + points[8][1])/2)
        nose         = points[0][:2]

        # Torso angle = degrees from vertical between shoulder and hip
        # 0° = perfectly upright, >15° = slouching
        dx = hip_avg[0] - shoulder_avg[0]
        dy = hip_avg[1] - shoulder_avg[1]
        torso_angle = abs(math.degrees(math.atan2(dx, dy)))

        head_offset = abs(nose[0] - shoulder_avg[0]) / frame_w

        print(f"Torso: {torso_angle:.1f}° | Head: {head_offset:.3f}")

        return {
            'slouching':    torso_angle > torso_thresh,  # > because 0 = upright
            'torso_angle':  torso_angle,
            'attentive':    head_offset < head_thresh,
            'head_forward': head_offset,
            'nose':         nose,
            'shoulder_avg': shoulder_avg,
            'hip_avg':      hip_avg
        }


