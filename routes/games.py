from flask import Blueprint, request, jsonify
from database.db_connection import get_connection
from datetime import date

games_bp = Blueprint("games", __name__)


@games_bp.route("/api/game/complete", methods=["POST"])
def complete_game():

    data = request.get_json()

    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    conn = get_connection()
    cur = conn.cursor()

    today = date.today()

    # count games played today
    cur.execute("""
        SELECT COUNT(*)
        FROM game_sessions
        WHERE user_id = %s AND played_on = %s
    """, (user_id, today))

    games_today = cur.fetchone()[0]

    if games_today >= 3:
        cur.close()
        conn.close()
        return jsonify({"error": "Daily game limit reached"}), 403

    points = 10

    # insert game session
    cur.execute("""
        INSERT INTO game_sessions (user_id, played_on, points_awarded)
        VALUES (%s,%s,%s)
    """, (user_id, today, points))

    # update user points
    cur.execute("""
        UPDATE users
        SET total_points = total_points + %s
        WHERE user_id = %s
    """, (points, user_id))

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        "message": "Game completed",
        "points_awarded": points
    }) 