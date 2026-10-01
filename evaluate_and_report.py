import os
import time
import json
import numpy as np
import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support, accuracy_score
from ultralytics import YOLO

# Paths
CLEAN_DIR = "dataset/clean"
YOLO_DIR = "dataset/yolo"
REPORTS_DIR = "ml/reports"
MODELS_DIR = "ml/models"
YOLO_BEST_PATH = "runs/classify/ml/models/yolov8_cls/weights/best.pt"
MB_BEST_PATH = "ml/models/mobilenetv2_best.pt"

# 7 Classes
CLASSES = ["organic", "paper", "glass", "plastic", "metal", "mixed", "ewaste"]

CATEGORY_MAP = {
    "organic": "Biodegradable",
    "paper": "Dry Recyclable",
    "glass": "Dry Recyclable",
    "plastic": "Dry Recyclable",
    "metal": "Dry Recyclable",
    "mixed": "Dry Recyclable",
    "ewaste": "Hazardous/E-Waste"
}

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

def eval_mobilenetv2():
    print("Evaluating MobileNetV2...")
    data_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    test_dataset = datasets.ImageFolder(os.path.join(CLEAN_DIR, 'Test'), data_transforms)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    class_indices = test_dataset.class_to_idx
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    model = models.mobilenet_v2(pretrained=False)
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, len(CLASSES))
    model.load_state_dict(torch.load(MB_BEST_PATH, map_location=device))
    model = model.to(device)
    model.eval()
    
    y_true = []
    y_pred = []
    
    t_inf_start = time.time()
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            y_pred.extend(preds.cpu().numpy())
            y_true.extend(labels.numpy())
            
    t_inf_total = time.time() - t_inf_start
    inf_per_image = t_inf_total / len(y_true)
    
    metrics, cls_report = calculate_metrics(y_true, y_pred, class_indices, "MobileNetV2", inf_per_image)
    metrics["Model Size (MB)"] = os.path.getsize(MB_BEST_PATH) / (1024 * 1024)
    return metrics, cls_report

def eval_yolo():
    print("Evaluating YOLOv8...")
    eval_model = YOLO(YOLO_BEST_PATH)
    
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
    metrics["Model Size (MB)"] = os.path.getsize(YOLO_BEST_PATH) / (1024 * 1024)
    return metrics, cls_report

def main():
    mb_metrics, mb_report = eval_mobilenetv2()
    yolo_metrics, yolo_report = eval_yolo()
    
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    md_content = "# Final Model Comparison Report\n\n"
    md_content += "## 1. Performance Metrics\n\n"
    md_content += "| Metric | MobileNetV2 | YOLOv8-CLS |\n"
    md_content += "|---|---:|---:|\n"
    
    keys_to_compare = [
        "Accuracy", "Macro Precision", "Macro Recall", "Macro F1",
        "E-Waste Precision", "E-Waste Recall", "E-Waste F1",
        "3-Category Accuracy", "Inference Time/Image (ms)", "Model Size (MB)"
    ]
    
    for k in keys_to_compare:
        mb_val = mb_metrics[k]
        yl_val = yolo_metrics[k]
        md_content += f"| {k} | {mb_val:.4f} | {yl_val:.4f} |\n"
        
    md_content += "\n## 2. Model Selection Considerations\n"
    md_content += "- **Classification Performance**: See table above. (Note: Only trained for 1 epoch as a pipeline prototype).\n"
    md_content += "- **E-Waste Retrieval**: Currently evaluated on `battery` imagery only.\n"
    md_content += "- **Inference Speed**: Measured per image on CPU.\n"
    md_content += "- **Model Size**: YOLO provides smaller deployable architectures, whereas MobileNetV2 depends on PyTorch deployment sizes.\n"
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
