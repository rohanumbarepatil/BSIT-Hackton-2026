import sqlite3
import os

DB_PATH = "database/wastesense.db"

try:

    os.makedirs("database", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Connected to SQLite...")

    # USERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        total_points INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        campus TEXT
    );
    """)

    # WASTE TYPES
    cur.execute("""
    CREATE TABLE IF NOT EXISTS waste_types (
        waste_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
        waste_name TEXT UNIQUE NOT NULL,
        eco_points INTEGER NOT NULL
    );
    """)

    # Insert waste types
    cur.execute("""
    INSERT OR IGNORE INTO waste_types (waste_name, eco_points) VALUES
    ('organic',18),
    ('paper',12),
    ('glass',25),
    ('plastic',20),
    ('metal',30),
    ('mixed',15);
    """)

    # WASTE BINS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS waste_bins (
        bin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bin_type TEXT,
        latitude REAL,
        longitude REAL,
        location_name TEXT
    );
    """)

    # Insert Kalinga University bins
    cur.execute("""
    INSERT OR IGNORE INTO waste_bins (bin_type, latitude, longitude, location_name) VALUES
    ('paper',21.251400,81.605000,'Library Recycling Bin'),
    ('plastic',21.251700,81.604400,'Cafeteria Recycling Bin'),
    ('organic',21.252100,81.603900,'Hostel Mess Compost Bin'),
    ('mixed',21.250900,81.605700,'Admin Block Waste Bin');
    """)

    # DISPOSAL LOGS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS waste_disposal_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        waste_type_id INTEGER,
        points_earned INTEGER,
        total_points_after INTEGER,
        latitude REAL,
        longitude REAL,
        disposal_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # BADGES
    cur.execute("""
    CREATE TABLE IF NOT EXISTS badges (
        badge_id INTEGER PRIMARY KEY AUTOINCREMENT,
        badge_name TEXT UNIQUE,
        min_points INTEGER
    );
    """)

    cur.execute("""
    INSERT OR IGNORE INTO badges (badge_name, min_points) VALUES
    ('Eco Beginner',50),
    ('Green Warrior',150),
    ('Recycling Hero',300),
    ('Planet Protector',500);
    """)

    cur.execute("""
    INSERT OR IGNORE INTO badges (badge_name, min_points) VALUES
    ('Eco Starter',300),
    ('Green Guardian',800),
    ('Recycling Champion',1500),
    ('Planet Protector',3000),
    ('Eco Legend',6000);
    """)

    # VOUCHERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vouchers (
        voucher_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        code TEXT UNIQUE,
        reward_type TEXT,
        points_spent INTEGER,
        expires_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # GAME SESSIONS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS game_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        played_on DATE,
        points_awarded INTEGER
    );
    """)

    # REDEMPTIONS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS redemptions (
        redemption_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        points_used INTEGER,
        reward_name TEXT,
        redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()

    print("WasteSense SQLite database initialized successfully!")

    cur.close()
    conn.close()

except Exception as e:
    print("Database setup error:")
    print(e)