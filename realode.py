from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

API_KEY = "8509386079:AAGo1ZZki1t1pJRW3xzZllrIXrPvpjxXueY"

CHANNELS = [
    "@Movie_Zone_Vip",
    "@Reading_Book_Movie_Zone",
    "https://t.me/+JWscqPT8saEwZThl"
]

OWNER_ID = 8452357204
ADMIN_GROUP_ID = -5139705408

user_balance = {}
withdraw_states = {}

# ---------- UTIL ----------
async def is_user_joined(bot, user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# ---------- COMMANDS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    user_balance.setdefault(user_id, 0)

    joined = await is_user_joined(context.bot, user_id)
    if not joined:
        await update.message.reply_text(
            "❌ Please join all channels first:\n\n" +
            "\n".join(CHANNELS) +
            "\n\nThen send /start again"
        )
        return

    keyboard = [["Balance", "Referral"], ["Withdrawal"]]
    await update.message.reply_text(
        f"Welcome {user_name} 👋",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bal = user_balance.get(update.effective_user.id, 0)
    await update.message.reply_text(f"💰 Your balance: Rs {bal}")

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    link = f"https://t.me/yourbot?start={uid}"
    await update.message.reply_text(f"🔗 Your referral link:\n{link}")

async def withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if user_balance.get(uid, 0) < 50:
        await update.message.reply_text("❌ Minimum withdrawal is Rs 50")
        return

    withdraw_states[uid] = {"step": "name"}
    await update.message.reply_text("Enter your name:")

async def owner_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    uid = int(context.args[0])
    amount = int(context.args[1])
    user_balance[uid] = user_balance.get(uid, 0) + amount
    await context.bot.send_message(uid, f"✅ Credited Rs {amount}")

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text(
            "👥 Users:\n" + "\n".join(map(str, user_balance.keys()))
        )

# ---------- MESSAGE HANDLER ----------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    if uid not in withdraw_states:
        return

    state = withdraw_states[uid]

    if state["step"] == "name":
        state["name"] = text
        state["step"] = "amount"
        await update.message.reply_text("Enter withdrawal amount:")

    elif state["step"] == "amount":
        amount = int(text)
        if amount < 50:
            await update.message.reply_text("❌ Minimum Rs 50")
            return
        state["amount"] = amount
        state["step"] = "reload"
        await update.message.reply_text("Enter reload number:")

    elif state["step"] == "reload":
        state["reload"] = text

        await context.bot.send_message(
            ADMIN_GROUP_ID,
            f"💸 Withdrawal Request\n"
            f"User: {uid}\n"
            f"Name: {state['name']}\n"
            f"Amount: Rs {state['amount']}\n"
            f"Reload: {state['reload']}"
        )

        await update.message.reply_text("✅ Request sent. Reload within 24 hours.")
        withdraw_states.pop(uid)

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

    app.run_polling()

if __name__ == "__main__":
    main()
