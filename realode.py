from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

# Replace with your bot API key
API_KEY = "8509386079:AAGo1ZZki1t1pJRW3xzZllrIXrPvpjxXueY"

# Placeholder: Replace with actual details
CHANNELS = [
    "https://t.me/Movie_Zone_Vip", 
    "https://t.me/Reading_Book_Movie_Zone", 
    "https://t.me/quotes_Srilanka", 
    "https://t.me/+JWscqPT8saEwZThl", 
    "https://t.me/+66O0nXcSlTNjZTk9", 
    "https://t.me/+RZzIcgCPk8ZjY2Zl"
]

OWNER_ID = 8452357204 # Your owner telegram user ID
ADMIN_GROUP_ID = -5139705408  # Admin group ID

user_balance = {}
user_referrals = {}

def is_user_joined(user_id):
    for channel in CHANNELS:
        try:
            # Check if the user is a member of each channel
            member = bot.get_chat_member(channel, user_id)
            if member.status == "left":
                return False
        except Exception as e:
            return False
    return True

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    user_balance[user_id] = 0  # Initialize user balance

    # Send start message with channel join link and "try again" button
    if not is_user_joined(user_id):
        update.message.reply_text(
            "Please join all the following channels before using the bot:\n" + 
            "\n".join(CHANNELS) + "\nThen try again."
        )
    else:
        # Show buttons for Balance, Referral, and Withdrawal
        keyboard = [
            ['Balance', 'Referral'],
            ['Withdrawal']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text(f"Welcome {user_name}!", reply_markup=reply_markup)

def balance(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    balance = user_balance.get(user_id, 0)
    update.message.reply_text(f"Your balance is: Rs {balance}")

def referral(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    referral_link = f"t.me/yourbot?start={user_id}"
    user_referrals[user_id] = user_referrals.get(user_id, 0) + 1
    update.message.reply_text(f"Your referral link: {referral_link}")

def withdrawal(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_balance.get(user_id, 0) < 50:
        update.message.reply_text("Minimum withdrawal is Rs 50.")
        return

    update.message.reply_text("Please provide your name.")
    return "WAITING_FOR_NAME"

def handle_withdrawal_name(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_name = update.message.text
    update.message.reply_text("Please provide the amount you'd like to withdraw (minimum Rs 50).")
    return "WAITING_FOR_AMOUNT"

def handle_withdrawal_amount(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    amount = int(update.message.text)
    if amount < 50:
        update.message.reply_text("Minimum withdrawal amount is Rs 50.")
        return
    # Ask for Reload number
    update.message.reply_text("Please provide your Reload number.")
    return "WAITING_FOR_RELOAD"

def handle_reload_number(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    reload_number = update.message.text
    update.message.reply_text(f"Your request is being processed. Reload will arrive within 24 hours.")
    
    # Send the request to admin group
    context.bot.send_message(
        ADMIN_GROUP_ID,
        f"User {user_id} requested withdrawal. Details:\nName: {user_name}\nAmount: Rs {amount}\nReload Number: {reload_number}"
    )

    return "PROCESSING"

def owner_send(update: Update, context: CallbackContext):
    if update.message.from_user.id == OWNER_ID:
        user_id = int(context.args[0])
        amount = int(context.args[1])
        user_balance[user_id] += amount
        context.bot.send_message(user_id, f"Your balance has been credited with Rs {amount}.")

def users(update: Update, context: CallbackContext):
    if update.message.from_user.id == OWNER_ID:
        all_users = '\n'.join([str(user) for user in user_balance.keys()])
        update.message.reply_text(f"All Users: {all_users}")

def main():
    updater = Updater(API_KEY)
    dispatcher = updater.dispatcher

    # Commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("balance", balance))
    dispatcher.add_handler(CommandHandler("referral", referral))
    dispatcher.add_handler(CommandHandler("withdrawal", withdrawal))
    dispatcher.add_handler(CommandHandler("send", owner_send, pass_args=True))
    dispatcher.add_handler(CommandHandler("users", users))

    # Message Handlers
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_withdrawal_name))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_withdrawal_amount))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_reload_number))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
