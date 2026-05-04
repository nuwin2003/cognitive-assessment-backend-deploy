from fastapi import APIRouter, UploadFile, File, Form
from movement_features import MovementAnalyzer
from pose_feature_extractor import extract_pose_features
import cv2
import numpy as np
from PIL import Image
import io
import joblib

router = APIRouter()

try:
    model = joblib.load("risk_model.pkl")
    scaler = joblib.load("scaler.pkl")
except Exception as e:
    model = None
    scaler = None
    print(f"Warning: Could not load model/scaler file. {e}")

def sanitize_for_json(value):
    """Recursively convert numpy values/containers to JSON-safe native Python types."""
    if isinstance(value, dict):
        return {k: sanitize_for_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize_for_json(v) for v in value]
    if isinstance(value, np.ndarray):
        return [sanitize_for_json(v) for v in value.tolist()]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    return value

@router.post("/predict")
async def predict(
    file: UploadFile = File(...),
    instruction: str = Form("")
):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    features = extract_pose_features(frame, instruction)
    if not features:
        return {
            "prediction": 0,
            "probability": 0.1,
            "error": "No pose detected",
            "instruction_check": {"target_met": False, "target_distance": 1.0, "instruction_type": "none"},
            "features": {}
        }

    instruction_check = features.get("instruction_check", {})
    target_met      = bool(instruction_check.get("target_met", False))
    target_distance = float(instruction_check.get("target_distance", 1.0))

    analyzer = MovementAnalyzer()
    analyzer.update(features["left_elbow_angle"], features["right_elbow_angle"])
    computed_features = analyzer.compute_features()
    if not computed_features:
        return {"error": "Not enough data"}

    computed_features = sanitize_for_json(computed_features)
    instruction_check = sanitize_for_json(instruction_check)

    # ── Use pose check as the primary decision ──
    if target_met:
        return {
            "prediction":        1,
            "probability":       float(max(0.75, 1.0 - target_distance)),
            "features":          computed_features,
            "instruction_check": instruction_check,
        }
    else:
        return {
            "prediction":        0,
            "probability":       float(max(0.1, 1.0 - target_distance)),
            "features":          computed_features,
            "instruction_check": instruction_check,
            "reason":            f"Pose check failed for: {instruction}"
        }