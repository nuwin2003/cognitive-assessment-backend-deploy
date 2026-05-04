import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from collections import deque
import os

pose = None
pose_history = deque(maxlen=30)  # Keep last 30 frames for motion analysis

def _init_pose():
    global pose
    if pose is None:
        # Get the absolute path to the model file
        model_path = os.path.join(os.path.dirname(__file__), 'pose_landmarker_lite.task')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE
        )
        pose = vision.PoseLandmarker.create_from_options(options)

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arccos(
        np.dot(a-b, c-b) /
        (np.linalg.norm(a-b) * np.linalg.norm(c-b) + 1e-6)
    )
    return np.degrees(radians)

# ─────────────────────────────────────────────────────────────────────────────
# ADVANCED HELPER FUNCTIONS FOR ACTION DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def dist_2d(a, b):
    """Calculate 2D Euclidean distance"""
    return float(np.sqrt((a.x - b.x)**2 + (a.y - b.y)**2))

def dist_3d(a, b):
    """Calculate 3D Euclidean distance including depth"""
    return float(np.sqrt((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2))

def get_hand_velocity(landmarks, history_length=5):
    """Calculate hand velocity from recent pose history"""
    if len(pose_history) < history_length:
        return 0.0
    
    recent = list(pose_history)[-history_length:]
    if not recent:
        return 0.0
    
    left_wrist_current = recent[-1][15]
    left_wrist_prev = recent[0][15]
    right_wrist_current = recent[-1][16]
    right_wrist_prev = recent[0][16]
    
    left_vel = np.sqrt((left_wrist_current.x - left_wrist_prev.x)**2 + 
                       (left_wrist_current.y - left_wrist_prev.y)**2)
    right_vel = np.sqrt((right_wrist_current.x - right_wrist_prev.x)**2 + 
                        (right_wrist_current.y - right_wrist_prev.y)**2)
    
    return float(max(left_vel, right_vel))

def is_hand_in_front_of_face(wrist, nose, face_threshold=0.1):
    """Check if hand is in front of face (closer to camera)"""
    return wrist.z < (nose.z - face_threshold)

def is_hand_near_face(wrist, nose, distance_threshold=0.25):
    """Check if hand is near face area"""
    return dist_2d(wrist, nose) < distance_threshold

def is_arm_bent(shoulder, elbow, wrist, min_angle=40, max_angle=160):
    """Check if arm is bent within reasonable angle range"""
    angle = calculate_angle(
        [shoulder.x, shoulder.y],
        [elbow.x, elbow.y],
        [wrist.x, wrist.y]
    )
    return min_angle < angle < max_angle

def get_horizontal_hand_distance(left_wrist, right_wrist):
    """Calculate horizontal distance between hands"""
    return abs(left_wrist.x - right_wrist.x)

def get_vertical_hand_alignment(left_wrist, right_wrist):
    """Check if hands are vertically aligned (for clap detection)"""
    return abs(left_wrist.y - right_wrist.y)

def is_wrist_above_shoulder(wrist, shoulder, margin=0.05):
    """Check if wrist is above shoulder level"""
    return wrist.y < (shoulder.y - margin)

def is_wrist_at_face_level(wrist, face_y_center, tolerance=0.1):
    """Check if wrist is at facial level"""
    return abs(wrist.y - face_y_center) < tolerance

def calculate_hand_distance_trend(landmarks, window=5):
    """Calculate if hand is moving toward or away from face"""
    if len(pose_history) < window:
        return 0.0
    
    recent = list(pose_history)[-window:]
    distances = [dist_2d(frame[15], frame[0]) for frame in recent]
    
    if len(distances) < 2:
        return 0.0
    
    trend = distances[-1] - distances[0]  # negative = approaching, positive = moving away
    return float(trend)

def get_shoulder_level(left_shoulder, right_shoulder):
    """Get average shoulder y-position"""
    return (left_shoulder.y + right_shoulder.y) / 2.0

def get_face_bbox(landmarks):
    """Get face bounding box dimensions"""
    nose = landmarks[0]
    left_eye = landmarks[2]
    right_eye = landmarks[5]
    left_ear = landmarks[7]
    right_ear = landmarks[8]
    
    face_width = max(dist_2d(left_eye, right_eye), dist_2d(left_ear, right_ear))
    face_height = dist_2d(left_eye, landmarks[10]) * 2  # chin-like
    
    return {"width": face_width, "height": face_height}

# ─────────────────────────────────────────────────────────────────────────────
# ADVANCED ACTION DETECTION LOGIC
# ─────────────────────────────────────────────────────────────────────────────

def check_instruction(landmarks, instruction: str) -> dict:
    """Advanced instruction checking with multi-dimensional analysis."""
    
    instruction_lower = instruction.lower()
    
    # ── TOUCH NOSE (Advanced Detection) ──────────────────────────────────────
    if "nose" in instruction_lower:
        nose = landmarks[0]
        left_wrist = landmarks[15]
        right_wrist = landmarks[16]
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_elbow = landmarks[13]
        right_elbow = landmarks[14]
        
        # Calculate distances
        left_dist_3d = dist_3d(left_wrist, nose)
        right_dist_3d = dist_3d(right_wrist, nose)
        min_dist_3d = min(left_dist_3d, right_dist_3d)
        min_dist_2d = min(dist_2d(left_wrist, nose), dist_2d(right_wrist, nose))
        
        closer_wrist = left_wrist if left_dist_3d < right_dist_3d else right_wrist
        closer_elbow = left_elbow if left_dist_3d < right_dist_3d else right_elbow
        closer_shoulder = left_shoulder if left_dist_3d < right_dist_3d else right_shoulder
        
        # Multi-dimensional checks for nose touch
        check1_very_close = min_dist_3d < 0.22  # Strict 3D distance
        check2_in_front = is_hand_in_front_of_face(closer_wrist, nose, face_threshold=0.05)
        check3_arm_bent = is_arm_bent(closer_shoulder, closer_elbow, closer_wrist, min_angle=50, max_angle=140)
        check4_approaching = calculate_hand_distance_trend(landmarks) <= 0.01  # Moving toward or stable
        check5_wrist_centered = abs(closer_wrist.x - nose.x) < 0.12  # Horizontally centered
        
        # All checks must pass
        target_met = bool(check1_very_close and check2_in_front and check3_arm_bent and check5_wrist_centered)
        confidence = sum([check1_very_close, check2_in_front, check3_arm_bent, check4_approaching, check5_wrist_centered]) / 5.0
        
        return {
            "target_distance": float(min_dist_3d),
            "target_met": target_met,
            "instruction_type": "touch_nose",
            "confidence": float(confidence),
            "details": {
                "very_close": check1_very_close,
                "in_front": check2_in_front,
                "arm_bent": check3_arm_bent,
                "approaching": check4_approaching,
                "centered": check5_wrist_centered
            }
        }
    
    # ── TOUCH HEAD (Advanced Detection) ──────────────────────────────────────
    elif "head" in instruction_lower:
        left_wrist = landmarks[15]
        right_wrist = landmarks[16]
        left_ear = landmarks[7]
        right_ear = landmarks[8]
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_elbow = landmarks[13]
        right_elbow = landmarks[14]
        
        # Calculate metrics
        left_dist_ear = dist_2d(left_wrist, left_ear)
        right_dist_ear = dist_2d(right_wrist, right_ear)
        best_dist = min(left_dist_ear, right_dist_ear)
        
        closer_wrist = left_wrist if left_dist_ear < right_dist_ear else right_wrist
        closer_ear = left_ear if left_dist_ear < right_dist_ear else right_ear
        closer_elbow = left_elbow if left_dist_ear < right_dist_ear else right_elbow
        closer_shoulder = left_shoulder if left_dist_ear < right_dist_ear else right_shoulder
        
        # Advanced checks
        check1_near_head = best_dist < 0.20  # Close to ear/head
        check2_wrist_above_shoulder = is_wrist_above_shoulder(closer_wrist, closer_shoulder, margin=0.0)
        check3_arm_bent = is_arm_bent(closer_shoulder, closer_elbow, closer_wrist, min_angle=45, max_angle=150)
        check4_at_head_level = is_wrist_at_face_level(closer_wrist, closer_ear.y, tolerance=0.15)
        
        target_met = bool(check1_near_head and check2_wrist_above_shoulder and (check3_arm_bent or check4_at_head_level))
        confidence = sum([check1_near_head, check2_wrist_above_shoulder, check3_arm_bent, check4_at_head_level]) / 4.0
        
        return {
            "target_distance": float(best_dist),
            "target_met": target_met,
            "instruction_type": "touch_head",
            "confidence": float(confidence),
            "details": {
                "near_head": check1_near_head,
                "above_shoulder": check2_wrist_above_shoulder,
                "arm_bent": check3_arm_bent,
                "at_head_level": check4_at_head_level
            }
        }
    
    # ── WAVE HAND (Advanced Detection) ──────────────────────────────────────
    elif "wave" in instruction_lower:
        left_wrist = landmarks[15]
        right_wrist = landmarks[16]
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_elbow = landmarks[13]
        right_elbow = landmarks[14]
        nose = landmarks[0]
        
        # Motion characteristics
        velocity = get_hand_velocity(landmarks)
        left_dist_nose = dist_2d(left_wrist, nose)
        right_dist_nose = dist_2d(right_wrist, nose)
        
        # Wrist above shoulder checks
        left_raised = is_wrist_above_shoulder(left_wrist, left_shoulder, margin=0.02)
        right_raised = is_wrist_above_shoulder(right_wrist, right_shoulder, margin=0.02)
        
        # Critical: hand must be away from face for wave
        left_away_from_face = left_dist_nose > 0.28
        right_away_from_face = right_dist_nose > 0.28
        
        # Arm must be bent for waving motion
        left_arm_bent = is_arm_bent(left_shoulder, left_elbow, left_wrist, min_angle=60, max_angle=140)
        right_arm_bent = is_arm_bent(right_shoulder, right_elbow, right_wrist, min_angle=60, max_angle=140)
        
        # Check that wrist is not too close to body (should be extended to sides)
        left_extended = abs(left_wrist.x - left_shoulder.x) > 0.15
        right_extended = abs(right_wrist.x - right_shoulder.x) > 0.15
        
        height_diff = min(
            left_shoulder.y - left_wrist.y,
            right_shoulder.y - right_wrist.y
        )
        
        # Wave requires: raised wrist + arm bent + away from face + extended
        left_is_wave = left_raised and left_arm_bent and left_away_from_face and left_extended
        right_is_wave = right_raised and right_arm_bent and right_away_from_face and right_extended
        
        target_met = bool(left_is_wave or right_is_wave)
        confidence = sum([left_is_wave or right_raised, left_arm_bent or right_arm_bent, 
                         left_away_from_face or right_away_from_face, left_extended or right_extended]) / 4.0
        
        return {
            "target_distance": float(abs(height_diff)),
            "target_met": target_met,
            "instruction_type": "wave_hand",
            "confidence": float(confidence),
            "velocity": float(velocity),
            "details": {
                "left_raised": left_raised,
                "right_raised": right_raised,
                "left_away": left_away_from_face,
                "right_away": right_away_from_face,
                "left_bent": left_arm_bent,
                "right_bent": right_arm_bent,
                "left_extended": left_extended,
                "right_extended": right_extended
            }
        }
    
    # ── CLAP HANDS (Advanced Detection) ──────────────────────────────────────
    elif "clap" in instruction_lower:
        left_wrist = landmarks[15]
        right_wrist = landmarks[16]
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_elbow = landmarks[13]
        right_elbow = landmarks[14]
        nose = landmarks[0]
        
        # Distance metrics
        wrist_dist = dist_2d(left_wrist, right_wrist)
        left_dist_nose = dist_2d(left_wrist, nose)
        right_dist_nose = dist_2d(right_wrist, nose)
        
        # Hands must be very close for clap
        check1_hands_together = wrist_dist < 0.18  # Very close
        
        # Hands should be above chest level
        check2_raised = (left_wrist.y < left_shoulder.y + 0.2) and (right_wrist.y < right_shoulder.y + 0.2)
        
        # Arms should be bent appropriately
        left_arm_bent = is_arm_bent(left_shoulder, left_elbow, left_wrist, min_angle=50, max_angle=130)
        right_arm_bent = is_arm_bent(right_shoulder, right_elbow, right_wrist, min_angle=50, max_angle=130)
        check3_arms_bent = left_arm_bent and right_arm_bent
        
        # Hands should be away from face (not touching face instead)
        check4_away_from_face = (left_dist_nose > 0.25) and (right_dist_nose > 0.25)
        
        # Vertical alignment (hands at similar heights)
        vertical_alignment = abs(left_wrist.y - right_wrist.y)
        check5_aligned = vertical_alignment < 0.12
        
        target_met = bool(check1_hands_together and check2_raised and check3_arms_bent and check4_away_from_face and check5_aligned)
        confidence = sum([check1_hands_together, check2_raised, check3_arms_bent, check4_away_from_face, check5_aligned]) / 5.0
        
        return {
            "target_distance": float(wrist_dist),
            "target_met": target_met,
            "instruction_type": "clap_hands",
            "confidence": float(confidence),
            "details": {
                "hands_together": check1_hands_together,
                "raised": check2_raised,
                "arms_bent": check3_arms_bent,
                "away_from_face": check4_away_from_face,
                "aligned": check5_aligned
            }
        }
    
    # ── UNKNOWN ──────────────────────────────────────────────────────────────
    else:
        return {
            "target_distance": 1.0,
            "target_met": False,
            "instruction_type": "unknown",
            "confidence": 0.0,
            "details": {}
        }


def extract_pose_features(frame, instruction: str = ""):
    _init_pose()

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    results = pose.detect(mp_image)

    if not results.pose_landmarks:
        return None

    landmarks = results.pose_landmarks[0]
    
    # Add to history for motion analysis
    pose_history.append(landmarks)

    left_shoulder = [landmarks[11].x, landmarks[11].y]
    left_elbow    = [landmarks[13].x, landmarks[13].y]
    left_wrist    = [landmarks[15].x, landmarks[15].y]

    right_shoulder = [landmarks[12].x, landmarks[12].y]
    right_elbow    = [landmarks[14].x, landmarks[14].y]
    right_wrist    = [landmarks[16].x, landmarks[16].y]

    left_elbow_angle  = calculate_angle(left_shoulder, left_elbow, left_wrist)
    right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

    instruction_check = check_instruction(landmarks, instruction) if instruction else {
        "target_distance": 1.0,
        "target_met":      False,
        "instruction_type": "none",
        "confidence": 0.0,
        "details": {}
    }

    return {
        "left_elbow_angle":  left_elbow_angle,
        "right_elbow_angle": right_elbow_angle,
        "instruction_check": instruction_check,
    }