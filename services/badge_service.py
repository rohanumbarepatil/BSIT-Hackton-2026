# services/badge_service.py

from database.db_connection import get_connection


def check_and_assign_badges(user_id):

    conn = get_connection()
    cur = conn.cursor()

    # Get user total points
    cur.execute("""
        SELECT total_points
        FROM users
        WHERE user_id = %s
    """, (user_id,))

    result = cur.fetchone()

    if not result:
        cur.close()
        conn.close()
        return

    total_points = result[0]

    # Find badges the user qualifies for
    cur.execute("""
        SELECT badge_id
        FROM badges
        WHERE min_points <= %s
    """, (total_points,))

    eligible_badges = cur.fetchall()

    for badge in eligible_badges:

        badge_id = badge[0]

        # Check if user already has badge
        cur.execute("""
            SELECT *
            FROM user_badges
            WHERE user_id=%s AND badge_id=%s
        """, (user_id, badge_id))

        already_has = cur.fetchone()

        if not already_has:

            cur.execute("""
                INSERT INTO user_badges (user_id, badge_id)
                VALUES (%s,%s)
            """, (user_id, badge_id))

    conn.commit()

    cur.close()
    conn.close()