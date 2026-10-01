# confidence.py

def evaluate_confidence(confidence: float, threshold: float) -> dict:
    """
    Evaluates whether a prediction meets the required confidence threshold.
    Returns the boolean flag and any adjusted guidance if it fails.
    """
    is_low_confidence = confidence < threshold
    
    if is_low_confidence:
        return {
            "is_low_confidence": True,
            "adjusted_guidance": "Low confidence prediction. Please ensure the waste item is isolated, well-lit, and try again."
        }
    
    return {
        "is_low_confidence": False,
        "adjusted_guidance": None
    }
