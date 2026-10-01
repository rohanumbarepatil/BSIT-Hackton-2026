# preprocessing.py
from PIL import Image
import io
import torch
from torchvision import transforms

def preprocess_image(image_bytes: bytes) -> torch.Tensor:
    """
    Decodes an image from bytes and applies the exact validation/test transformations 
    used during the MobileNetV2 prototype training.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    except Exception as e:
        raise ValueError("Invalid image format or corrupted bytes.") from e

    # MobileNetV2 standard eval transforms
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # Add batch dimension
    tensor = transform(image).unsqueeze(0)
    return tensor
