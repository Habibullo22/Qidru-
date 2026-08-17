import os
import psycopg2


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL topilmadi. Replit Database ulanishini tekshiring."
        )

    return psycopg2.connect(DATABASE_URL)


def init_database():
    with get_connection() as conn:
        with conn.cursor() as cur:

            with open("schema.sql", "r", encoding="utf-8") as file:
                schema = file.read()

            cur.execute(schema)

        conn.commit()

    print("✅ PostgreSQL baza tayyor!")


if __name__ == "__main__":
    init_database()
