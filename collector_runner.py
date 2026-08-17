import os
import asyncio

from telegram_client import create_client
from collector import save_public_message


CHAT_USERNAME = os.getenv("COLLECT_CHAT")


async def collect_chat():

    if not CHAT_USERNAME:
        raise RuntimeError(
            "COLLECT_CHAT topilmadi"
        )

    client = create_client()

    await client.start()

    try:

        entity = await client.get_entity(
            CHAT_USERNAME
        )

        print(
            f"✅ Chat topildi: "
            f"{getattr(entity, 'title', CHAT_USERNAME)}"
        )

        count = 0

        async for message in client.iter_messages(
            entity,
            limit=1000
        ):

            if not message:
                continue

            if not message.message:
                continue

            try:

                await client.get_messages(
                    entity,
                    ids=message.id
                )

                sender = await message.get_sender()
                chat = await message.get_chat()

                message.sender = sender
                message.chat = chat

                save_public_message(
                    message
                )

                count += 1

            except Exception as error:

                print(
                    f"⚠️ {message.id}: {error}"
                )

        print(
            f"✅ Yig‘ish tugadi. "
            f"{count} ta xabar qayta ishlandi."
        )

    finally:

        await client.disconnect()


if __name__ == "__main__":

    asyncio.run(
        collect_chat()
              )
