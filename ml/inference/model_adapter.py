# model_adapter.py
import torch
import torch.nn as nn
from torchvision import models
import json
import os

class ModelAdapter:
    """
    Abstract interface for model adapters.
    """
    def load(self, weights_path: str, class_names_path: str):
        raise NotImplementedError
        
    def predict(self, input_tensor: torch.Tensor) -> tuple[str, float]:
        raise NotImplementedError

class MobileNetV2Adapter(ModelAdapter):
    def __init__(self):
        self.model = None
        self.classes = []
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def load(self, weights_path: str, class_names_path: str):
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Model weights not found at {weights_path}")
        if not os.path.exists(class_names_path):
            raise FileNotFoundError(f"Class names not found at {class_names_path}")
            
        with open(class_names_path, "r") as f:
            class_map = json.load(f)
            # Invert the dict: index -> class_name
            self.classes = [k for k, v in sorted(class_map.items(), key=lambda item: item[1])]
            
        # Reconstruct MobileNetV2
        self.model = models.mobilenet_v2(weights=None)
        num_ftrs = self.model.classifier[1].in_features
        self.model.classifier[1] = nn.Linear(num_ftrs, len(self.classes))
        
        # Load state dict
        state_dict = torch.load(weights_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model = self.model.to(self.device)
        self.model.eval()
        
    def predict(self, input_tensor: torch.Tensor) -> tuple[str, float]:
        input_tensor = input_tensor.to(self.device)
        with torch.no_grad():
            outputs = self.model(input_tensor)
            # Apply softmax to get confidences
            probs = torch.nn.functional.softmax(outputs, dim=1)[0]
            confidence, predicted_idx = torch.max(probs, 0)
            
        class_name = self.classes[predicted_idx.item()]
        return class_name, confidence.item()
