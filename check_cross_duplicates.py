import os
from PIL import Image
import imagehash
from collections import defaultdict

def generate_phash(file_path):
    try:
        with Image.open(file_path) as img:
            return str(imagehash.phash(img))
    except Exception:
        return None

def collect_hashes(base_path, dataset_name, hash_dict):
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if not file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                continue
            file_path = os.path.join(root, file)
            p_hash = generate_phash(file_path)
            if p_hash:
                hash_dict[p_hash].append((dataset_name, file_path))

def main():
    hashes = defaultdict(list)
    print("Collecting hashes for TrashNet...")
    collect_hashes("dataset/raw/TrashNet", "TrashNet", hashes)
    
    print("Collecting hashes for GarbageClassificationV2...")
    collect_hashes("dataset/raw/GarbageClassificationV2", "GCV2", hashes)
    
    cross_dupes = 0
    for phash, paths in hashes.items():
        datasets = set([p[0] for p in paths])
        if len(datasets) > 1:
            cross_dupes += 1
            
    print(f"\nFound {cross_dupes} unique perceptual hashes that exist in BOTH TrashNet and GarbageClassificationV2.")

if __name__ == "__main__":
    main()
