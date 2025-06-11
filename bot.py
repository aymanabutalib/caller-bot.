from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

TOKEN = "7594533191:AAHXQmfjOudDiUGz5RyZJTQJb9xn1jj1mXs"

user_language = {}
user_state = {}

languages = {
    "en": "🇺🇸 English",
    "ar": "🇸🇦 العربية",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
    "de": "🇩🇪 Deutsch",
    "ru": "🇷🇺 Русский"
}

main_buttons = [
    ["☎️ هوية المتصل", "✉️ هوية المرسل"],
    ["🟢 إجراء مكالمة", "💬 رسالة SMS"],
    ["📧 إرسال Email", "🔊 تغيير الصوت"],
    ["💎 بريميوم", "💰 تجديد الرصيد"],
    ["🌐 eSIM", "💸 يكسب"],
    ["📩 التواصل بفريق الدعم"],
    ["🔒 حماية من الانتحال", "✉️ تجربة الأرقام/الإيميل"]
]

menu_buttons = [
    ["☰ القائمة الرئيسية"],
    ["💰 شحن الرصيد", "🟢 مكالمة"],
    ["📧 Email", "💬 رسالة"],
    ["☎️ تغيير المتصل", "✉️ تغيير المرسل"],
    ["🔊 تغيير الصوت", "📱 رقم افتراضي"],
    ["💎 بريميوم", "🌐 شراء eSIM"],
    ["📩 فريق الدعم"]
]

def set_user_state(user_id, state):
    user_state[user_id] = state

def get_user_state(user_id):
    return user_state.get(user_id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    codes = list(languages.keys())
    keyboard = []
    for i in range(0, len(codes), 2):
        row = []
        for j in range(i, min(i + 2, len(codes))):
            code = codes[j]
            name = languages[code]
            row.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🗰️ يرجى اختيار لغتك / Please choose your language:",
        reply_markup=reply_markup
    )

