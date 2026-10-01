# classifier.py
import json
import os
from ml.inference.preprocessing import preprocess_image
from ml.inference.model_adapter import MobileNetV2Adapter
from ml.inference.class_mapping import get_category_and_guidance
from ml.inference.confidence import evaluate_confidence

class WasteClassifier:
    def __init__(self, config_path="ml/config/model_config.json"):
        with open(config_path, "r") as f:
            self.full_config = json.load(f)
            
        active_key = self.full_config["active_model_key"]
        self.config = self.full_config["models"][active_key]
        
        self.threshold = self.config["confidence_threshold"]
        
        # Load appropriate adapter
        if self.config["type"] == "pytorch_mobilenetv2":
            self.adapter = MobileNetV2Adapter()
        else:
            raise ValueError(f"Unsupported model type: {self.config['type']}")
            
        self.adapter.load(self.config["weights_path"], self.config["class_names_path"])
        
    def predict(self, image_bytes: bytes) -> dict:
        """
        Takes raw image bytes and returns the full classification response.
        """
        # Preprocess
        tensor = preprocess_image(image_bytes)
        
        # Predict
        raw_class, confidence = self.adapter.predict(tensor)
        
        # Mapping
        mapping = get_category_and_guidance(raw_class)
        
        # Confidence Handling
        conf_eval = evaluate_confidence(confidence, self.threshold)
        
        # Assemble Response
        response = {
            "class_name": raw_class,
            "confidence": float(confidence),
            "category_group": mapping["category_group"],
            "guidance": mapping["guidance"],
            "is_low_confidence": conf_eval["is_low_confidence"]
        }
        
        # Overwrite guidance if low confidence
        if conf_eval["is_low_confidence"]:
            response["guidance"] = conf_eval["adjusted_guidance"]
            
        return response
