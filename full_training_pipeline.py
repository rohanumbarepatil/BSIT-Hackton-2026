import os
import time
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import copy
try:
    from ultralytics import YOLO
except ImportError:
    pass

# Load config
with open("training_config.json", "r") as f:
    CONFIG = json.load(f)

# Hardcoded Mappings
CLASSES = ["organic", "paper", "glass", "plastic", "metal", "mixed", "ewaste"]
CATEGORY_MAP = {
    "organic": "Biodegradable",
    "paper": "Dry Recyclable",
    "glass": "Dry Recyclable",
    "plastic": "Dry Recyclable",
    "metal": "Dry Recyclable",
    "mixed": "Mixed/Uncertain guidance",
    "ewaste": "Hazardous/E-Waste"
}

REPORTS_DIR = "ml/reports"
MODELS_DIR = "ml/models"
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Ensure reproducibility
torch.manual_seed(CONFIG["seed"])
np.random.seed(CONFIG["seed"])

def plot_curves(train_losses, val_losses, train_accs, val_accs, model_name):
    epochs = range(1, len(train_losses) + 1)
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(epochs, train_losses, label='Train Loss')
    plt.plot(epochs, val_losses, label='Validation Loss')
    plt.title(f'{model_name} Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(epochs, train_accs, label='Train Acc')
    plt.plot(epochs, val_accs, label='Validation Acc')
    plt.title(f'{model_name} Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    
    plt.savefig(os.path.join(REPORTS_DIR, f"{model_name.lower()}_training_curves.png"))
    plt.close()

def plot_cm(cm, model_name):
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=CLASSES, yticklabels=CLASSES)
    plt.title(f"{model_name} Confusion Matrix")
    plt.ylabel('True')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, f"{model_name.lower()}_confusion_matrix.png"))
    plt.close()

def evaluate_model(y_true, y_pred, class_indices, model_name, inf_time, size_mb, train_time, epochs_run, best_epoch, stop_reason):
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
    plot_cm(cm, model_name)
    
    metrics = {
        "Accuracy": acc,
        "Macro Precision": mac_p,
        "Macro Recall": mac_r,
        "Macro F1": mac_f1,
        "E-Waste Precision": ew_p,
        "E-Waste Recall": ew_r,
        "E-Waste F1": ew_f1,
        "3-Category Accuracy": acc_3,
        "Inference Time/Image (ms)": inf_time * 1000,
        "Model Size (MB)": size_mb,
        "Training Time (s)": train_time,
        "Epochs Run": epochs_run,
        "Best Epoch": best_epoch,
        "Early Stopping Condition": stop_reason
    }
    
    cls_report = classification_report(y_true_cls, y_pred_cls, labels=CLASSES, zero_division=0, output_dict=True)
    return metrics, cls_report