async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = query.data.split("_")[1]
    user_language[query.from_user.id] = lang_code

    welcome_msg = {
        "ar": "مرحباً بك في بوت CallerConnectBot! 👋 سيتم عرض القائمة الآن.",
        "en": "Welcome to CallerConnectBot! 👋 Menu will appear now."
    }.get(lang_code, "Welcome!")

    keyboard = []
    for row in main_buttons:
        if len(row) == 2:
            text1, text2 = row
            keyboard.append([
                InlineKeyboardButton(text1, callback_data=f"btn_{text1}"),
                InlineKeyboardButton(text2, callback_data=f"btn_{text2}")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(row[0], callback_data=f"btn_{row[0]}")
            ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=query.message.chat.id, text=welcome_msg, reply_markup=reply_markup)

    reply_kb = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
    await context.bot.send_message(chat_id=query.message.chat.id, text="👇 استخدم القائمة:", reply_markup=reply_kb)

async def handle_main_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    await update.message.reply_text(f"🔘 تم الضغط على: {msg}\n(الرد الحقيقي سيتم تطويره لاحقاً)")

async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "btn_💰 تجديد الرصيد":
        set_user_state(query.from_user.id, "main_menu")
        amounts = [50, 100, 250, 500, 1000]
        rows = []
        for i in range(0, len(amounts), 2):
            row = []
            for j in range(i, min(i + 2, len(amounts))):
                amt = amounts[j]
                row.append(InlineKeyboardButton(f"${amt}", callback_data=f"recharge_{amt}"))
            rows.append(row)
        rows.append([InlineKeyboardButton("🔙 خلف", callback_data="back")])
        markup = InlineKeyboardMarkup(rows)
        await query.edit_message_text("💰 التجديد\n\nاكتب أو حدد المبلغ الذي ترغب في تجديد الرصيد.\n\nالحد الأدنى للمبلغ: $50", reply_markup=markup)

    elif data.startswith("recharge_"):
        amount = int(data.split("_")[1])
        set_user_state(query.from_user.id, "btn_💰 تجديد الرصيد")
        crypto_buttons = [
            [InlineKeyboardButton("₿ BTC", callback_data=f"pay_BTC_{amount}"),
             InlineKeyboardButton("Ξ ETH", callback_data=f"pay_ETH_{amount}")],
            [InlineKeyboardButton("USDT (TRC20)", callback_data=f"pay_USDT_{amount}"),
             InlineKeyboardButton("SOL", callback_data=f"pay_SOL_{amount}")],
            [InlineKeyboardButton("LTC", callback_data=f"pay_LTC_{amount}"),
             InlineKeyboardButton("DOGE", callback_data=f"pay_DOGE_{amount}")],
            [InlineKeyboardButton("🔙 خلف", callback_data="back")]
        ]
        await query.edit_message_text(
            f"💳 اختر طريقة الدفع للمبلغ ${amount}:", reply_markup=InlineKeyboardMarkup(crypto_buttons)
        )

    elif data.startswith("pay_"):
        _, coin, amount = data.split("_")
        amount = int(amount)
        set_user_state(query.from_user.id, f"recharge_{amount}")

        wallets = {
            "BTC": "bc1q4a2rn0sk6as7348ryfsxvrcqt3gy453xmhr5s2",
            "ETH": "0x2a3489047b085d04a1fa5d4da9825173ad82eb1b",
            "USDT": "TYQNqkFQsqFhiGesS93xxaecDj9CBsJ75s",
            "SOL": "0x2a3489047b085d04a1fa5d4da9825173ad82eb1b",
            "LTC": "TYQNqkFQsqFhiGesS93xxaecDj9CBsJ75s",
            "DOGE": "TYQNqkFQsqFhiGesS93xxaecDj9CBsJ75s"
        }

        fake_rates = {
            "BTC": 108295.43,
            "ETH": 3800.12,
            "USDT": 1.0,
            "SOL": 160.0,
            "LTC": 85.0,
            "DOGE": 0.14
        }

        price = fake_rates.get(coin, 1)
        wallet = wallets.get(coin, "لا يوجد عنوان متاح")
        coin_amount = round(amount / price, 8)

        text = f"""💰 التجديد

طريقة الدفع: {coin}
شبكة الاتصال: {'TRC20' if coin == 'USDT' else f"{coin} network"}
المبلغ: ${amount}

📤 أرسل إلى العنوان أدناه:
`{wallet}`

💵 المبلغ: `{coin_amount} {coin}` (بسعر الصرف ${price})

⏰ العنوان صالح لمدة 1 ساعة. قد يختلف المبلغ الفعلي بسبب تقلب الأسعار.
"""
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 خلف", callback_data="back")]])
        await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")

    elif data == "btn_🔒 حماية من الانتحال":
        set_user_state(query.from_user.id, "main_menu")
        await query.edit_message_text(
            "🔒 حماية من الانتحال\n\nتساعدك هذه الميزة على اكتشاف الأرقام أو الإيميلات المزورة وحمايتك من استخدامها ضدك.\nقريباً ستتوفر تقارير مفصلة.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 خلف", callback_data="back")]])
        )

    elif data == "btn_✉️ تجربة الأرقام/الإيميل":
        set_user_state(query.from_user.id, "main_menu")
        await query.edit_message_text(
            "✉️ تجربة الانتحال\n\nيمكنك تجربة ما إذا كان الرقم أو الإيميل قابلاً للانتحال عبر هذه الميزة.\nستتوفر قريباً كتقرير تفاعلي.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 خلف", callback_data="back")]])
        )

    elif data == "back":
        prev = get_user_state(query.from_user.id)
        if prev:
            query.data = prev
            await handle_inline_buttons(update, context)
        else:
            await language_selected(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_selected, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(handle_inline_buttons, pattern="^(btn_|recharge_|pay_|back)"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_buttons))
    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
