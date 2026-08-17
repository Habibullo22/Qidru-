import os
import telebot
from telebot import types

from database import get_connection
from vip import (
    get_pending_requests,
    approve_vip,
    reject_vip,
)


# =========================================================
#                    SETTINGS
# =========================================================

BOT_TOKEN = os.getenv("8611335484:AAHoH8mg1OO9V7PDB3wUlZ6wU3HxsQx7avY")

ADMIN_IDS = {
    int(x.strip())
    for x in os.getenv("5815294733", "").split(",")
    if x.strip().isdigit()
}

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)


# =========================================================
#                    SECURITY
# =========================================================

def is_admin(user_id):
    return user_id in ADMIN_IDS


def admin_only(message):
    return is_admin(message.from_user.id)


# =========================================================
#                    ADMIN KEYBOARD
# =========================================================

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

    kb.row(
        "⬅️ Asosiy menyu"
    )

    return kb


# =========================================================
#                    ADMIN COMMAND
# =========================================================

@bot.message_handler(commands=["admin"])
def admin_command(message):

    if not admin_only(message):

        bot.send_message(
            message.chat.id,
            "❌ Sizda admin panelga kirish huquqi yo‘q."
        )

        return

    bot.send_message(
        message.chat.id,
        "🛠 <b>ADMIN PANEL</b>\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=admin_keyboard()
    )


# =========================================================
#                    STATISTICS
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "📊 Statistika"
)
def statistics(message):

    if not admin_only(message):
        return

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
            "📊 <b>BOT STATISTIKASI</b>\n\n"
            f"👥 Foydalanuvchilar: <b>{users}</b>\n"
            f"💎 Faol VIP: <b>{vip}</b>\n"
            f"📢 Chatlar: <b>{chats}</b>\n"
            f"💬 Xabarlar: <b>{messages}</b>\n"
            f"⏳ VIP arizalar: <b>{pending}</b>"
        )

    finally:
        conn.close()


# =========================================================
#                    USERS
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "👥 Foydalanuvchilar"
)
def users_list(message):

    if not admin_only(message):
        return

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
                    last_seen
                FROM users
                ORDER BY last_seen DESC
                LIMIT 30
                """
            )

            rows = cur.fetchall()

        if not rows:

            bot.send_message(
                message.chat.id,
                "👥 Foydalanuvchilar topilmadi."
            )

            return

        text = "👥 <b>SO‘NGGI FOYDALANUVCHILAR</b>\n\n"

        for row in rows:

            user_id = row[0]
            username = row[1]
            first_name = row[2]
            last_name = row[3]

            name = " ".join(
                x for x in [
                    first_name,
                    last_name
                ]
                if x
            )

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


# =========================================================
#                    VIP REQUESTS
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "💎 VIP arizalar"
)
def vip_requests(message):

    if not admin_only(message):
        return

    requests = get_pending_requests()

    if not requests:

        bot.send_message(
            message.chat.id,
            "✅ Hozircha kutilayotgan VIP arizalar yo‘q."
        )

        return

    bot.send_message(
        message.chat.id,
        f"💎 <b>{len(requests)} ta VIP ariza</b>"
    )

    for request in requests:

        request_id = request[0]
        user_id = request[1]
        amount = request[2]
        days = request[3]
        created_at = request[4]

        text = (
            "💎 <b>VIP ARIZA</b>\n\n"
            f"🧾 Ariza: <code>#{request_id}</code>\n"
            f"🆔 User ID: <code>{user_id}</code>\n"
            f"💰 Summa: <b>{amount:,} so‘m</b>\n"
            f"⏳ Muddat: <b>{days} kun</b>\n"
            f"📅 Sana: {created_at}"
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


# =========================================================
#                 VIP APPROVE
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith(
        "vip_approve:"
    )
)
def vip_approve_callback(call):

    if not is_admin(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "❌ Siz admin emassiz.",
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
            "💎 VIP: <b>7 kun</b>\n"
            "🔎 User qidirish funksiyasi ochildi."
        )

    except Exception as error:

        print(
            "Userga VIP xabari yuborilmadi:",
            error
        )

    bot.answer_callback_query(
        call.id,
        "✅ VIP tasdiqlandi!"
    )


# =========================================================
#                  VIP REJECT
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith(
        "vip_reject:"
    )
)
def vip_reject_callback(call):

    if not is_admin(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "❌ Siz admin emassiz.",
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
            "❌ <b>VIP arizangiz rad etildi.</b>\n\n"
            "Agar xatolik bo‘lsa, admin bilan bog‘laning."
        )

    except Exception as error:

        print(
            "Userga rad javobi yuborilmadi:",
            error
        )

    bot.answer_callback_query(
        call.id,
        "❌ Ariza rad etildi."
    )


# =========================================================
#                  VIP MANAGEMENT
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "👑 VIP boshqarish"
)
def vip_management(message):

    if not admin_only(message):
        return

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "💎 Faol VIP lar",
            callback_data="admin_active_vips"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "🔎 VIP tekshirish",
            callback_data="admin_check_vip"
        )
    )

    bot.send_message(
        message.chat.id,
        "👑 <b>VIP BOSHQARUV</b>",
        reply_markup=kb
    )


# =========================================================
#                  ACTIVE VIP LIST
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
    call.data == "admin_active_vips"
)
def active_vips(call):

    if not is_admin(call.from_user.id):
        return

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    user_id,
                    started_at,
                    expires_at
                FROM vip_users
                WHERE expires_at > CURRENT_TIMESTAMP
                ORDER BY expires_at ASC
                LIMIT 50
                """
            )

            rows = cur.fetchall()

        if not rows:

            bot.send_message(
                call.message.chat.id,
                "💎 Faol VIP foydalanuvchilar yo‘q."
            )

            return

        text = "💎 <b>FAOL VIP LAR</b>\n\n"

        for row in rows:

            text += (
                f"🆔 <code>{row[0]}</code>\n"
                f"📅 Boshlangan: {row[1]}\n"
                f"⏳ Tugaydi: {row[2]}\n"
                "────────────\n"
            )

        bot.send_message(
            call.message.chat.id,
            text
        )

    finally:
        conn.close()

    bot.answer_callback_query(call.id)


