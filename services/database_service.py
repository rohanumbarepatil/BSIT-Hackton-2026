# services/database_service.py

from database.db_connection import get_connection


# ------------------------------------------------
# WASTE SCAN / POINT SYSTEM
# ------------------------------------------------

def log_waste_scan(user_id, waste_type_id, points, lat, lon):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO waste_disposal_logs
        (user_id, waste_type_id, points_earned, latitude, longitude)
        VALUES (%s,%s,%s,%s,%s)
    """, (user_id, waste_type_id, points, lat, lon))

    conn.commit()

    cur.close()
    conn.close()


def update_user_points(user_id, points):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET total_points = total_points + %s
        WHERE user_id = %s
    """, (points, user_id))

    conn.commit()

    cur.close()
    conn.close()


def get_waste_type_id(waste_name):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT waste_type_id
        FROM waste_types
        WHERE waste_name = %s
    """, (waste_name,))

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result[0] if result else None


# ------------------------------------------------
# USER AUTH / MANAGEMENT
# ------------------------------------------------

def create_user(name, email, password):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (username, email, password_hash, total_points)
        VALUES (%s,%s,%s,0)
        RETURNING user_id
    """, (name, email, password))

    user_id = cur.fetchone()[0]

    conn.commit()

    cur.close()
    conn.close()

    return user_id


def get_user_by_email(email):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, username, email, password_hash
        FROM users
        WHERE email = %s
    """, (email,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return {
            "user_id": row[0],
            "name": row[1],
            "email": row[2],
            "password": row[3]
        }

    return None


# ------------------------------------------------
# DASHBOARD DATA
# ------------------------------------------------

def get_user_dashboard(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT total_points
        FROM users
        WHERE user_id = %s
    """, (user_id,))

    points_result = cur.fetchone()
    points = points_result[0] if points_result else 0

    cur.execute("""
        SELECT COUNT(*)
        FROM waste_disposal_logs
        WHERE user_id = %s
    """, (user_id,))

    scans_result = cur.fetchone()
    scans = scans_result[0] if scans_result else 0

    cur.execute("""
        SELECT wt.waste_name, COUNT(*)
        FROM waste_disposal_logs w
        JOIN waste_types wt ON w.waste_type_id = wt.waste_type_id
        WHERE w.user_id = %s
        GROUP BY wt.waste_name
    """, (user_id,))

    waste_distribution = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "points": points,
        "scans": scans,
        "waste_distribution": waste_distribution
    }


# ------------------------------------------------
# BADGES
# ------------------------------------------------

def get_user_badges(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT b.badge_name
        FROM user_badges ub
        JOIN badges b ON ub.badge_id = b.badge_id
        WHERE ub.user_id = %s
    """, (user_id,))

    badges = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return badges


# ------------------------------------------------
# USER LIST
# ------------------------------------------------

def get_all_users_from_db():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, username, email, total_points
        FROM users
        ORDER BY total_points DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    users = []

    for row in rows:
        users.append({
            "user_id": row[0],
            "name": row[1],
            "email": row[2],
            "points": row[3]
        })

    return users


# ------------------------------------------------
# ANALYTICS
# ------------------------------------------------

def get_waste_heatmap_data():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT latitude, longitude, COUNT(*)
        FROM waste_disposal_logs
        GROUP BY latitude, longitude
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    data = []

    for row in rows:
        data.append({
            "lat": row[0],
            "lon": row[1],
            "count": row[2]
        })

    return data


def get_waste_type_stats():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT wt.waste_name, COUNT(*)
        FROM waste_disposal_logs w
        JOIN waste_types wt ON w.waste_type_id = wt.waste_type_id
        GROUP BY wt.waste_name
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    data = []

    for row in rows:
        data.append({
            "waste_type": row[0],
            "count": row[1]
        })

    return data


def get_daily_waste_trend():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DATE(disposal_time), COUNT(*)
        FROM waste_disposal_logs
        GROUP BY DATE(disposal_time)
        ORDER BY DATE(disposal_time)
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    data = []

    for row in rows:
        data.append({
            "date": str(row[0]),
            "count": row[1]
        })

    return data


# ------------------------------------------------
# LEADERBOARD
# ------------------------------------------------

def get_leaderboard():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT username, total_points
        FROM users
        ORDER BY total_points DESC
        LIMIT 10
    """)

    rows = cur.fetchall()

    leaderboard = []

    rank = 1

    for row in rows:

        leaderboard.append({
            "rank": rank,
            "username": row[0],
            "points": row[1]
        })

        rank += 1

    cur.close()
    conn.close()

    return leaderboard


# ------------------------------------------------
# VOUCHER / REWARD SYSTEM
# ------------------------------------------------

def get_user_points(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT total_points
        FROM users
        WHERE user_id = %s
    """, (user_id,))

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result[0] if result else 0


def redeem_voucher(user_id, reward_type, points_spent, code):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO vouchers (user_id, code, reward_type, points_spent)
        VALUES (%s,%s,%s,%s)
    """, (user_id, code, reward_type, points_spent))

    cur.execute("""
        UPDATE users
        SET total_points = total_points - %s
        WHERE user_id = %s
    """, (points_spent, user_id))

    conn.commit()

    cur.close()
    conn.close()

    return {
        "status": "success",
        "voucher_code": code
    }


# ------------------------------------------------
# DISPOSAL SUPPORT
# ------------------------------------------------

def log_disposal(user_id, waste_type, points, lat=None, lon=None):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT waste_type_id
        FROM waste_types
        WHERE waste_name = %s
    """, (waste_type,))

    result = cur.fetchone()

    if not result:

        cur.close()
        conn.close()

        return {
            "status": "error",
            "message": "Invalid waste type"
        }

    waste_type_id = result[0]

    cur.execute("""
        INSERT INTO waste_disposal_logs
        (user_id, waste_type_id, points_earned, latitude, longitude)
        VALUES (%s,%s,%s,%s,%s)
    """, (user_id, waste_type_id, points, lat, lon))

    cur.execute("""
        UPDATE users
        SET total_points = total_points + %s
        WHERE user_id = %s
    """, (points, user_id))

    conn.commit()

    cur.close()
    conn.close()

    return {
        "status": "success",
        "points_awarded": points
    }


# ------------------------------------------------
# USER PROFILE
# ------------------------------------------------

def get_user_profile(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT username, total_points
        FROM users
        WHERE user_id = %s
    """, (user_id,))

    user = cur.fetchone()

    if not user:

        cur.close()
        conn.close()

        return None

    username = user[0]
    points = user[1]

    cur.execute("""
        SELECT COUNT(*)
        FROM waste_disposal_logs
        WHERE user_id = %s
    """, (user_id,))

    scans = cur.fetchone()[0]

    level = 1

    if points >= 6000:
        level = 5
    elif points >= 3000:
        level = 4
    elif points >= 1500:
        level = 3
    elif points >= 500:
        level = 2

    cur.close()
    conn.close()

    return {
        "username": username,
        "points": points,
        "level": level,
        "scans": scans
    }