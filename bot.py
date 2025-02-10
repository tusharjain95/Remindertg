import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta
import asyncio

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to store reminders for each user
user_reminders = {}  # Active reminders
user_expired_reminders = {}  # Expired reminders

# Command to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm your reminder bot. Use /remind to set a reminder, /list to view active reminders, or /expired to view expired reminders.")

# Command to set a reminder
async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Parse the command: /remind YYYY-MM-DD HH:MM "Message" [repeat]
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Usage: /remind YYYY-MM-DD HH:MM \"Message\" [repeat]")
            return

        date_str = args[0]
        time_str = args[1]
        message = " ".join(args[2:-1]) if len(args) > 3 else args[2]
        repeat = args[-1] if len(args) > 3 else None

        # Parse date and time
        reminder_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

        # Store reminder
        chat_id = update.message.chat_id
        if chat_id not in user_reminders:
            user_reminders[chat_id] = []

        reminder = {
            "time": reminder_time,
            "message": message,
            "repeat": repeat
        }
        user_reminders[chat_id].append(reminder)

        await update.message.reply_text(f"Reminder set for {reminder_time}!")

        # Schedule the reminder
        asyncio.create_task(send_reminder(chat_id, reminder_time, message, repeat))

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Function to send reminders
async def send_reminder(chat_id, reminder_time, message, repeat):
    while True:
        delay = (reminder_time - datetime.now()).total_seconds()
        if delay > 0:
            await asyncio.sleep(delay)
        await context.bot.send_message(chat_id=chat_id, text=f"Reminder: {message}")

        # Move the reminder to expired list if it's non-repeating
        if not repeat:
            if chat_id not in user_expired_reminders:
                user_expired_reminders[chat_id] = []
            expired_reminder = {
                "time": reminder_time,
                "message": message
            }
            user_expired_reminders[chat_id].append(expired_reminder)

            # Remove the reminder from active list
            if chat_id in user_reminders:
                user_reminders[chat_id] = [r for r in user_reminders[chat_id] if r["time"] != reminder_time or r["message"] != message]
            break
        else:
            # Handle repeating reminders
            if repeat == "daily":
                reminder_time += timedelta(days=1)
            elif repeat == "weekly":
                reminder_time += timedelta(weeks=1)

# Command to list active reminders
async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in user_reminders and user_reminders[chat_id]:
        reminders_list = []
        for i, reminder in enumerate(user_reminders[chat_id], start=1):
            reminders_list.append(
                f"{i}. {reminder['time'].strftime('%Y-%m-%d %H:%M')}: {reminder['message']} "
                f"(Repeat: {reminder['repeat'] if reminder['repeat'] else 'No'})"
            )
        await update.message.reply_text("Your active reminders:\n" + "\n".join(reminders_list))
    else:
        await update.message.reply_text("You have no active reminders.")

# Command to list expired reminders
async def list_expired_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in user_expired_reminders and user_expired_reminders[chat_id]:
        expired_list = []
        for i, reminder in enumerate(user_expired_reminders[chat_id], start=1):
            expired_list.append(
                f"{i}. {reminder['time'].strftime('%Y-%m-%d %H:%M')}: {reminder['message']}"
            )
        await update.message.reply_text("Your expired reminders:\n" + "\n".join(expired_list))
    else:
        await update.message.reply_text("You have no expired reminders.")

# Main function to run the bot
def main():
    # Replace 'YOUR_API_TOKEN' with your bot's API token
    application = Application.builder().token("YOUR_API_TOKEN").build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("remind", set_reminder))
    application.add_handler(CommandHandler("list", list_reminders))
    application.add_handler(CommandHandler("expired", list_expired_reminders))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
