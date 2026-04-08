# ♻️ WasteSense AI — Smart Waste Classification System

> An AI-powered campus waste management system built with Deep Learning, Flask, and PostgreSQL.  
> **Presented at NHIDE-2026 National Hackathon, GGV Bilaspur** 🏆

---

## 🚀 Overview

WasteSense AI is a full-stack intelligent waste management platform that uses **MobileNetV2 deep learning** to classify waste into 6 categories in real-time. The system rewards eco-friendly disposal behaviour through an **Eco Points & Leaderboard** system, ensuring data integrity through **GPS-based bin proximity validation** and **duplicate scan detection**.

---

## 🧠 Features

- 🔍 **AI Waste Classification** — MobileNetV2 model classifies waste into: `organic`, `paper`, `glass`, `plastic`, `metal`, `mixed`
- 📍 **GPS Bin Proximity Validation** — Confirms disposal at the correct bin within 5-metre accuracy (100m threshold)
- 🔁 **Duplicate Scan Detection** — Prevents fraudulent eco-point farming
- 🏆 **Eco Points & Leaderboard** — Rewards users for correct disposal; ranked leaderboard across campus
- 🎁 **Rewards & Vouchers** — Users redeem eco-points for vouchers and badges
- 🎮 **Gamification** — Mini-games and challenges to encourage eco-friendly habits
- 📊 **Analytics Dashboard** — Disposal trends, category breakdowns, and campus-wide stats
- 🔐 **JWT Authentication** — Secure role-based login system
- 👤 **User Profiles** — Disposal history, eco-points balance, badge collection

---

## 🗂️ Project Structure

```
WasteSense-2/
│
├── app.py                  # Flask application factory & entry point
├── config.py               # App configuration (model, bins, eco-points, JWT)
├── train_model.py          # MobileNetV2 model training script
├── requirements.txt        # Python dependencies
│
├── routes/                 # Flask Blueprint API routes
│   ├── auth.py             # Registration & JWT login
│   ├── predict.py          # Waste image classification endpoint
│   ├── disposal.py         # Disposal confirmation with GPS validation
│   ├── dispose.py          # Disposal logic handler
│   ├── users.py            # User management
│   ├── leaderboard.py      # Eco-points leaderboard
│   ├── analytics.py        # Disposal analytics & stats
│   ├── rewards.py          # Rewards system
│   ├── vouchers.py         # Voucher redemption
│   ├── games.py            # Gamification routes
│   ├── bins.py             # Campus bin locations
│   └── user_profile.py     # User profile & history
│
├── models/
│   └── waste_model.py      # SQLAlchemy ORM database models
│
├── services/               # Business logic layer
│   ├── database_service.py # Core DB operations (PostgreSQL via psycopg2)
│   ├── badge_service.py    # Badge assignment logic
│   ├── bin_locator.py      # GPS distance calculation
│   ├── eco_points.py       # Eco-points calculation
│   └── image_similarity.py # Duplicate scan detection
│
├── utils/                  # Utility helpers
│   ├── image_processing.py # Image preprocessing for model input
│   └── location_utils.py   # Haversine distance & GPS utilities
│
├── trained_model/
│   └── wastesense_model.h5 # Trained MobileNetV2 model (not tracked in Git)
│
├── dataset/                # Training data (not tracked in Git)
│   ├── train/
│   └── val/
│
└── frontend/               # HTML/CSS/JS frontend
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **AI / ML** | TensorFlow, MobileNetV2, scikit-learn, OpenCV |
| **Backend** | Python, Flask, Flask-JWT-Extended, Flask-CORS |
| **Database** | PostgreSQL, SQLAlchemy ORM, psycopg2 |
| **Frontend** | HTML, CSS, JavaScript, REST API |
| **Tools** | Git, VS Code, Jupyter Notebook |

---

## 🏷️ Waste Categories & Eco Points

| Category | Eco Points |
|---|---|
| 🥬 Organic | 80 pts |
| 📄 Paper | 100 pts |
| 🍶 Glass | 120 pts |
| 🧴 Plastic | 150 pts |
| 🔩 Metal | 200 pts |
| 🗑️ Mixed | 60 pts |

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/ShibamKhadanga/WasteSense-AI.git
cd WasteSense-AI
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL
Set up your PostgreSQL database and update connection settings in `services/database_service.py`.

### 5. Run the Application
```bash
python app.py
```
The API will be live at: `http://127.0.0.1:5000`

---

## 🤖 Model Training

The model uses **MobileNetV2** (pretrained on ImageNet) with transfer learning, fine-tuned on a 6-class waste dataset.

```bash
# Prepare dataset in:
# dataset/train/<category>/
# dataset/val/<category>/

python train_model.py
# Saves: wastesense_model.h5
```

**Training Config:**
- Image Size: 224×224
- Batch Size: 32
- Epochs: 10
- Optimizer: Adam (lr=0.0001)
- Classes: 6 (organic, paper, glass, plastic, metal, mixed)

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login & get JWT token |
| POST | `/predict` | Classify waste image |
| POST | `/dispose` | Confirm disposal with GPS |
| GET | `/leaderboard` | Get eco-points leaderboard |
| GET | `/analytics` | Get disposal analytics |
| GET | `/rewards` | View available rewards |
| POST | `/vouchers` | Redeem voucher |
| GET | `/bins` | Get nearby bin locations |
| GET | `/profile` | Get user profile & history |

---

## 🏆 Hackathon

This project was built and presented at:

> **NHIDE-2026 — National Hackathon for Innovation, Design & Entrepreneurship**  
> Guru Ghasidas Vishwavidyalaya (GGV), Bilaspur, Chhattisgarh  
> **Team Size:** 4 members (AI/ML · Frontend · Backend)

---

## 👨‍💻 Author

**Shibam Khadanga**  
B.Tech Computer Science, Kalinga University (CGPA: 8.5)  
📧 shibamkhadanga947@gmail.com  
🔗 [LinkedIn](http://www.linkedin.com/in/shibam-khadanga-b91436286) | [GitHub](https://github.com/ShibamKhadanga) | [LeetCode](https://leetcode.com/u/Shibam_Khadanga/)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
