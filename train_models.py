import os
import time
import json
import numpy as np
import shutil
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support, accuracy_score

print("Checking YOLO requirements...")
try:
    from ultralytics import YOLO
except ImportError:
    print("Warning: ultralytics not installed. YOLOv8 will fail.")

# Paths
CLEAN_DIR = "dataset/clean"
YOLO_DIR = "dataset/yolo"
REPORTS_DIR = "ml/reports"
MODELS_DIR = "ml/models"

# 7 Classes
CLASSES = ["organic", "paper", "glass", "plastic", "metal", "mixed", "ewaste"]

# Category mapping
CATEGORY_MAP = {
    "organic": "Biodegradable",
    "paper": "Dry Recyclable",
    "glass": "Dry Recyclable",
    "plastic": "Dry Recyclable",
    "metal": "Dry Recyclable",
    "mixed": "Dry Recyclable",
    "ewaste": "Hazardous/E-Waste"
}

def phase1_integrity_check():
    print("--- PHASE 1: Dataset Integrity Check ---")
    splits = ["Train", "Validation", "Test"]
    for split in splits:
        split_path = os.path.join(CLEAN_DIR, split)
        if not os.path.exists(split_path):
            raise Exception(f"Missing split directory: {split_path}")
        found_classes = os.listdir(split_path)
        for cls in CLASSES:
            if cls not in found_classes:
                raise Exception(f"Missing class {cls} in split {split}")
        print(f"Split: {split}")
        for cls in CLASSES:
            c = len(os.listdir(os.path.join(split_path, cls)))
            print(f"  {cls}: {c}")

def setup_yolo_structure():
    if not os.path.exists(YOLO_DIR):
        os.makedirs(YOLO_DIR)
        for old, new in [("Train", "train"), ("Validation", "val"), ("Test", "test")]:
            shutil.copytree(os.path.join(CLEAN_DIR, old), os.path.join(YOLO_DIR, new))

def calculate_metrics(y_true, y_pred, class_indices, model_name, inference_time):
    idx_to_cls = {v: k for k, v in class_indices.items()}
    y_true_cls = [idx_to_cls[i] for i in y_true]
    y_pred_cls = [idx_to_cls[i] for i in y_pred]
    
    acc = accuracy_score(y_true, y_pred)
    mac_p, mac_r, mac_f1, _ = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0)
    
    ewaste_idx = class_indices["ewaste"]
    y_true_ewaste = [1 if i == ewaste_idx else 0 for i in y_true]
    y_pred_ewaste = [1 if i == ewaste_idx else 0 for i in y_pred]
    ew_p, ew_r, ew_f1, _ = precision_recall_fscore_support(y_true_ewaste, y_pred_ewaste, average='binary', zero_division=0)
    
    y_true_3 = [CATEGORY_MAP[c] for c in y_true_cls]
    y_pred_3 = [CATEGORY_MAP[c] for c in y_pred_cls]
    acc_3 = accuracy_score(y_true_3, y_pred_3)
    
    cm = confusion_matrix(y_true_cls, y_pred_cls, labels=CLASSES)
    
    metrics = {
        "Accuracy": acc,
        "Macro Precision": mac_p,
        "Macro Recall": mac_r,
        "Macro F1": mac_f1,
        "E-Waste Precision": ew_p,
        "E-Waste Recall": ew_r,
        "E-Waste F1": ew_f1,
        "3-Category Accuracy": acc_3,
        "Inference Time/Image (ms)": inference_time * 1000,
        "Confusion Matrix": cm.tolist()
    }
    
    return metrics, classification_report(y_true_cls, y_pred_cls, labels=CLASSES, zero_division=0, output_dict=True)

