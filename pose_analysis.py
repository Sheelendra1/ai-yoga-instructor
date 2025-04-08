import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe once
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    model_complexity=0  # Lowest complexity for maximum speed
)

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    return min(angle, 360-angle)

def analyze_pose(image):
    feedback = "Perform a yoga pose"
    
    try:
        # Convert to RGB and process
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_image)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Get key points (using only left side for demo)
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                   landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            
            angle = calculate_angle(shoulder, hip, knee)
            feedback = "Good posture!" if angle > 160 else "Straighten your back"
            
            # Draw landmarks (simplified for performance)
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245,117,66), thickness=1, circle_radius=1),
                mp_drawing.DrawingSpec(color=(245,66,230), thickness=1, circle_radius=1)
            )
            
            cv2.putText(image, feedback, (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    
    except Exception as e:
        pass
        
    return image, feedback