import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS


def get_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS
    )


def setup_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id       SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions (
            id            SERIAL PRIMARY KEY,
            player_id     INTEGER REFERENCES players(id),
            score         INTEGER NOT NULL,
            level_reached INTEGER NOT NULL,
            played_at     TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def get_or_create_player(username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING",
        (username,)
    )
    conn.commit()
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    pid = cur.fetchone()[0]
    cur.close()
    conn.close()
    return pid


def save_session(player_id, score, level):
    conn = get_conn()
    cur = conn.cursor()
    # check if player already has a session, keep only the best score
    cur.execute("SELECT id, score FROM game_sessions WHERE player_id = %s", (player_id,))
    existing = cur.fetchone()
    if existing:
        if score > existing[1]:
            # update to new best
            cur.execute(
                "UPDATE game_sessions SET score = %s, level_reached = %s, played_at = NOW() WHERE id = %s",
                (score, level, existing[0])
            )
    else:
        cur.execute(
            "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
            (player_id, score, level)
        )
    conn.commit()
    cur.close()
    conn.close()


def get_leaderboard():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.username, gs.score, gs.level_reached, gs.played_at::date
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        ORDER BY gs.score DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_personal_best(player_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT MAX(score) FROM game_sessions WHERE player_id = %s", (player_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] or 0
