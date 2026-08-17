import os
from datetime import datetime

from database import get_connection


def save_user(
    telegram_id,
    username=None,
    first_name=None,
    last_name=None
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO users (
                    telegram_id,
                    username,
                    first_name,
                    last_name
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (telegram_id)
                DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    last_seen = CURRENT_TIMESTAMP
                """,
                (
                    telegram_id,
                    username,
                    first_name,
                    last_name
                )
            )

        conn.commit()

    finally:
        conn.close()


def save_username_history(
    telegram_id,
    username
):
    if not username:
        return

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT 1
                FROM username_history
                WHERE telegram_id = %s
                AND username = %s
                LIMIT 1
                """,
                (
                    telegram_id,
                    username
                )
            )

            exists = cur.fetchone()

            if not exists:

                cur.execute(
                    """
                    INSERT INTO username_history (
                        telegram_id,
                        username
                    )
                    VALUES (%s, %s)
                    """,
                    (
                        telegram_id,
                        username
                    )
                )

        conn.commit()

    finally:
        conn.close()


def save_chat(
    chat_id,
    title,
    username,
    chat_type,
    is_public=True
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO chats (
                    telegram_chat_id,
                    title,
                    username,
                    chat_type,
                    is_public
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (telegram_chat_id)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    username = EXCLUDED.username,
                    chat_type = EXCLUDED.chat_type,
                    is_public = EXCLUDED.is_public,
                    last_seen = CURRENT_TIMESTAMP
                """,
                (
                    chat_id,
                    title,
                    username,
                    chat_type,
                    is_public
                )
            )

        conn.commit()

    finally:
        conn.close()


def save_membership(
    telegram_id,
    chat_id
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO memberships (
                    telegram_id,
                    telegram_chat_id
                )
                VALUES (%s, %s)
                ON CONFLICT (
                    telegram_id,
                    telegram_chat_id
                )
                DO NOTHING
                """,
                (
                    telegram_id,
                    chat_id
                )
            )

        conn.commit()

    finally:
        conn.close()


def save_message(
    message_id,
    chat_id,
    author_id,
    username,
    text,
    message_date
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO messages (
                    telegram_message_id,
                    telegram_chat_id,
                    author_id,
                    username,
                    text,
                    message_date
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (
                    telegram_message_id,
                    telegram_chat_id
                )
                DO NOTHING
                """,
                (
                    message_id,
                    chat_id,
                    author_id,
                    username,
                    text,
                    message_date
                )
            )

        conn.commit()

    finally:
        conn.close()


def save_public_message(message):
    """
    Telegram'dan olingan ruxsat etilgan
    public xabar obyektini bazaga saqlash.
    """

    if not message:
        return

    sender = getattr(
        message,
        "sender",
        None
    )

    chat = getattr(
        message,
        "chat",
        None
    )

    if not sender or not chat:
        return

    sender_id = getattr(
        sender,
        "id",
        None
    )

    username = getattr(
        sender,
        "username",
        None
    )

    first_name = getattr(
        sender,
        "first_name",
        None
    )

    last_name = getattr(
        sender,
        "last_name",
        None
    )

    chat_id = getattr(
        chat,
        "id",
        None
    )

    title = getattr(
        chat,
        "title",
        None
    )

    chat_username = getattr(
        chat,
        "username",
        None
    )

    text = getattr(
        message,
        "message",
        None
    )

    message_date = getattr(
        message,
        "date",
        None
    )

    if not sender_id or not chat_id:
        return

    save_user(
        sender_id,
        username,
        first_name,
        last_name
    )

    save_username_history(
        sender_id,
        username
    )

    save_chat(
        chat_id,
        title,
        chat_username,
        "public"
    )

    save_membership(
        sender_id,
        chat_id
    )

    save_message(
        message.id,
        chat_id,
        sender_id,
        username,
        text,
        message_date
    )


print("✅ Collector moduli tayyor.")
