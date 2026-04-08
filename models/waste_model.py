# models/waste_model.py

import tensorflow as tf
import numpy as np

from config import MODEL_PATH, CONFIDENCE_THRESHOLD


class WasteClassifier:

    def __init__(self):
        """
        Load trained model when server starts
        """
        print("Loading WasteSense AI model...")

        self.model = tf.keras.models.load_model(MODEL_PATH)

        self.classes = [
            "glass",
            "metal",
            "mixed",
            "organic",
            "paper",
            "plastic"
        ]

        print("Model loaded successfully.")

    def predict(self, image):
        """
        Predict waste type from processed image
        """

        prediction = self.model.predict(image)

        class_index = np.argmax(prediction)

        waste_type = self.classes[class_index]

        confidence = float(np.max(prediction))

        return waste_type, confidence

    def predict_with_validation(self, image):
        """
        Predict waste type and check confidence threshold
        """

        waste_type, confidence = self.predict(image)

        if confidence < CONFIDENCE_THRESHOLD:
            return None, confidence

        return waste_type, confidence


# Singleton instance
classifier = WasteClassifier()