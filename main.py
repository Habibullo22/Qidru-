import os
import logging
import telebot
from telebot import types

# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv("8611335484:AAHoH8mg1OO9V7PDB3wUlZ6wU3HxsQx7avY", "")
ADMIN_ID = int(os.getenv("5815294733", "0"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# =========================================================
# PROJECT MODULES
# =========================================================

import database
import vip
import search
import collector
import telegram_client

try:
    import admin
except Exception as e:
    admin = None
    logging.warning(f"admin.py yuklanmadi: {e}")

try:
    import collector_runner
except Exception as e:
    collector_runner = None
    logging.warning(f"collector_runner.py yuklanmadi: {e}")


# =========================================================
# USER MENU
# =========================================================

def user_menu():

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.row(
        "🔎 User qidirish",
        "📢 Kanal/Guruh"
    )

    kb.row(
        "💬 Xabar qidirish",
        "👤 Profil"
    )

    kb.row(
        "💎 VIP",
        "🔔 Yangi xabarlar"
    )

    return kb


# =========================================================
# ADMIN MENU
# =========================================================

def admin_menu():

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.row(
        "📊 Statistika",
        "👥 Foydalanuvchilar"
    )

    kb.row(
        "🔎 User qidirish",
        "📢 Kanal/Guruh"
    )

    kb.row(
        "💬 Xabar qidirish",
        "💎 VIP arizalar"
    )

    kb.row(
        "👑 VIP boshqarish",
        "📢 Hammaga xabar"
    )

    kb.row(
        "🎯 Tanlanganlarga xabar",
        "🔔 Yangi xabarlar"
    )

    kb.row(
        "📋 Xabarlar tarixi",
        "🚫 Ban / Unban"
    )

    kb.row(
        "⚙️ Sozlamalar",
        "⬅️ User menyusi"
    )

    return kb


# =========================================================
# CHECK ADMIN
# =========================================================

def is_admin(user_id):

    return (
        ADMIN_ID != 0
        and user_id == ADMIN_ID
    )


# =========================================================
# START
# =========================================================

@bot.message_handler(commands=["start"])
def start(message):

    user = message.from_user

    try:

        if hasattr(database, "add_user"):
            database.add_user(
                user.id,
                user.username,
                user.first_name,
                user.last_name
            )

        elif hasattr(database, "register_user"):
            database.register_user(
                user.id,
                user.username,
                user.first_name,
                user.last_name
            )

    except Exception as e:

        logging.warning(
            f"User database error: {e}"
        )

    if is_admin(user.id):

        bot.send_message(
            message.chat.id,

            "👑 <b>ADMIN PANEL</b>\n\n"
            "Xush kelibsiz, administrator.",

            reply_markup=admin_menu()
        )

    else:

        bot.send_message(
            message.chat.id,

            f"👋 <b>Salom, {user.first_name}!</b>\n\n"
            "Telegram qidiruv botiga xush kelibsiz.\n\n"
            "Kerakli bo‘limni tanlang:",

            reply_markup=user_menu()
        )


# =========================================================
# PROFILE
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "👤 Profil"
)
def profile(message):

    user = message.from_user

    username = (
        f"@{user.username}"
        if user.username
        else "Username yo‘q"
    )

    text = (
        "👤 <b>PROFIL</b>\n\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"👤 Username: {username}\n"
        f"📛 Ism: {user.first_name or '-'}\n"
    )

    # VIP holati
    try:

        if hasattr(vip, "is_vip"):

            status = vip.is_vip(user.id)

            if status:
                text += "\n💎 <b>VIP: FAOL</b>"

            else:
                text += "\n🔒 <b>VIP: FAOL EMAS</b>"

    except Exception:

        pass

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=user_menu()
    )


