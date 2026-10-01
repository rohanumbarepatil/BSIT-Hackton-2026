# class_mapping.py

def get_category_and_guidance(predicted_class: str) -> dict:
    """
    Maps the internal 7 classes to the 3-category problem statement 
    plus specific disposal guidance.
    """
    mapping = {
        "organic": {
            "category_group": "Biodegradable",
            "guidance": "Dispose of in the green compost bin. Suitable for biogas processing."
        },
        "paper": {
            "category_group": "Dry Recyclable",
            "guidance": "Dispose of in the blue recycling bin. Ensure it is not heavily contaminated with food."
        },
        "glass": {
            "category_group": "Dry Recyclable",
            "guidance": "Dispose of in the blue recycling bin. Handle with care."
        },
        "plastic": {
            "category_group": "Dry Recyclable",
            "guidance": "Dispose of in the blue recycling bin. Please crush bottles to save space."
        },
        "metal": {
            "category_group": "Dry Recyclable",
            "guidance": "Dispose of in the blue recycling bin. Ensure cans are empty."
        },
        "ewaste": {
            "category_group": "Hazardous/E-Waste",
            "guidance": "DANGER: Dispose of in the red e-waste collection bin only. Do not place in general waste."
        },
        "mixed": {
            "category_group": "Mixed/Uncertain",
            "guidance": "Dispose of in the general waste bin. Please attempt to separate recyclables if possible."
        }
    }
    
    return mapping.get(predicted_class, {
        "category_group": "Unknown",
        "guidance": "Uncertain classification. Please contact support."
    })
