from fastapi import APIRouter, UploadFile, File, Form
import io

router = APIRouter()

# Lazy imports - only loaded when needed
model = None
scaler = None
MovementAnalyzer = None
extract_pose_features = None
cv2 = None
np = None
Image = None
joblib = None

def _load_dependencies():
    """Load heavy dependencies on first use"""
    global model, scaler, MovementAnalyzer, extract_pose_features, cv2, np, Image, joblib
    
    if cv2 is not None:
        return  # Already loaded
    
    try:
        import cv2 as cv2_import
        import numpy as np_import
        from PIL import Image as PILImage
        import joblib as joblib_import
        from movement_features import MovementAnalyzer as MA
        from pose_feature_extractor import extract_pose_features as epf
        
        cv2 = cv2_import
        np = np_import
        Image = PILImage
        joblib = joblib_import
        MovementAnalyzer = MA
        extract_pose_features = epf
        
        # Load model and scaler
        try:
            model = joblib.load("risk_model.pkl")
            scaler = joblib.load("scaler.pkl")
        except Exception as e:
            print(f"Warning: Could not load model/scaler file. {e}")
    except ImportError as e:
        print(f"Error loading movement prediction dependencies: {e}")
        raise

def sanitize_for_json(value):
    """Recursively convert numpy values/containers to JSON-safe native Python types."""
    if isinstance(value, dict):
        return {k: sanitize_for_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize_for_json(v) for v in value]
    if hasattr(value, 'tolist'):  # numpy array
        return [sanitize_for_json(v) for v in value.tolist()]
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return float(value)
    return value

@router.post("/predict")
async def predict(
    file: UploadFile = File(...),
    instruction: str = Form("")
):
    try:
        _load_dependencies()
        
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
    except Exception as e:
        import traceback
        print(f"ERROR in /predict endpoint: {str(e)}")
        print(traceback.format_exc())
        return {"error": str(e)}