def train_mobilenetv2_pytorch():
    print("\n--- PHASE 2: MobileNetV2 BASELINE (PyTorch) ---")
    
    data_transforms = {
        'Train': transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'Validation': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'Test': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }
    
    image_datasets = {x: datasets.ImageFolder(os.path.join(CLEAN_DIR, x), data_transforms[x]) for x in ['Train', 'Validation', 'Test']}
    dataloaders = {x: DataLoader(image_datasets[x], batch_size=32, shuffle=(x=='Train')) for x in ['Train', 'Validation', 'Test']}
    dataset_sizes = {x: len(image_datasets[x]) for x in ['Train', 'Validation', 'Test']}
    class_indices = image_datasets['Train'].class_to_idx
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    model = models.mobilenet_v2(pretrained=True)
    # Freeze base
    for param in model.parameters():
        param.requires_grad = False
        
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, len(CLASSES))
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.classifier[1].parameters(), lr=0.001)
    
    num_epochs = 1  # Fast prototype for demonstration due to limits
    
    best_model_wts = model.state_dict()
    best_acc = 0.0
    
    t0 = time.time()
    for epoch in range(num_epochs):
        print(f'Epoch {epoch}/{num_epochs - 1}')
        for phase in ['Train', 'Validation']:
            if phase == 'Train':
                model.train()
            else:
                model.eval()
            
            running_corrects = 0
            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)
                
                optimizer.zero_grad()
                with torch.set_grad_enabled(phase == 'Train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    if phase == 'Train':
                        loss = criterion(outputs, labels)
                        loss.backward()
                        optimizer.step()
                running_corrects += torch.sum(preds == labels.data)
                
            epoch_acc = running_corrects.double() / dataset_sizes[phase]
            print(f'{phase} Acc: {epoch_acc:.4f}')
            
            if phase == 'Validation' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = model.state_dict()

    train_time = time.time() - t0
    model.load_state_dict(best_model_wts)
    
    checkpoint_path = os.path.join(MODELS_DIR, 'mobilenetv2_best.pt')
    os.makedirs(MODELS_DIR, exist_ok=True)
    torch.save(model.state_dict(), checkpoint_path)
    
    # Evaluate
    print("Evaluating MobileNetV2 on Test Set...")
    model.eval()
    y_true = []
    y_pred = []
    
    t_inf_start = time.time()
    with torch.no_grad():
        for inputs, labels in dataloaders['Test']:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            y_pred.extend(preds.cpu().numpy())
            y_true.extend(labels.numpy())
            
    t_inf_total = time.time() - t_inf_start
    inf_per_image = t_inf_total / len(y_true)
    
    metrics, cls_report = calculate_metrics(y_true, y_pred, class_indices, "MobileNetV2", inf_per_image)
    metrics["Training Time (s)"] = train_time
    metrics["Model Size (MB)"] = os.path.getsize(checkpoint_path) / (1024 * 1024)
    
    return metrics, cls_report, class_indices

def train_yolov8():
    print("\n--- PHASE 3: YOLOv8-CLS ---")
    setup_yolo_structure()
    
    model = YOLO('yolov8n-cls.pt')
    
    t0 = time.time()
    results = model.train(
        data=os.path.abspath(YOLO_DIR),
        epochs=1,  # Fast prototype
        imgsz=224,
        batch=32,
        project=MODELS_DIR,
        name='yolov8_cls',
        exist_ok=True,
        seed=42
    )
    train_time = time.time() - t0
    
    print("Evaluating YOLOv8 on Test Set...")
    best_model_path = os.path.join(MODELS_DIR, 'yolov8_cls', 'weights', 'best.pt')
    eval_model = YOLO(best_model_path)
    
    test_dir = os.path.join(YOLO_DIR, 'test')
    class_names = sorted(os.listdir(test_dir))
    class_indices = {name: i for i, name in enumerate(class_names)}
    
    y_true = []
    y_pred = []
    
    t_inf_start = time.time()
    for cls_name in class_names:
        cls_dir = os.path.join(test_dir, cls_name)
        img_paths = [os.path.join(cls_dir, f) for f in os.listdir(cls_dir)]
        preds = eval_model(img_paths, verbose=False)
        for p in preds:
            y_pred.append(p.probs.top1)
            y_true.append(class_indices[cls_name])
            
    t_inf_total = time.time() - t_inf_start
    inf_per_image = t_inf_total / len(y_true)
    
    metrics, cls_report = calculate_metrics(y_true, y_pred, class_indices, "YOLOv8-CLS", inf_per_image)
    metrics["Training Time (s)"] = train_time
    metrics["Model Size (MB)"] = os.path.getsize(best_model_path) / (1024 * 1024)
    
    return metrics, cls_report

def main():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    phase1_integrity_check()
    mb_metrics, mb_report, cls_indices = train_mobilenetv2_pytorch()
    
    with open(os.path.join(MODELS_DIR, "class_names.json"), "w") as f:
        json.dump(cls_indices, f)
        
    yolo_metrics, yolo_report = train_yolov8()
    
    print("\n--- PHASE 4: FAIR COMPARISON ---")
    md_content = "# Final Model Comparison Report\n\n"
    md_content += "## 1. Performance Metrics\n\n"
    md_content += "| Metric | MobileNetV2 | YOLOv8-CLS |\n"
    md_content += "|---|---:|---:|\n"
    
    keys_to_compare = [
        "Accuracy", "Macro Precision", "Macro Recall", "Macro F1",
        "E-Waste Precision", "E-Waste Recall", "E-Waste F1",
        "3-Category Accuracy", "Inference Time/Image (ms)", "Model Size (MB)", "Training Time (s)"
    ]
    
    for k in keys_to_compare:
        mb_val = mb_metrics[k]
        yl_val = yolo_metrics[k]
        md_content += f"| {k} | {mb_val:.4f} | {yl_val:.4f} |\n"
        
    md_content += "\n## 2. Model Selection Considerations\n"
    md_content += "- **Classification Performance**: YOLO typically maintains stronger bounds on smaller data, though here we ran abbreviated epochs (1 epoch) for the prototype pipeline.\n"
    md_content += "- **E-Waste Retrieval**: Currently evaluated on `battery` imagery only.\n"
    md_content += "- **Inference Speed**: Measured per image on CPU.\n"
    md_content += "- **Model Size**: YOLO provides smaller deployable architectures, whereas MobileNetV2 depends on standard PyTorch deployment sizes.\n"
    md_content += "- **Important Limitation**: Due to the local prototype training limitation (1 epoch), neither model has reached convergence. Do not select a winner based on this prototype accuracy alone. A full-scale training session on appropriate hardware is required.\n"
    
    with open(os.path.join(REPORTS_DIR, "model_comparison.md"), "w") as f:
        f.write(md_content)
        
    with open(os.path.join(REPORTS_DIR, "evaluation_metrics.json"), "w") as f:
        json.dump({
            "MobileNetV2": mb_metrics,
            "YOLOv8-CLS": yolo_metrics,
            "MobileNetV2_Classes": mb_report,
            "YOLOv8_Classes": yolo_report
        }, f, indent=4)
        
    print("Done. Report saved to ml/reports/model_comparison.md")

if __name__ == "__main__":
    main()
