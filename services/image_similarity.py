# services/image_similarity.py

import imagehash
from PIL import Image

# Store recent hashes
recent_hashes = []

# Maximum hashes to store
MAX_HASH_HISTORY = 50

# Similarity threshold
HASH_THRESHOLD = 5


def generate_image_hash(file):
    """
    Generate perceptual hash for uploaded image
    """

    img = Image.open(file).convert("RGB")

    img_hash = imagehash.phash(img)

    return img_hash


def is_duplicate(image_hash):
    """
    Check if uploaded image is similar to recent images
    """

    for existing_hash in recent_hashes:

        if abs(image_hash - existing_hash) <= HASH_THRESHOLD:
            return True

    return False


def store_hash(image_hash):
    """
    Store new image hash in memory
    """

    recent_hashes.append(image_hash)

    # Maintain fixed history size
    if len(recent_hashes) > MAX_HASH_HISTORY:
        recent_hashes.pop(0)