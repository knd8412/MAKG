import cv2

def draw_metrics(frame, num_people, poses_analyses):
    y = 30
    cv2.putText(frame, f"People detected: {num_people}", (10, y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    y += 30
    for i, analysis in enumerate(poses_analyses):
        status = "GOOD" if not analysis['slouching'] and analysis['attentive'] else "BAD"
        color = (0,255,0) if status == "GOOD" else (0,0,255)
        cv2.putText(frame, f"Person {i+1}: {status} (Angle: {analysis['torso_angle']:.0f}°)", 
                    (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        y += 25

    # Debug lines on frame
    for i, analysis in enumerate(poses_analyses):
        cv2.circle(frame, tuple(map(int, analysis['nose'])), 8, (0,0,255), -1)
        cv2.circle(frame, tuple(map(int, analysis['shoulder_avg'])), 6, (255,0,0), -1)
        cv2.circle(frame, tuple(map(int, analysis['hip_avg'])), 6, (0,255,0), -1)
        cv2.line(frame, tuple(map(int, analysis['hip_avg'])), tuple(map(int, analysis['shoulder_avg'])), (255,255,0), 3)

    
    return frame


