import os
import hashlib
import json
import random
from PIL import Image
import imagehash
from collections import defaultdict

# Global Config
SEED = 42
random.seed(SEED)

CLEAN_DIR = "dataset/clean"
MANIFEST_PATH = "dataset_manifest.json"
INTERNAL_CLASSES = ["organic", "paper", "glass", "plastic", "metal", "mixed", "ewaste"]

DATASET_CONFIGS = {
    "TrashNet": {
        "path": "dataset/raw/TrashNet",
        "license": "MIT",
        "source_url": "https://github.com/garythung/trashnet",
        "attribution_requirement": "Gary Thung and Mindy Yang",
        "mapping": {
            "cardboard": "paper",
            "paper": "paper",
            "glass": "glass",
            "plastic": "plastic",
            "metal": "metal",
            "trash": "mixed"
        }
    },
    "GarbageClassificationV2": {
        "path": "dataset/raw/GarbageClassificationV2",
        "license": "TBD (Verify Source)",
        "source_url": "TBD",
        "attribution_requirement": "TBD",
        "mapping": {
            "biological": "organic",
            "cardboard": "paper",
            "paper": "paper",
            "glass": "glass",
            "plastic": "plastic",
            "metal": "metal",
            "trash": "mixed",
            "battery": "ewaste"
        }
    },
    "OrganicDataset": {
        "path": "dataset/raw/OrganicDataset",
        "license": "CC BY 4.0",
        "source_url": "https://www.kaggle.com/datasets/techsash/waste-classification-data",
        "attribution_requirement": "Image Waste Classification Dataset Authors",
        "mapping": {
            "O": "organic"
        }
    },
    "Roboflow": {
        "path": "dataset/raw/Roboflow",
        "license": "CC BY 4.0",
        "source_url": "https://universe.roboflow.com/waste-classification-jl6nz/waste-lx8r0-z2u2v",
        "attribution_requirement": "Waste classification / Roboflow Universe",
        "mapping": {
            "Battery": "ewaste",
            "Keyboard": "ewaste",
            "Mobile": "ewaste",
            "Mouse": "ewaste",
            "PCB": "ewaste",
            "Printer": "ewaste"
        }
    }
}

INGESTION_ORDER = ["TrashNet", "GarbageClassificationV2", "OrganicDataset", "Roboflow"]

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