# =========================================================
# VIP MENU
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "💎 VIP"
)
def vip_menu(message):

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "💎 VIP olish",
            callback_data="vip_buy"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "ℹ️ VIP haqida",
            callback_data="vip_info"
        )
    )

    bot.send_message(
        message.chat.id,

        "💎 <b>VIP TIZIMI</b>\n\n"
        "VIP orqali qo‘shimcha qidiruv imkoniyatlaridan "
        "foydalanishingiz mumkin.\n\n"
        "👇 Kerakli bo‘limni tanlang:",

        reply_markup=kb
    )


# =========================================================
# VIP INFO
# =========================================================

@bot.callback_query_handler(
    func=lambda c: c.data == "vip_info"
)
def vip_info(call):

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,

        "💎 <b>VIP imkoniyatlari</b>\n\n"
        "🔎 Kengaytirilgan user qidiruvi\n"
        "📢 Kanal/guruh qidiruvi\n"
        "💬 Xabar qidiruvi\n"
        "🔔 Yangi xabarlar\n"
        "⚡ VIP funksiyalardan foydalanish\n\n"
        "VIP olish uchun «💎 VIP olish» tugmasini bosing."
    )


# =========================================================
# VIP BUY
# =========================================================

@bot.callback_query_handler(
    func=lambda c: c.data == "vip_buy"
)
def vip_buy(call):

    bot.answer_callback_query(call.id)

    # vip.py ichidagi funksiyalardan foydalanishga harakat qiladi

    try:

        if hasattr(vip, "show_plans"):

            result = vip.show_plans(
                bot,
                call.message.chat.id
            )

            if result:
                return

        if hasattr(vip, "vip_plans"):

            plans = vip.vip_plans()

            kb = types.InlineKeyboardMarkup()

            for plan in plans:

                kb.add(
                    types.InlineKeyboardButton(
                        str(plan["name"]),
                        callback_data=f"vip_plan:{plan['id']}"
                    )
                )

            bot.send_message(
                call.message.chat.id,
                "💎 <b>VIP tarifni tanlang:</b>",
                reply_markup=kb
            )

            return

    except Exception as e:

        logging.error(
            f"VIP plan error: {e}"
        )

    # Agar vip.py hali plan funksiyasiga ega bo‘lmasa

    kb = types.InlineKeyboardMarkup()

    kb.row(
        types.InlineKeyboardButton(
            "💎 7 kun",
            callback_data="vip_plan:7"
        ),
        types.InlineKeyboardButton(
            "💎 30 kun",
            callback_data="vip_plan:30"
        )
    )

    kb.row(
        types.InlineKeyboardButton(
            "💎 90 kun",
            callback_data="vip_plan:90"
        )
    )

    bot.send_message(
        call.message.chat.id,

        "💎 <b>VIP tariflar</b>\n\n"
        "Kerakli muddatni tanlang:",

        reply_markup=kb
    )


# =========================================================
# VIP PLAN
# =========================================================

@bot.callback_query_handler(
    func=lambda c: c.data.startswith("vip_plan:")
)
def vip_plan(call):

    bot.answer_callback_query(call.id)

    days = call.data.split(":")[1]

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "💳 To‘lov qilish",
            callback_data=f"vip_payment:{days}"
        )
    )

    bot.send_message(
        call.message.chat.id,

        f"💎 <b>{days} kunlik VIP</b>\n\n"
        "To‘lovni amalga oshirgandan keyin "
        "chekni botga yuborasiz.\n\n"
        "📸 Chek yuborish orqali arizangiz admin "
        "tomonidan tekshiriladi.",

        reply_markup=kb
    )


# =========================================================
# VIP PAYMENT
# =========================================================

