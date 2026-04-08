# utils/image_processing.py

import numpy as np
from PIL import Image


def preprocess_image(file):
    """
    Convert uploaded image into model-ready format
    """

    # Open image
    img = Image.open(file).convert("RGB")

    # Resize to model input size
    img = img.resize((224, 224))

    # Convert to numpy array
    img_array = np.array(img)

    # Normalize pixels (0–255 → 0–1)
    img_array = img_array / 255.0

    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)

    return img_array


def load_image_from_path(image_path):
    """
    Utility for testing images directly from disk
    """

    img = Image.open(image_path).convert("RGB")

    img = img.resize((224, 224))

    img_array = np.array(img) / 255.0

    img_array = np.expand_dims(img_array, axis=0)

    return img_array