def main():
    os.makedirs(CLEAN_DIR, exist_ok=True)
    
    # Global Hash Registries
    global_md5 = {}    # md5 -> (ds_name, img_path)
    global_phash = {}  # phash -> (ds_name, img_path)
    
    # Tracking
    manifest = []
    stats = {
        c: {"sources": set(), "raw": 0, "corrupt": 0, "exact_dupes": 0, "perceptual_dupes": 0, "capped": 0, "final": 0}
        for c in INTERNAL_CLASSES
    }
    
    # Pass 1: Global Ingestion & Deduplication
    unique_candidates = defaultdict(list)
    
    for ds_name in INGESTION_ORDER:
        ds_config = DATASET_CONFIGS[ds_name]
        base_path = ds_config["path"]
        
        if not os.path.exists(base_path):
            print(f"Skipping {ds_name} (Not found at {base_path})")
            continue
            
        for root, dirs, files in os.walk(base_path):
            source_class = os.path.basename(root)
            mapped_class = ds_config["mapping"].get(source_class)
            
            if not mapped_class:
                continue
                
            for img_name in files:
                if not img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    continue
                    
                img_path = os.path.join(root, img_name)
                stats[mapped_class]["raw"] += 1
                stats[mapped_class]["sources"].add(ds_name)
                
                if is_corrupt(img_path):
                    stats[mapped_class]["corrupt"] += 1
                    continue
                    
                md5_hash = generate_md5(img_path)
                if md5_hash in global_md5:
                    stats[mapped_class]["exact_dupes"] += 1
                    # Log duplicate provenance could be stored globally
                    continue
                    
                p_hash = generate_phash(img_path)
                if p_hash is None or p_hash in global_phash:
                    stats[mapped_class]["perceptual_dupes"] += 1
                    continue
                    
                # Passed all checks
                global_md5[md5_hash] = (ds_name, img_path)
                global_phash[p_hash] = (ds_name, img_path)
                
                candidate = {
                    "ds_name": ds_name,
                    "source_class": source_class,
                    "mapped_class": mapped_class,
                    "img_name": img_name,
                    "img_path": img_path,
                    "md5_hash": md5_hash,
                    "p_hash": p_hash,
                    "ds_config": ds_config
                }
                unique_candidates[mapped_class].append(candidate)
                
    # Pass 2: Class Balancing & Subsampling
    final_selections = []
    
    for cls in INTERNAL_CLASSES:
        candidates = unique_candidates[cls]
        
        # Sort candidates deterministically by MD5 hash before sampling
        candidates.sort(key=lambda x: x["md5_hash"])
        
        if cls == "organic" and len(candidates) > 3000:
            # We want to stratify. Let's group by source dataset.
            sources_groups = defaultdict(list)
            for c in candidates:
                sources_groups[c["ds_name"]].append(c)
                
            sampled_cls = []
            target = 3000
            # Simple proportional sampling if multiple sources exist
            for src, group in sources_groups.items():
                proportion = len(group) / len(candidates)
                src_target = int(target * proportion)
                sampled_cls.extend(random.sample(group, min(len(group), src_target)))
                
            # If we missed a few due to rounding, that's fine.
            stats[cls]["capped"] = len(candidates) - len(sampled_cls)
            final_selections.extend(sampled_cls)
            stats[cls]["final"] = len(sampled_cls)
        else:
            final_selections.extend(candidates)
            stats[cls]["final"] = len(candidates)
            
    # Sort globally before split assignment to ensure determinism regardless of dict orders
    final_selections.sort(key=lambda x: x["md5_hash"])
    
    # Pass 3: Splits and File Writing
    for cand in final_selections:
        md5_hash = cand["md5_hash"]
        hash_int = int(md5_hash, 16)
        split_val = hash_int % 100
        
        if split_val < 80:
            final_split = "Train"
        elif split_val < 90:
            final_split = "Validation"
        else:
            final_split = "Test"
            
        mapped_class = cand["mapped_class"]
        split_dir = os.path.join(CLEAN_DIR, final_split, mapped_class)
        os.makedirs(split_dir, exist_ok=True)
        
        new_img_name = f"{cand['ds_name']}_{cand['source_class']}_{md5_hash[:8]}.jpg"
        clean_path = os.path.join(split_dir, new_img_name)
        
        # Copy file
        with Image.open(cand["img_path"]) as img:
            img.convert("RGB").save(clean_path, "JPEG")
            
        manifest.append({
            "original_filename": cand["img_name"],
            "filename": new_img_name,
            "retained_source_dataset": cand["ds_name"],
            "source_class": cand["source_class"],
            "mapped_class": mapped_class,
            "final_split": final_split,
            "source_license": cand["ds_config"]["license"],
            "source_url": cand["ds_config"]["source_url"],
            "attribution_requirement": cand["ds_config"]["attribution_requirement"],
            "hash": md5_hash,
            "p_hash": cand["p_hash"]
        })
        
    # Write manifest
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=4)
        
    # Generate Report
    print("\n### FINAL DATASET REPORT\n")
    print("| Internal Class | Source(s) | Raw | Corrupt Removed | Exact Duplicates | Perceptual Duplicates | Sampled/Capped | Final |")
    print("|---|---|---:|---:|---:|---:|---:|---:|")
    
    tot_raw = tot_final = 0
    for cls in INTERNAL_CLASSES:
        s = stats[cls]
        tot_raw += s["raw"]
        tot_final += s["final"]
        srcs = ", ".join(sorted(list(s["sources"]))) if s["sources"] else "None"
        print(f"| {cls} | {srcs} | {s['raw']} | {s['corrupt']} | {s['exact_dupes']} | {s['perceptual_dupes']} | {s['capped']} | {s['final']} |")
        
    train_c = len([m for m in manifest if m["final_split"] == "Train"])
    val_c = len([m for m in manifest if m["final_split"] == "Validation"])
    test_c = len([m for m in manifest if m["final_split"] == "Test"])
    
    print(f"\n- **Total raw images**: {tot_raw}")
    print(f"- **Total final images**: {tot_final}")
    print(f"- **Train/Validation/Test counts**: Train: {train_c}, Val: {val_c}, Test: {test_c}")
    print(f"- **Exact split methodology**: Deterministic MD5 modulo (80/10/10)")
    print(f"- **Random seed for sampling**: {SEED}")

if __name__ == "__main__":
    main()