# =========================================================
#                    CHANNEL / GROUP
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "📢 Kanal/Guruh"
)
def channel_group(message):

    if not admin_only(message):
        return

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
                "📢 Bazada chatlar yo‘q."
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


# =========================================================
#                   MESSAGE SEARCH
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "💬 Xabar qidirish"
)
def message_search(message):

    if not admin_only(message):
        return

    msg = bot.send_message(
        message.chat.id,
        "💬 Qidiriladigan so‘zni yuboring:"
    )

    bot.register_next_step_handler(
        msg,
        process_message_search
    )


def process_message_search(message):

    if not admin_only(message):
        return

    query = message.text.strip()

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    username,
                    text,
                    author_id,
                    message_date
                FROM messages
                WHERE text ILIKE %s
                ORDER BY message_date DESC
                LIMIT 30
                """,
                (f"%{query}%",)
            )

            rows = cur.fetchall()

        if not rows:

            bot.send_message(
                message.chat.id,
                "❌ Xabar topilmadi."
            )

            return

        text = "💬 <b>XABAR QIDIRUV</b>\n\n"

        for row in rows:

            username = (
                f"@{row[0]}"
                if row[0]
                else "Nomaʼlum"
            )

            msg_text = row[1] or ""

            if len(msg_text) > 300:
                msg_text = (
                    msg_text[:300] +
                    "..."
                )

            text += (
                f"👤 {username}\n"
                f"🆔 <code>{row[2]}</code>\n"
                f"💬 {msg_text}\n"
                f"📅 {row[3]}\n"
                "────────────\n"
            )

        bot.send_message(
            message.chat.id,
            text
        )

    finally:
        conn.close()


# =========================================================
#                    BAN / UNBAN
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "🚫 Ban / Unban"
)
def ban_menu(message):

    if not admin_only(message):
        return

    kb = types.InlineKeyboardMarkup()

    kb.row(
        types.InlineKeyboardButton(
            "🚫 BAN",
            callback_data="admin_ban"
        ),
        types.InlineKeyboardButton(
            "✅ UNBAN",
            callback_data="admin_unban"
        )
    )

    bot.send_message(
        message.chat.id,
        "🚫 <b>FOYDALANUVCHI BOSHQARUVI</b>",
        reply_markup=kb
    )


# =========================================================
#                  BROADCAST
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "📢 Hammaga xabar"
)
def broadcast_start(message):

    if not admin_only(message):
        return

    msg = bot.send_message(
        message.chat.id,
        "📢 Hammaga yuboriladigan xabarni yozing:"
    )

    bot.register_next_step_handler(
        msg,
        broadcast_send
    )


def broadcast_send(message):

    if not admin_only(message):
        return

    text = message.text

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                "SELECT telegram_id FROM users"
            )

            users = cur.fetchall()

    finally:
        conn.close()

    sent = 0
    failed = 0

    for row in users:

        user_id = row[0]

        try:

            bot.send_message(
                user_id,
                text
            )

            sent += 1

        except Exception:
            failed += 1

    bot.send_message(
        message.chat.id,
        "📢 <b>YUBORISH YAKUNLANDI</b>\n\n"
        f"✅ Yuborildi: {sent}\n"
        f"❌ Yuborilmadi: {failed}"
    )


# =========================================================
#              SELECTED USERS BROADCAST
# =========================================================

@bot.message_handler(
    func=lambda m:
    m.text == "🎯 Tanlanganlarga xabar"
)
def selected_broadcast(message):

    if not admin_only(message):
        return

    msg = bot.send_message(
        message.chat.id,
        "🎯 User IDlarni vergul bilan yuboring.\n\n"
        "Masalan:\n"
        "<code>123456,987654,555555</code>"
    )

    bot.register_next_step_handler(
        msg,
        selected_users_step
    )


def selected_users_step(message):

    if not admin_only(message):
        return

    ids = []

    for value in message.text.split(","):

        value = value.strip()

        if value.isdigit():
            ids.append(int(value))

    if not ids:

        bot.send_message(
            message.chat.id,
            "❌ ID topilmadi."
        )

        return

    msg = bot.send_message(
        message.chat.id,
        "📨 Endi yuboriladigan xabarni yozing:"
    )

    bot.register_next_step_handler(
        msg,
        lambda m: send_selected(
            m,
            ids
        )
    )


def send_selected(message, ids):

    if not admin_only(message):
        return

    sent = 0
    failed = 0

    for user_id in ids:

        try:

            bot.send_message(
                user_id,
                message.text
            )

            sent += 1

        except Exception:
            failed += 1

    bot.send_message(
        message.chat.id,
        "🎯 <b>YAKUNLANDI</b>\n\n"
        f"✅ Yuborildi: {sent}\n"
        f"❌ Xatolik: {failed}"
    )


# =========================================================
#                  NEW MESSAGES
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "🔔 Yangi xabarlar"
)
def new_messages(message):

    if not admin_only(message):
        return

    bot.send_message(
        message.chat.id,
        "🔔 <b>Yangi xabarlar</b>\n\n"
        "Bu bo‘lim collector orqali bazaga "
        "yangi public xabarlar tushganda "
        "keyingi bosqichda avtomatik ko‘rsatadi."
    )


# =========================================================
#                     SETTINGS
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "⚙️ Sozlamalar"
)
def settings(message):

    if not admin_only(message):
        return

    bot.send_message(
        message.chat.id,
        "⚙️ <b>BOT SOZLAMALARI</b>\n\n"
        "💎 VIP: 30 000 so‘m / 7 kun\n"
        "🔎 User qidirish: VIP\n"
        "🛠 Admin panel: faqat adminlar"
    )


# =========================================================
#                 MAIN MENU BUTTON
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "⬅️ Asosiy menyu"
)
def back_main(message):

    if not admin_only(message):
        return

    bot.send_message(
        message.chat.id,
        "⬅️ Asosiy menyuga qaytish funksiyasi "
        "main.py tomonidan boshqariladi."
    )


print("🛠 Admin modul tayyor.")