@bot.callback_query_handler(
    func=lambda c: c.data.startswith("vip_payment:")
)
def vip_payment(call):

    bot.answer_callback_query(call.id)

    days = call.data.split(":")[1]

    text = (
        "💳 <b>VIP TO‘LOV</b>\n\n"
        f"💎 Tarif: <b>{days} kun</b>\n\n"
        "To‘lov rekvizitlari:\n"
        "💳 Humo / Uzcard\n"
        "📱 Admin bergan karta raqamiga to‘lov qiling.\n\n"
        "✅ To‘lovdan keyin <b>chek rasmini</b> yuboring."
    )

    bot.send_message(
        call.message.chat.id,
        text,
        reply_markup=user_menu()
    )

    msg = bot.send_message(
        call.message.chat.id,
        "📸 Endi to‘lov chekini rasm ko‘rinishida yuboring:"
    )

    bot.register_next_step_handler(
        msg,
        lambda m: receive_vip_receipt(
            m,
            days
        )
    )


# =========================================================
# VIP RECEIPT
# =========================================================

def receive_vip_receipt(
    message,
    days
):

    if not message.photo:

        bot.send_message(
            message.chat.id,
            "❌ Iltimos, chekni <b>rasm</b> qilib yuboring."
        )

        return

    file_id = message.photo[-1].file_id

    # Admin'ga yuborish

    if ADMIN_ID:

        kb = types.InlineKeyboardMarkup()

        kb.row(

            types.InlineKeyboardButton(
                "✅ Tasdiqlash",
                callback_data=(
                    f"vip_approve:"
                    f"{message.from_user.id}:"
                    f"{days}"
                )
            ),

            types.InlineKeyboardButton(
                "❌ Rad etish",
                callback_data=(
                    f"vip_reject:"
                    f"{message.from_user.id}"
                )
            )

        )

        bot.send_photo(

            ADMIN_ID,
            file_id,

            caption=(
                "💎 <b>YANGI VIP ARIZA</b>\n\n"
                f"👤 User ID: "
                f"<code>{message.from_user.id}</code>\n"
                f"👤 Username: "
                f"@{message.from_user.username or 'yo‘q'}\n"
                f"💎 Muddat: <b>{days} kun</b>"
            ),

            reply_markup=kb
        )

    bot.send_message(
        message.chat.id,

        "✅ <b>Chek qabul qilindi.</b>\n\n"
        "🛠 Admin tekshiradi.\n"
        "Tasdiqlangandan keyin VIP avtomatik faollashadi.",

        reply_markup=user_menu()
    )


# =========================================================
# VIP APPROVE
# =========================================================

@bot.callback_query_handler(
    func=lambda c: c.data.startswith("vip_approve:")
)
def vip_approve(call):

    if not is_admin(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "⛔ Ruxsat yo‘q!",
            show_alert=True
        )

        return

    data = call.data.split(":")

    user_id = int(data[1])
    days = int(data[2])

    success = False

    try:

        if hasattr(vip, "activate_vip"):

            vip.activate_vip(
                user_id,
                days
            )

            success = True

        elif hasattr(database, "activate_vip"):

            database.activate_vip(
                user_id,
                days
            )

            success = True

    except Exception as e:

        logging.error(
            f"VIP activation error: {e}"
        )

    if success:

        bot.send_message(
            user_id,

            "🎉 <b>VIP TASDIQLANDI!</b>\n\n"
            f"💎 VIP muddati: <b>{days} kun</b>\n\n"
            "Endi VIP funksiyalaridan foydalanishingiz mumkin."
        )

        bot.answer_callback_query(
            call.id,
            "✅ VIP berildi!"
        )

        bot.edit_message_caption(
            "✅ <b>TASDIQLANDI</b>\n\n"
            f"👤 User: <code>{user_id}</code>\n"
            f"💎 VIP: {days} kun",

            call.message.chat.id,
            call.message.message_id
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ VIP funksiyasi database/vip.py bilan ulanmagan.",
            show_alert=True
        )


# =========================================================
# VIP REJECT
# =========================================================

