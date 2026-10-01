import os
import json
import random
import shutil
from collections import defaultdict
from PIL import Image
import imagehash

MANIFEST_PATH = "dataset_manifest.json"
CLEAN_DIR = "dataset/clean"
SEED = 42

def generate_phash(file_path):
    try:
        with Image.open(file_path) as img:
            return str(imagehash.phash(img))
    except Exception:
        return None

def analyze_cross_source():
    # Gather raw hashes for exact perceptual cross-source matrix
    datasets = ["TrashNet", "GarbageClassificationV2", "OrganicDataset"]
    dataset_paths = {
        "TrashNet": "dataset/raw/TrashNet",
        "GarbageClassificationV2": "dataset/raw/GarbageClassificationV2",
        "OrganicDataset": "dataset/raw/OrganicDataset"
    }
    
    hash_registry = defaultdict(set)
    for ds_name, path in dataset_paths.items():
        if not os.path.exists(path):
            continue
        for root, dirs, files in os.walk(path):
            for file in files:
                if not file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    continue
                file_path = os.path.join(root, file)
                phash = generate_phash(file_path)
                if phash:
                    hash_registry[phash].add(ds_name)
                    
    matrix = defaultdict(int)
    for phash, sources in hash_registry.items():
        sources_list = sorted(list(sources))
        if len(sources_list) > 1:
            for i in range(len(sources_list)):
                for j in range(i+1, len(sources_list)):
                    pair = f"{sources_list[i]} <-> {sources_list[j]}"
                    matrix[pair] += 1
                    
    print("\n--- CROSS-SOURCE PERCEPTUAL MATCHES ---")
    for pair, count in matrix.items():
        print(f"{pair}: {count}")

def check_and_fix_splits():
    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)
        
    class_splits = defaultdict(lambda: {"Train": 0, "Validation": 0, "Test": 0, "Total": 0})
    for m in manifest:
        cls = m["mapped_class"]
        split = m["final_split"]
        class_splits[cls][split] += 1
        class_splits[cls]["Total"] += 1
        
    print("\n--- SPLIT STRATIFICATION ---")
    needs_rebalance = False
    for cls, counts in class_splits.items():
        tot = counts["Total"]
        if tot == 0: continue
        tr = counts["Train"]/tot*100
        val = counts["Validation"]/tot*100
        tst = counts["Test"]/tot*100
        print(f"{cls}: Train {tr:.1f}% | Val {val:.1f}% | Test {tst:.1f}%")
        
        # If deviation is > 2% from 80/10/10
        if abs(tr - 80) > 2 or abs(val - 10) > 2 or abs(tst - 10) > 2:
            needs_rebalance = True
            
    if needs_rebalance:
        print("\nFixing split stratification...")
        random.seed(SEED)
        
        # Group by class
        by_class = defaultdict(list)
        for m in manifest:
            by_class[m["mapped_class"]].append(m)
            
        for cls, items in by_class.items():
            # Sort items by hash to ensure determinism
            items.sort(key=lambda x: x["hash"])
            # Shuffle deterministically
            random.shuffle(items)
            
            n = len(items)
            n_train = int(n * 0.8)
            n_val = int(n * 0.1)
            
            for i, m in enumerate(items):
                old_split = m["final_split"]
                if i < n_train:
                    new_split = "Train"
                elif i < n_train + n_val:
                    new_split = "Validation"
                else:
                    new_split = "Test"
                    
                if old_split != new_split:
                    # Move the file physically
                    old_path = os.path.join(CLEAN_DIR, old_split, m["mapped_class"], m["filename"])
                    new_dir = os.path.join(CLEAN_DIR, new_split, m["mapped_class"])
                    new_path = os.path.join(new_dir, m["filename"])
                    os.makedirs(new_dir, exist_ok=True)
                    if os.path.exists(old_path):
                        shutil.move(old_path, new_path)
                        
                    m["final_split"] = new_split
                    
        with open(MANIFEST_PATH, "w") as f:
            json.dump(manifest, f, indent=4)
        print("Stratification fixed and files moved.")
    else:
        print("Stratification is perfectly balanced.")
        
def check_cross_split_leakage():
    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)
        
    phash_splits = defaultdict(set)
    for m in manifest:
        phash_splits[m["p_hash"]].add(m["final_split"])
        
    leakage = 0
    for phash, splits in phash_splits.items():
        if len(splits) > 1:
            leakage += 1
            
    print("\n--- PERCEPTUAL LEAKAGE REPORT ---")
    print(f"Cross-split perceptual matches found: {leakage}")

if __name__ == "__main__":
    analyze_cross_source()
    check_and_fix_splits()
    check_cross_split_leakage()
