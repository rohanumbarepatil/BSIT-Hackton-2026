# config.py

# -----------------------------

# Model Configuration

# -----------------------------

MODEL_PATH = "trained_model/wastesense_model.h5"

# Minimum confidence required to accept prediction

CONFIDENCE_THRESHOLD = 0.6

# JWT Authentication

JWT_SECRET_KEY = "wastesense_super_secret_key_change_this"

# -----------------------------

# Eco Points Configuration

# -----------------------------

ECO_POINTS = {
    "organic": 80,
    "paper": 100,
    "glass": 120,
    "plastic": 150,
    "metal": 200,
    "mixed": 60
}

# -----------------------------

# Campus Bin Locations

# (Human readable labels)

# -----------------------------

CAMPUS_BINS = {
    "organic": [
        "Hostel Mess Compost Bin",
        "Cafeteria Organic Waste Bin"
    ],

    "paper": [
        "Library Paper Recycling Bin",
        "Academic Block Paper Bin"
    ],

    "plastic": [
        "Cafeteria Plastic Recycling Bin",
        "Main Gate Recycling Bin"
    ],

    "glass": [
        "Cafeteria Glass Bottle Bin"
    ],

    "metal": [
        "Mechanical Block Scrap Collection Bin"
    ],

    "mixed": [
        "Admin Block General Waste Bin"
    ]
}

# -----------------------------

# Bin Coordinates

# (Used for distance validation)

# -----------------------------

CAMPUS_BIN_COORDINATES = [
    {
        "name": "Library Paper Recycling Bin",
        "type": "paper",
        "lat": 21.251400,
        "lon": 81.605000
    },

    {
        "name": "Cafeteria Plastic Recycling Bin",
        "type": "plastic",
        "lat": 21.251700,
        "lon": 81.604400
    },

    {
        "name": "Hostel Mess Compost Bin",
        "type": "organic",
        "lat": 21.252100,
        "lon": 81.603900
    },

    {
        "name": "Admin Block General Waste Bin",
        "type": "mixed",
        "lat": 21.250900,
        "lon": 81.605700
    }
]

# Maximum distance allowed to confirm disposal (meters)

BIN_DISTANCE_THRESHOLD = 100

# -----------------------------

# App Settings

# -----------------------------

DEBUG = True

APP_NAME = "WasteSense AI"