@bot.callback_query_handler(
    func=lambda c: c.data.startswith("vip_reject:")
)
def vip_reject(call):

    if not is_admin(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "⛔ Ruxsat yo‘q!",
            show_alert=True
        )

        return

    user_id = int(
        call.data.split(":")[1]
    )

    bot.send_message(
        user_id,

        "❌ <b>VIP arizangiz rad etildi.</b>\n\n"
        "Agar to‘lovda muammo bo‘lgan bo‘lsa, "
        "admin bilan bog‘laning."
    )

    bot.answer_callback_query(
        call.id,
        "❌ Ariza rad etildi."
    )


# =========================================================
# USER SEARCH
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "🔎 User qidirish"
)
def user_search(message):

    # VIP tekshirish

    try:

        if hasattr(vip, "is_vip"):

            if not vip.is_vip(
                message.from_user.id
            ):

                bot.send_message(

                    message.chat.id,

                    "🔒 <b>VIP kerak</b>\n\n"
                    "User qidirish funksiyasidan "
                    "foydalanish uchun VIP oling.\n\n"
                    "💎 VIP → 💎 VIP olish",

                    reply_markup=user_menu()
                )

                return

    except Exception as e:

        logging.warning(
            f"VIP check: {e}"
        )

    msg = bot.send_message(
        message.chat.id,

        "🔎 <b>User qidirish</b>\n\n"
        "Username yoki ID yuboring:"
    )

    bot.register_next_step_handler(
        msg,
        process_user_search
    )


def process_user_search(message):

    query = message.text.strip()

    result = None

    try:

        if hasattr(search, "search_user"):

            result = search.search_user(
                query
            )

        elif hasattr(search, "find_user"):

            result = search.find_user(
                query
            )

    except Exception as e:

        logging.error(
            f"Search error: {e}"
        )

    if result:

        bot.send_message(
            message.chat.id,
            str(result),
            reply_markup=user_menu()
        )

    else:

        bot.send_message(

            message.chat.id,

            "❌ User topilmadi.",

            reply_markup=user_menu()
        )


# =========================================================
# CHANNEL / GROUP
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "📢 Kanal/Guruh"
)
def channel_group(message):

    msg = bot.send_message(
        message.chat.id,

        "📢 <b>Kanal/Guruh</b>\n\n"
        "Username yoki link yuboring:"
    )

    bot.register_next_step_handler(
        msg,
        process_channel
    )


def process_channel(message):

    query = message.text.strip()

    result = None

    try:

        for name in [
            "search_channel",
            "search_group",
            "search_chat"
        ]:

            if hasattr(search, name):

                result = getattr(
                    search,
                    name
                )(query)

                break

    except Exception as e:

        logging.error(
            f"Channel search error: {e}"
        )

    bot.send_message(

        message.chat.id,

        str(result)
        if result
        else "❌ Kanal/Guruh topilmadi.",

        reply_markup=user_menu()
    )


# =========================================================
# MESSAGE SEARCH
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "💬 Xabar qidirish"
)
def message_search(message):

    msg = bot.send_message(
        message.chat.id,

        "💬 <b>Xabar qidirish</b>\n\n"
        "Qidiriladigan so‘zni yuboring:"
    )

    bot.register_next_step_handler(
        msg,
        process_message_search
    )


def process_message_search(message):

    query = message.text.strip()

    result = None

    try:

        for name in [
            "search_messages",
            "search_message",
            "find_messages"
        ]:

            if hasattr(search, name):

                result = getattr(
                    search,
                    name
                )(query)

                break

    except Exception as e:

        logging.error(
            f"Message search error: {e}"
        )

    bot.send_message(

        message.chat.id,

        str(result)
        if result
        else "❌ Xabar topilmadi.",

        reply_markup=user_menu()
    )


# =========================================================
# NEW MESSAGES
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "🔔 Yangi xabarlar"
)
def new_messages(message):

    bot.send_message(

        message.chat.id,

        "🔔 <b>Yangi xabarlar</b>\n\n"
        "Collector orqali kelgan yangi xabarlar "
        "shu yerda ko‘rsatiladi.",

        reply_markup=user_menu()
    )


