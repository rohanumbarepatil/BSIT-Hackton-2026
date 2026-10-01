import os
import hashlib
from PIL import Image
import imagehash
from collections import defaultdict

def generate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def is_corrupt(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
        return False
    except Exception:
        return True

def generate_phash(file_path):
    try:
        with Image.open(file_path) as img:
            return str(imagehash.phash(img))
    except Exception:
        return None

def inspect_dataset(base_path, expected_classes=None):
    if not os.path.exists(base_path):
        return {"error": "Path not found"}
        
    stats = defaultdict(lambda: {"raw": 0, "corrupt": 0, "exact_dupes": 0, "perceptual_dupes": 0, "final": 0})
    seen_md5 = set()
    seen_phash = set()
    
    # Recursively find all files
    for root, dirs, files in os.walk(base_path):
        # Determine class name from the folder name
        folder_name = os.path.basename(root)
        if expected_classes and folder_name not in expected_classes:
            pass
            
        # Group by folder name (e.g., 'O', 'R', 'glass', etc.)
        cls_name = folder_name
        
        for file in files:
            if not file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                continue
                
            stats[cls_name]["raw"] += 1
            file_path = os.path.join(root, file)
            
            if is_corrupt(file_path):
                stats[cls_name]["corrupt"] += 1
                continue
                
            md5_hash = generate_md5(file_path)
            if md5_hash in seen_md5:
                stats[cls_name]["exact_dupes"] += 1
                continue
                
            p_hash = generate_phash(file_path)
            if p_hash is None or p_hash in seen_phash:
                stats[cls_name]["perceptual_dupes"] += 1
                continue
                
            seen_md5.add(md5_hash)
            seen_phash.add(p_hash)
            stats[cls_name]["final"] += 1
            
    return dict(stats)

def main():
    print("Inspecting OrganicDataset...")
    organic_stats = inspect_dataset("dataset/raw/OrganicDataset")
    
    print("\nInspecting TrashNet...")
    trashnet_stats = inspect_dataset("dataset/raw/TrashNet")
    
    print("\nInspecting GarbageClassificationV2...")
    gc2_stats = inspect_dataset("dataset/raw/GarbageClassificationV2")
    
    print("\n--- OrganicDataset Report ---")
    for cls, counts in organic_stats.items():
        if counts["raw"] > 0:
            print(f"Folder '{cls}': {counts}")
            
    print("\n--- TrashNet Report ---")
    for cls, counts in trashnet_stats.items():
        if counts["raw"] > 0:
            print(f"Folder '{cls}': {counts}")
            
    print("\n--- GarbageClassificationV2 Report ---")
    for cls, counts in gc2_stats.items():
        if counts["raw"] > 0:
            print(f"Folder '{cls}': {counts}")

if __name__ == "__main__":
    main()
