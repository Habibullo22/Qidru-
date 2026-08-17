import os
from datetime import datetime, timedelta

from database import get_connection


VIP_PRICE = 30000
VIP_DAYS = 7

VIP_CARD = os.getenv("VIP_CARD", "")
VIP_CARD_NAME = os.getenv("VIP_CARD_NAME", "Abidjanov H")


def get_vip_status(user_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT expires_at
                FROM vip_users
                WHERE user_id = %s
                """,
                (user_id,)
            )

            row = cur.fetchone()

            if not row:
                return False, None

            expires_at = row[0]

            if expires_at <= datetime.now():
                return False, expires_at

            return True, expires_at

    finally:
        conn.close()


def get_pending_request(user_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, status
                FROM vip_requests
                WHERE user_id = %s
                  AND status = 'PENDING'
                ORDER BY id DESC
                LIMIT 1
                """,
                (user_id,)
            )

            return cur.fetchone()

    finally:
        conn.close()


def create_vip_request(user_id):
    existing = get_pending_request(user_id)

    if existing:
        return False, "PENDING"

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO vip_requests (
                    user_id,
                    amount,
                    duration_days,
                    status
                )
                VALUES (%s, %s, %s, 'PENDING')
                RETURNING id
                """,
                (
                    user_id,
                    VIP_PRICE,
                    VIP_DAYS
                )
            )

            request_id = cur.fetchone()[0]

        conn.commit()

        return True, request_id

    finally:
        conn.close()


def approve_vip(request_id, admin_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    user_id,
                    amount,
                    duration_days,
                    status
                FROM vip_requests
                WHERE id = %s
                FOR UPDATE
                """,
                (request_id,)
            )

            request = cur.fetchone()

            if not request:
                return False, "NOT_FOUND"

            user_id, amount, days, status = request

            if status != "PENDING":
                return False, status

            now = datetime.now()
            expires = now + timedelta(days=days)

            cur.execute(
                """
                UPDATE vip_requests
                SET
                    status = 'APPROVED',
                    processed_at = CURRENT_TIMESTAMP,
                    processed_by = %s
                WHERE id = %s
                  AND status = 'PENDING'
                """,
                (
                    admin_id,
                    request_id
                )
            )

            if cur.rowcount != 1:
                conn.rollback()
                return False, "ALREADY_PROCESSED"

            cur.execute(
                """
                INSERT INTO vip_users (
                    user_id,
                    started_at,
                    expires_at
                )
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id)
                DO UPDATE SET
                    started_at = EXCLUDED.started_at,
                    expires_at = EXCLUDED.expires_at
                """,
                (
                    user_id,
                    now,
                    expires
                )
            )

        conn.commit()

        return True, user_id

    finally:
        conn.close()


def reject_vip(request_id, admin_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                UPDATE vip_requests
                SET
                    status = 'REJECTED',
                    processed_at = CURRENT_TIMESTAMP,
                    processed_by = %s
                WHERE id = %s
                  AND status = 'PENDING'
                RETURNING user_id
                """,
                (
                    admin_id,
                    request_id
                )
            )

            row = cur.fetchone()

            if not row:
                conn.rollback()
                return False, "ALREADY_PROCESSED"

            user_id = row[0]

        conn.commit()

        return True, user_id

    finally:
        conn.close()


def get_pending_requests():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    user_id,
                    amount,
                    duration_days,
                    created_at
                FROM vip_requests
                WHERE status = 'PENDING'
                ORDER BY created_at ASC
                """
            )

            return cur.fetchall()

    finally:
        conn.close()
