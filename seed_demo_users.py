from db.database import SessionLocal
from db.models import User
import hashlib
import uuid

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

demo_users = [
    {
        "name": "Demo Student",
        "email": "student@wastesense.ai",
        "password_hash": hash_password("student123"),
        "role": "student"
    },
    {
        "name": "Demo Staff",
        "email": "staff@wastesense.ai",
        "password_hash": hash_password("staff123"),
        "role": "staff"
    },
    {
        "name": "Demo Admin",
        "email": "admin@wastesense.ai",
        "password_hash": hash_password("admin123"),
        "role": "admin"
    },
    {
        "name": "Demo Recycler",
        "email": "recycler@wastesense.ai",
        "password_hash": hash_password("recycler123"),
        "role": "recycler"
    }
]

db = SessionLocal()
for u_data in demo_users:
    user = db.query(User).filter(User.email == u_data["email"]).first()
    if not user:
        user = User(**u_data)
        db.add(user)
    else:
        user.password_hash = u_data["password_hash"]
        user.role = u_data["role"]
db.commit()
print("Demo users seeded successfully.")
