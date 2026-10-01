# Final Model Comparison Report

## 1. Performance Metrics

| Metric | MobileNetV2 | YOLOv8-CLS |
|---|---:|---:|
| Accuracy | 0.8794 | 0.9057 |
| Macro Precision | 0.8723 | 0.8816 |
| Macro Recall | 0.8537 | 0.8893 |
| Macro F1 | 0.8605 | 0.8846 |
| E-Waste Precision | 0.9545 | 0.8641 |
| E-Waste Recall | 0.8842 | 0.9368 |
| E-Waste F1 | 0.9180 | 0.8990 |
| 3-Category Accuracy | 0.9693 | 0.9656 |
| Inference Time/Image (ms) | 53.6167 | 17.1408 |
| Model Size (MB) | 8.7495 | 2.8379 |

## 2. Model Selection Considerations
- **Classification Performance**: See table above. (Note: Only trained for 1 epoch as a pipeline prototype).
- **E-Waste Retrieval**: Currently evaluated on `battery` imagery only.
- **Inference Speed**: Measured per image on CPU.
- **Model Size**: YOLO provides smaller deployable architectures, whereas MobileNetV2 depends on PyTorch deployment sizes.
- **Important Limitation**: Due to the local prototype training limitation (1 epoch), neither model has reached convergence. Do not select a winner based on this prototype accuracy alone. A full-scale training session on appropriate hardware is required.
