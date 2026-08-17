from database import get_connection


def search_users(query, limit=20):
    query = query.strip().lstrip("@")

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    telegram_id,
                    username,
                    first_name,
                    last_name
                FROM users
                WHERE
                    username ILIKE %s
                    OR first_name ILIKE %s
                    OR last_name ILIKE %s
                    OR CAST(telegram_id AS TEXT) = %s
                ORDER BY last_seen DESC
                LIMIT %s
                """,
                (
                    f"%{query}%",
                    f"%{query}%",
                    f"%{query}%",
                    query,
                    limit
                )
            )

            return cur.fetchall()

    finally:
        conn.close()


def get_username_history(telegram_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT username, detected_at
                FROM username_history
                WHERE telegram_id = %s
                ORDER BY detected_at DESC
                """,
                (telegram_id,)
            )

            return cur.fetchall()

    finally:
        conn.close()


def get_user_chats(telegram_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.telegram_chat_id,
                    c.title,
                    c.username,
                    c.chat_type
                FROM memberships m
                JOIN chats c
                    ON c.telegram_chat_id =
                       m.telegram_chat_id
                WHERE m.telegram_id = %s
                ORDER BY c.title
                """,
                (telegram_id,)
            )

            return cur.fetchall()

    finally:
        conn.close()


def search_messages(query, limit=50):
    query = query.strip()

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    telegram_message_id,
                    telegram_chat_id,
                    author_id,
                    username,
                    text,
                    message_date
                FROM messages
                WHERE text ILIKE %s
                ORDER BY message_date DESC
                LIMIT %s
                """,
                (
                    f"%{query}%",
                    limit
                )
            )

            return cur.fetchall()

    finally:
        conn.close()


def get_user_profile(telegram_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    telegram_id,
                    username,
                    first_name,
                    last_name,
                    first_seen,
                    last_seen
                FROM users
                WHERE telegram_id = %s
                """,
                (telegram_id,)
            )

            return cur.fetchone()

    finally:
        conn.close()
