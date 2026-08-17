import os

from telethon import TelegramClient


API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")

SESSION_NAME = "telegram_search_session"


def create_client():

    if not API_ID:
        raise RuntimeError("API_ID topilmadi")

    if not API_HASH:
        raise RuntimeError("API_HASH topilmadi")

    return TelegramClient(
        SESSION_NAME,
        int(API_ID),
        API_HASH
    )


async def connect():

    client = create_client()

    if PHONE:
        await client.start(
            phone=PHONE
        )
    else:
        await client.start()

    print("✅ Telegram client ulandi!")

    return client


async def disconnect(client):

    if client:
        await client.disconnect()


async def test_connection():

    client = await connect()

    try:

        me = await client.get_me()

        print(
            f"✅ Ulangan akkaunt: "
            f"@{me.username or 'username yo‘q'}"
        )

        print(
            f"🆔 Telegram ID: {me.id}"
        )

    finally:

        await disconnect(client)


if __name__ == "__main__":

    import asyncio

    asyncio.run(
        test_connection()
      )