def train_mobilenetv2():
    print("--- Starting Full MobileNetV2 Training ---")
    device = torch.device(CONFIG["hardware"] if torch.cuda.is_available() else "cpu")
    print(f"Hardware: {device}")
    
    # Strictly isolate augmentation to Train
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(CONFIG["training"]["image_size"]),
        transforms.RandomHorizontalFlip(p=CONFIG["augmentation"]["random_horizontal_flip"]),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    eval_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(CONFIG["training"]["image_size"]),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    dirs = {
        "Train": os.path.join(CONFIG["dataset"]["base_dir"], CONFIG["dataset"]["train_split"]),
        "Validation": os.path.join(CONFIG["dataset"]["base_dir"], CONFIG["dataset"]["val_split"]),
        "Test": os.path.join(CONFIG["dataset"]["base_dir"], CONFIG["dataset"]["test_split"])
    }
    
    datasets_dict = {
        "Train": datasets.ImageFolder(dirs["Train"], train_transform),
        "Validation": datasets.ImageFolder(dirs["Validation"], eval_transform),
        "Test": datasets.ImageFolder(dirs["Test"], eval_transform)
    }
    
    loaders = {
        x: DataLoader(datasets_dict[x], batch_size=CONFIG["training"]["batch_size"], shuffle=(x=='Train'))
        for x in ['Train', 'Validation', 'Test']
    }
    
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
    
    # 1. Freeze Backbone
    for param in model.parameters():
        param.requires_grad = False
        
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, CONFIG["dataset"]["num_classes"])
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    
    def run_training_loop(model, optimizer, epochs, patience, stage_name):
        best_model_wts = copy.deepcopy(model.state_dict())
        best_loss = float('inf')
        epochs_no_improve = 0
        best_epoch = 0
        
        hist = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
        
        for epoch in range(epochs):
            print(f"[{stage_name}] Epoch {epoch+1}/{epochs}")
            for phase in ['Train', 'Validation']:
                if phase == 'Train': model.train()
                else: model.eval()
                
                run_loss = 0.0
                run_corrects = 0
                
                for inputs, labels in loaders[phase]:
                    inputs, labels = inputs.to(device), labels.to(device)
                    optimizer.zero_grad()
                    with torch.set_grad_enabled(phase == 'Train'):
                        outputs = model(inputs)
                        loss = criterion(outputs, labels)
                        _, preds = torch.max(outputs, 1)
                        if phase == 'Train':
                            loss.backward()
                            optimizer.step()
                    run_loss += loss.item() * inputs.size(0)
                    run_corrects += torch.sum(preds == labels.data)
                    
                epoch_loss = run_loss / len(datasets_dict[phase])
                epoch_acc = run_corrects.double() / len(datasets_dict[phase])
                
                if phase == 'Train':
                    hist["train_loss"].append(epoch_loss)
                    hist["train_acc"].append(epoch_acc.item())
                else:
                    hist["val_loss"].append(epoch_loss)
                    hist["val_acc"].append(epoch_acc.item())
                    print(f"Val Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")
                    
                    if epoch_loss < best_loss:
                        best_loss = epoch_loss
                        best_epoch = epoch + 1
                        best_model_wts = copy.deepcopy(model.state_dict())
                        epochs_no_improve = 0
                    else:
                        epochs_no_improve += 1
                        
            if epochs_no_improve >= patience:
                print("Early stopping triggered.")
                break
                
        model.load_state_dict(best_model_wts)
        return hist, (epoch + 1), best_epoch, (epochs_no_improve >= patience)

    t0 = time.time()
    
    # Train head
    opt_head = optim.Adam(model.classifier[1].parameters(), lr=CONFIG["training"]["mobilenet"]["head_lr"])
    h1, e1, b1, s1 = run_training_loop(model, opt_head, CONFIG["training"]["mobilenet"]["head_epochs"], CONFIG["training"]["mobilenet"]["patience"], "Head")
    
    # Fine-tune top layers
    for param in model.features[-4:].parameters():
        param.requires_grad = True
    opt_ft = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=CONFIG["training"]["mobilenet"]["finetune_lr"])
    h2, e2, b2, s2 = run_training_loop(model, opt_ft, CONFIG["training"]["mobilenet"]["finetune_epochs"], CONFIG["training"]["mobilenet"]["patience"], "FineTune")
    
    total_time = time.time() - t0
    
    # Combine history
    full_hist = {k: h1[k] + h2[k] for k in h1.keys()}
    plot_curves(full_hist["train_loss"], full_hist["val_loss"], full_hist["train_acc"], full_hist["val_acc"], "MobileNetV2")
    
    torch.save(model.state_dict(), os.path.join(MODELS_DIR, "mobilenetv2_best.pt"))
    size_mb = os.path.getsize(os.path.join(MODELS_DIR, "mobilenetv2_best.pt")) / (1024*1024)
    
    # Exact Once Evaluation on Untouched Test Set
    model.eval()
    y_true, y_pred = [], []
    t_inf = time.time()
    with torch.no_grad():
        for inputs, labels in loaders['Test']:
            outputs = model(inputs.to(device))
            _, preds = torch.max(outputs, 1)
            y_pred.extend(preds.cpu().numpy())
            y_true.extend(labels.numpy())
            
    inf_ms = (time.time() - t_inf) / len(y_true)
    reason = "Val Loss plateau" if (s1 or s2) else "Max Epochs Reached"
    
    metrics, cls_rep = evaluate_model(y_true, y_pred, datasets_dict['Train'].class_to_idx, "MobileNetV2", inf_ms, size_mb, total_time, (e1+e2), (b1 if b2==0 else e1+b2), reason)
    return metrics, cls_rep, datasets_dict['Train'].class_to_idx

