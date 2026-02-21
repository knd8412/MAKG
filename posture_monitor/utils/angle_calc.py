import math
import numpy as np

def calculate_angle(p1, p2, p3):
    """Angle at p2 between points p1-p2-p3 (in degrees). [web:3][web:57]"""
    a = np.array(p1)
    b = np.array(p2)
    c = np.array(p3)
    radians = np.arccos(np.dot(b-a, c-b) / (np.linalg.norm(b-a) * np.linalg.norm(c-b)))
    return np.degrees(radians)
