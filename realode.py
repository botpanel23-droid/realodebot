from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
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

user_balance = {}
withdraw_states = {}

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(name, url=url)]
        for name, url in CHANNELS.items()
    ]
    buttons.append([InlineKeyboardButton("🔁 Try Again", callback_data="try_again")])

    await update.message.reply_text(
        "🔔 Please join these channels first 👇",
        reply_markup=InlineKeyboardMarkup(buttons)
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
        caption="👋 Welcome to the Reload Bot\n\nSelect an option below ⬇️",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ---------- BALANCE ----------
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bal = user_balance.get(update.effective_user.id, 0)
    await update.message.reply_text(f"💰 Your Balance: Rs {bal}")

# ---------- REFERRAL ----------
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    link = f"https://t.me/yourbot?start={uid}"
    await update.message.reply_text(
        f"🔗 Your Referral Link:\n{link}"
    )

# ---------- WITHDRAW ----------
async def withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if user_balance.get(uid, 0) < MIN_WITHDRAW:
        await update.message.reply_text("❌ Minimum withdrawal is Rs 50")
        return

    withdraw_states[uid] = {"step": "botname"}
    await update.message.reply_text("🤖 Enter bot name:")

# ---------- TEXT HANDLER ----------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    if uid not in withdraw_states:
        return

    state = withdraw_states[uid]

    if state["step"] == "botname":
        state["botname"] = text
        state["step"] = "mobile"
        await update.message.reply_text("📱 Enter mobile number:")

    elif state["step"] == "mobile":
        state["mobile"] = text
        state["step"] = "amount"
        await update.message.reply_text("💰 Enter withdrawal amount:")

    elif state["step"] == "amount":
        amount = int(text)
        if amount < MIN_WITHDRAW:
            await update.message.reply_text("❌ Minimum withdrawal is Rs 50")
            return

        state["amount"] = amount
        name = update.effective_user.first_name

        await context.bot.send_message(
            ADMIN_GROUP_ID,
            f"💸 Withdrawal Request\n\n"
            f"👤 User: {name}\n"
            f"🆔 ID: {uid}\n"
            f"🤖 Bot: {state['botname']}\n"
            f"📱 Mobile: {state['mobile']}\n"
            f"💰 Amount: Rs {state['amount']}"
        )

        await update.message.reply_text(
            "✅ Withdrawal request sent.\nReload will be credited within 24 hours."
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
        f"✅ Rs {amount} credited.\nReload will be added within 24 hours."
    )

    await update.message.reply_text("✔ Balance updated")

# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(API_KEY).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("referral", referral))
    app.add_handler(CommandHandler("withdrawal", withdrawal))
    app.add_handler(CommandHandler("send", owner_send))

    app.add_handler(CallbackQueryHandler(try_again, pattern="try_again"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