def train_yolov8():
    print("--- Starting Full YOLOv8-CLS Training ---")
    model = YOLO(CONFIG["training"]["yolo"]["model_variant"])
    t0 = time.time()
    results = model.train(
        data=os.path.abspath(CONFIG["dataset"]["yolo_dir"]),
        epochs=CONFIG["training"]["yolo"]["epochs"],
        patience=CONFIG["training"]["yolo"]["patience"],
        imgsz=CONFIG["training"]["image_size"],
        batch=CONFIG["training"]["batch_size"],
        project=MODELS_DIR,
        name='yolov8_cls_full',
        exist_ok=True,
        seed=CONFIG["seed"]
    )
    total_time = time.time() - t0
    
    # Extract learning curves from YOLO CSV if exists
    try:
        import pandas as pd
        df = pd.read_csv(os.path.join(MODELS_DIR, "yolov8_cls_full", "results.csv"))
        df.columns = df.columns.str.strip()
        plot_curves(df["train/loss"], df["val/loss"], df["metrics/accuracy_top1"], df["metrics/accuracy_top1"], "YOLOv8")
    except Exception as e:
        print("Could not plot YOLO curves automatically:", e)
        
    best_pt = os.path.join(MODELS_DIR, "yolov8_cls_full", "weights", "best.pt")
    size_mb = os.path.getsize(best_pt) / (1024*1024)
    
    eval_model = YOLO(best_pt)
    test_dir = os.path.join(CONFIG["dataset"]["yolo_dir"], "test")
    class_names = sorted(os.listdir(test_dir))
    class_indices = {name: i for i, name in enumerate(class_names)}
    
    y_true, y_pred = [], []
    t_inf = time.time()
    for cls_name in class_names:
        cls_dir = os.path.join(test_dir, cls_name)
        img_paths = [os.path.join(cls_dir, f) for f in os.listdir(cls_dir)]
        preds = eval_model(img_paths, verbose=False)
        for p in preds:
            y_pred.append(p.probs.top1)
            y_true.append(class_indices[cls_name])
            
    inf_ms = (time.time() - t_inf) / len(y_true)
    
    # YOLO handles early stopping internally, we estimate based on results obj if needed
    epochs_run = len(results.results_dict) if hasattr(results, 'results_dict') else CONFIG["training"]["yolo"]["epochs"]
    metrics, cls_rep = evaluate_model(y_true, y_pred, class_indices, "YOLOv8", inf_ms, size_mb, total_time, epochs_run, "Auto", "Internal YOLO Patience")
    return metrics, cls_rep

def generate_report(mb_metrics, yolo_metrics):
    md = "# Final Model Evaluation & Comparison (Full Training)\n\n"
    
    md += "## E-Waste Training Limitation\n"
    md += "> **IMPORTANT**: The ewaste class currently contains battery imagery only. The model does NOT detect all forms of e-waste. PCB, laptop, keyboard, mouse, mobile phone, printer, and other institutional e-waste categories are explicitly not represented in the current training data.\n\n"
    
    md += "## 1. Primary Metrics\n"
    md += "| Metric | MobileNetV2 | YOLOv8-CLS |\n|---|---:|---:|\n"
    for k in ["Accuracy", "Macro Precision", "Macro Recall", "Macro F1", "3-Category Accuracy", "Inference Time/Image (ms)", "Model Size (MB)"]:
        md += f"| {k} | {mb_metrics[k]:.4f} | {yolo_metrics[k]:.4f} |\n"
        
    md += "\n## 2. E-Waste Specific Retrieval\n"
    md += "| Metric | MobileNetV2 | YOLOv8-CLS |\n|---|---:|---:|\n"
    for k in ["E-Waste Precision", "E-Waste Recall", "E-Waste F1"]:
        md += f"| {k} | {mb_metrics[k]:.4f} | {yolo_metrics[k]:.4f} |\n"
        
    md += "\n## 3. Training Telemetry\n"
    md += "| Metric | MobileNetV2 | YOLOv8-CLS |\n|---|---:|---:|\n"
    for k in ["Training Time (s)", "Epochs Run", "Best Epoch", "Early Stopping Condition"]:
        md += f"| {k} | {mb_metrics[k]} | {yolo_metrics[k]} |\n"
        
    md += "\n## 4. Hardware & Architecture\n"
    md += f"- **Hardware Used**: {CONFIG['hardware']}\n"
    md += f"- **Image Resolution**: {CONFIG['training']['image_size']}x{CONFIG['training']['image_size']}\n"
    md += f"- **Batch Size**: {CONFIG['training']['batch_size']}\n"
    md += f"- **MobileNet Optimizer**: {CONFIG['training']['mobilenet']['optimizer']}\n"
    md += f"- **YOLO Optimizer**: {CONFIG['training']['yolo']['optimizer']}\n"
    
    with open(os.path.join(REPORTS_DIR, "final_model_comparison.md"), "w") as f:
        f.write(md)

def main():
    print("WARNING: This full training script is designed to run for many hours on CPU.")
    mb_metrics, mb_report, cls_indices = train_mobilenetv2()
    yolo_metrics, yolo_report = train_yolov8()
    
    generate_report(mb_metrics, yolo_metrics)
    
    with open(os.path.join(REPORTS_DIR, "final_metrics.json"), "w") as f:
        json.dump({
            "MobileNetV2": mb_metrics,
            "YOLOv8-CLS": yolo_metrics,
            "MobileNetV2_Classes": mb_report,
            "YOLOv8_Classes": yolo_report
        }, f, indent=4)
        
    print("Full training complete. Artifacts saved in ml/reports/")

if __name__ == "__main__":
    main()
