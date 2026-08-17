import os
from telebot import types

from database import get_connection
from vip import (
    get_pending_requests,
    approve_vip,
    reject_vip,
)

ADMIN_IDS = {
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
}


def is_admin(user_id):
    return user_id in ADMIN_IDS


def register_admin_handlers(bot):

    # ==============================
    # ADMIN MENU
    # ==============================

    def admin_keyboard():

        kb = types.ReplyKeyboardMarkup(
            resize_keyboard=True
        )

        kb.row(
            "📊 Statistika",
            "👥 Foydalanuvchilar"
        )

        kb.row(
            "💎 VIP arizalar",
            "👑 VIP boshqarish"
        )

        kb.row(
            "🔎 User qidirish",
            "📢 Kanal/Guruh"
        )

        kb.row(
            "💬 Xabar qidirish",
            "🔔 Yangi xabarlar"
        )

        kb.row(
            "📢 Hammaga xabar",
            "🎯 Tanlanganlarga xabar"
        )

        kb.row(
            "🚫 Ban / Unban",
            "⚙️ Sozlamalar"
        )

        kb.row("⬅️ Asosiy menyu")

        return kb

    # ==============================
    # /ADMIN
    # ==============================

    @bot.message_handler(commands=["admin"])
    def admin_command(message):

        if not is_admin(message.from_user.id):
            bot.send_message(
                message.chat.id,
                "❌ Siz admin emassiz."
            )
            return

        bot.send_message(
            message.chat.id,
            "🛠 <b>ADMIN PANEL</b>\n\n"
            "Kerakli bo‘limni tanlang 👇",
            reply_markup=admin_keyboard()
        )

    # ==============================
    # STATISTIKA
    # ==============================

    @bot.message_handler(
        func=lambda m: (
            m.text == "📊 Statistika"
            and is_admin(m.from_user.id)
        )
    )
    def statistics(message):

        conn = get_connection()

        try:
            with conn.cursor() as cur:

                cur.execute(
                    "SELECT COUNT(*) FROM users"
                )
                users = cur.fetchone()[0]

                cur.execute(
                    "SELECT COUNT(*) FROM chats"
                )
                chats = cur.fetchone()[0]

                cur.execute(
                    "SELECT COUNT(*) FROM messages"
                )
                messages = cur.fetchone()[0]

                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM vip_users
                    WHERE expires_at > CURRENT_TIMESTAMP
                    """
                )
                vip = cur.fetchone()[0]

                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM vip_requests
                    WHERE status = 'PENDING'
                    """
                )
                pending = cur.fetchone()[0]

            bot.send_message(
                message.chat.id,
                "📊 <b>STATISTIKA</b>\n\n"
                f"👥 Userlar: <b>{users}</b>\n"
                f"💎 Faol VIP: <b>{vip}</b>\n"
                f"📢 Chatlar: <b>{chats}</b>\n"
                f"💬 Xabarlar: <b>{messages}</b>\n"
                f"⏳ VIP arizalar: <b>{pending}</b>"
            )

        finally:
            conn.close()

    # ==============================
    # FOYDALANUVCHILAR
    # ==============================

    @bot.message_handler(
        func=lambda m: (
            m.text == "👥 Foydalanuvchilar"
            and is_admin(m.from_user.id)
        )
    )
    def users(message):

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
                    ORDER BY last_seen DESC
                    LIMIT 30
                    """
                )

                rows = cur.fetchall()

            if not rows:
                bot.send_message(
                    message.chat.id,
                    "❌ Userlar topilmadi."
                )
                return

            text = "👥 <b>USERLAR</b>\n\n"

            for row in rows:

                user_id = row[0]
                username = row[1]
                first_name = row[2] or ""
                last_name = row[3] or ""

                name = (
                    f"{first_name} {last_name}"
                ).strip()

                username_text = (
                    f"@{username}"
                    if username
                    else "username yo‘q"
                )

                text += (
                    f"👤 <b>{name or 'Nomaʼlum'}</b>\n"
                    f"🔗 {username_text}\n"
                    f"🆔 <code>{user_id}</code>\n"
                    "────────────\n"
                )

            bot.send_message(
                message.chat.id,
                text
            )

        finally:
            conn.close()

    # ==============================
    # VIP ARIZALAR
    # ==============================

    @bot.message_handler(
        func=lambda m: (
            m.text == "💎 VIP arizalar"
            and is_admin(m.from_user.id)
        )
    )
    def vip_requests(message):

        requests = get_pending_requests()

        if not requests:

            bot.send_message(
                message.chat.id,
                "✅ Kutilayotgan VIP ariza yo‘q."
            )
            return

        for request in requests:

            request_id = request[0]
            user_id = request[1]
            amount = request[2]
            days = request[3]
            created = request[4]

            text = (
                "💎 <b>VIP ARIZA</b>\n\n"
                f"🧾 № <code>{request_id}</code>\n"
                f"👤 ID: <code>{user_id}</code>\n"
                f"💰 {amount:,} so‘m\n"
                f"⏳ {days} kun\n"
                f"📅 {created}"
            )

            kb = types.InlineKeyboardMarkup()

            kb.row(
                types.InlineKeyboardButton(
                    "✅ TASDIQLASH",
                    callback_data=f"vip_approve:{request_id}"
                ),
                types.InlineKeyboardButton(
                    "❌ RAD ETISH",
                    callback_data=f"vip_reject:{request_id}"
                )
            )

            bot.send_message(
                message.chat.id,
                text,
                reply_markup=kb
            )

    # ==============================
    # VIP APPROVE
    # ==============================

    @bot.callback_query_handler(
        func=lambda c: (
            c.data.startswith("vip_approve:")
        )
    )
    def vip_approve_callback(call):

        if not is_admin(call.from_user.id):

            bot.answer_callback_query(
                call.id,
                "❌ Admin emassiz.",
                show_alert=True
            )
            return

        request_id = int(
            call.data.split(":")[1]
        )

        success, result = approve_vip(
            request_id,
            call.from_user.id
        )

        if not success:

            bot.answer_callback_query(
                call.id,
                "⚠️ Bu ariza allaqachon ishlatilgan.",
                show_alert=True
            )
            return

        user_id = result

        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )

        bot.edit_message_text(
            call.message.text +
            "\n\n✅ <b>TASDIQLANDI</b>",
            call.message.chat.id,
            call.message.message_id
        )

        try:

            bot.send_message(
                user_id,
                "🎉 <b>VIP tasdiqlandi!</b>\n\n"
                "💎 Muddat: <b>7 kun</b>\n"
                "🔎 User qidirish ochildi."
            )

        except Exception as e:
            print("VIP xabari:", e)

        bot.answer_callback_query(
            call.id,
            "✅ VIP ochildi!"
        )

    # ==============================
    # VIP REJECT
    # ==============================

    @bot.callback_query_handler(
        func=lambda c: (
            c.data.startswith("vip_reject:")
        )
    )
    def vip_reject_callback(call):

        if not is_admin(call.from_user.id):

            bot.answer_callback_query(
                call.id,
                "❌ Admin emassiz.",
                show_alert=True
            )
            return

        request_id = int(
            call.data.split(":")[1]
        )

        success, result = reject_vip(
            request_id,
            call.from_user.id
        )

        if not success:

            bot.answer_callback_query(
                call.id,
                "⚠️ Bu ariza allaqachon ishlatilgan.",
                show_alert=True
            )
            return

        user_id = result

        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )

        bot.edit_message_text(
            call.message.text +
            "\n\n❌ <b>RAD ETILDI</b>",
            call.message.chat.id,
            call.message.message_id
        )

        try:

            bot.send_message(
                user_id,
                "❌ <b>VIP arizangiz rad etildi.</b>"
            )

        except Exception as e:
            print("Reject xabari:", e)

        bot.answer_callback_query(
            call.id,
            "❌ Rad etildi."
        )

    # ==============================
    # KANAL / GURUH
    # ==============================

    @bot.message_handler(
        func=lambda m: (
            m.text == "📢 Kanal/Guruh"
            and is_admin(m.from_user.id)
        )
    )
    def channels(message):

        conn = get_connection()

        try:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        telegram_chat_id,
                        title,
                        username,
                        chat_type
                    FROM chats
                    ORDER BY last_seen DESC
                    LIMIT 50
                    """
                )

                rows = cur.fetchall()

            if not rows:

                bot.send_message(
                    message.chat.id,
                    "📢 Hozircha chatlar yo‘q."
                )
                return

            text = "📢 <b>KANAL / GURUHLAR</b>\n\n"

            for row in rows:

                username = (
                    f"@{row[2]}"
                    if row[2]
                    else ""
                )

                text += (
                    f"📢 <b>{row[1] or 'Nomaʼlum'}</b>\n"
                    f"🔗 {username}\n"
                    f"🆔 <code>{row[0]}</code>\n"
                    f"📌 {row[3]}\n"
                    "────────────\n"
                )

            bot.send_message(
                message.chat.id,
                text
            )

        finally:
            conn.close()

    # ==============================
    # SOZLAMALAR
    # ==============================

    @bot.message_handler(
        func=lambda m: (
            m.text == "⚙️ Sozlamalar"
            and is_admin(m.from_user.id)
        )
    )
    def settings(message):

        bot.send_message(
            message.chat.id,
            "⚙️ <b>SOZLAMALAR</b>\n\n"
            "💎 VIP: 30 000 so‘m / 7 kun\n"
            "🔎 User qidirish: VIP\n"
            "🛠 Admin panel: faqat adminlar"
        )

    print("🛠 Admin handlerlar ulandi.")