# =========================================================
# ADMIN COMMAND
# =========================================================

@bot.message_handler(
    commands=["admin"]
)
def admin_command(message):

    if not is_admin(
        message.from_user.id
    ):

        bot.send_message(
            message.chat.id,
            "⛔ Siz admin emassiz."
        )

        return

    bot.send_message(

        message.chat.id,

        "🛠 <b>ADMIN PANEL</b>",

        reply_markup=admin_menu()
    )


# =========================================================
# ADMIN PANEL
# =========================================================

@bot.message_handler(
    func=lambda m: (
        is_admin(m.from_user.id)
        and m.text in [
            "📊 Statistika",
            "👥 Foydalanuvchilar",
            "🔎 User qidirish",
            "📢 Kanal/Guruh",
            "💬 Xabar qidirish",
            "💎 VIP arizalar",
            "👑 VIP boshqarish",
            "📢 Hammaga xabar",
            "🎯 Tanlanganlarga xabar",
            "🔔 Yangi xabarlar",
            "📋 Xabarlar tarixi",
            "🚫 Ban / Unban",
            "⚙️ Sozlamalar",
            "⬅️ User menyusi"
        ]
    )
)
def admin_panel(message):

    text = message.text

    if text == "⬅️ User menyusi":

        bot.send_message(
            message.chat.id,
            "👤 User menyusi:",
            reply_markup=user_menu()
        )

        return

    if admin is not None:

        # admin.py dagi handler mavjud bo‘lsa,
        # undan foydalanamiz.

        possible_names = {
            "📊 Statistika": [
                "statistics",
                "stats",
                "show_statistics"
            ],

            "👥 Foydalanuvchilar": [
                "users",
                "get_users",
                "show_users"
            ],

            "💎 VIP arizalar": [
                "vip_applications",
                "get_vip_applications"
            ],

            "👑 VIP boshqarish": [
                "vip_management",
                "manage_vip"
            ],

            "📋 Xabarlar tarixi": [
                "message_history",
                "get_message_history"
            ],

            "🚫 Ban / Unban": [
                "ban_menu",
                "ban_unban"
            ],

            "⚙️ Sozlamalar": [
                "settings",
                "admin_settings"
            ]
        }

        for function_name in possible_names.get(
            text,
            []
        ):

            function = getattr(
                admin,
                function_name,
                None
            )

            if callable(function):

                try:

                    result = function(
                        message.from_user.id
                    )

                    if result:

                        bot.send_message(
                            message.chat.id,
                            str(result)
                        )

                    return

                except TypeError:

                    try:

                        result = function()

                        if result:

                            bot.send_message(
                                message.chat.id,
                                str(result)
                            )

                        return

                    except Exception:
                        pass

                except Exception as e:

                    logging.error(
                        f"Admin error: {e}"
                    )

    # fallback

    bot.send_message(

        message.chat.id,

        f"🛠 <b>{text}</b>\n\n"
        "Bu bo‘lim admin.py bilan ulanadi.",

        reply_markup=admin_menu()
    )


# =========================================================
# UNKNOWN
# =========================================================

@bot.message_handler(
    func=lambda m: True
)
def unknown(message):

    if is_admin(
        message.from_user.id
    ):

        bot.send_message(
            message.chat.id,
            "🛠 Admin menyudan foydalaning.",
            reply_markup=admin_menu()
        )

    else:

        bot.send_message(
            message.chat.id,
            "👇 Menyudan tanlang.",
            reply_markup=user_menu()
        )


# =========================================================
# RUN
# =========================================================

def main():

    logging.info(
        "🤖 Telegram bot ishga tushmoqda..."
    )

    logging.info(
        f"👑 ADMIN_ID: {ADMIN_ID}"
    )

    try:

        bot.remove_webhook()

    except Exception:
        pass

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )


if __name__ == "__main__":

    main()
