from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

API_KEY = "8509386079:AAGo1ZZki1t1pJRW3xzZllrIXrPvpjxXueY"

CHANNELS = {
    "Movie Zone VIP": "https://t.me/Movie_Zone_Vip",
    "Reading Book": "https://t.me/Reading_Book_Movie_Zone",
    "Fine X Hub": "https://t.me/+JWscqPT8saEwZThl"
}

OWNER_ID = 8452357204
ADMIN_GROUP_ID = -5139705408

MIN_WITHDRAW = 50
REF_BONUS = 4

user_balance = {}
withdraw_states = {}

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(name, url=url)]
        for name, url in CHANNELS.items()
    ]
    keyboard.append([InlineKeyboardButton("🔁 Try Again", callback_data="try")])

    await update.message.reply_text(
        "🔔 Please join these channels 👇\n(Join or not – you can still try)",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------- TRY AGAIN ----------
async def try_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    user_balance.setdefault(uid, 0)

    keyboard = [["Balance", "Referral"], ["Withdrawal"]]

    await query.message.reply_photo(
        photo="https://files.catbox.moe/ii1zn5.jpg",
        caption="✅ Bot Menu",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ---------- BALANCE ----------
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bal = user_balance.get(update.effective_user.id, 0)
    await update.message.reply_text(f"💰 Balance: Rs {bal}")

# ---------- REFERRAL ----------
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    link = f"https://t.me/yourbot?start={uid}"
    await update.message.reply_text(
        f"🔗 Your Referral Link:\n{link}\n\n"
        f"🎁 Bonus per referral: Rs {REF_BONUS}"
    )

# ---------- WITHDRAW ----------
async def withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if user_balance.get(uid, 0) < MIN_WITHDRAW:
        await update.message.reply_text(
            f"❌ Minimum withdrawal is Rs {MIN_WITHDRAW}"
        )
        return

    withdraw_states[uid] = {"step": "amount"}
    await update.message.reply_text("💸 Enter withdrawal amount:")

# ---------- TEXT HANDLER ----------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    if uid not in withdraw_states:
        return

    state = withdraw_states[uid]

    if state["step"] == "amount":
        amount = int(text)
        if amount < MIN_WITHDRAW:
            await update.message.reply_text("❌ Minimum Rs 50")
            return

        state["amount"] = amount
        state["step"] = "mobile"
        await update.message.reply_text("📱 Enter mobile number:")

    elif state["step"] == "mobile":
        state["mobile"] = text
        name = update.effective_user.first_name

        await context.bot.send_message(
            ADMIN_GROUP_ID,
            f"💸 Withdrawal Request\n\n"
            f"👤 Name: {name}\n"
            f"🆔 ID: {uid}\n"
            f"💰 Amount: Rs {state['amount']}\n"
            f"📱 Mobile: {state['mobile']}"
        )

        await update.message.reply_text(
            "✅ Request sent.\nReload will be credited within 24 hours."
        )
        withdraw_states.pop(uid)

# ---------- OWNER SEND ----------
async def owner_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    uid = int(context.args[0])
    amount = int(context.args[1])

    user_balance[uid] = user_balance.get(uid, 0) + amount

    await context.bot.send_message(
        uid,
        f"✅ Rs {amount} credited.\nYour reload will arrive within 24 hours."
    )

    await update.message.reply_text("✔ Balance updated")

# ---------- USERS ----------
async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text(
            "👥 Users:\n" + "\n".join(map(str, user_balance.keys()))
        )

# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(API_KEY).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("referral", referral))
    app.add_handler(CommandHandler("withdrawal", withdrawal))
    app.add_handler(CommandHandler("send", owner_send))
    app.add_handler(CommandHandler("users", users))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(filters.CallbackQueryHandler(try_again, pattern="try"))

    app.run_polling()

if __name__ == "__main__":
    main()
