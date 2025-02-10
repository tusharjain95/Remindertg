import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta
import asyncio

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("YOUR_API_TOKEN")

user_reminders = {}  # Active reminders
user_expired_reminders = {}  # Expired reminders

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Use /remind to set reminders, /list to view, /delete to remove, /expired for completed reminders")

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Usage: /remind dd-mm-yyyy HH:MM \"Message\" [repeat]")
            return

        date_str, time_str = args[0], args[1]
        message = " ".join(args[2:-1]) if len(args) > 3 else args[2]
        repeat = args[-1] if len(args) > 3 else None

        reminder_time = datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M")
        chat_id = update.message.chat_id
        
        if chat_id not in user_reminders:
            user_reminders[chat_id] = []
            
        user_reminders[chat_id].append({
            "time": reminder_time,
            "message": message,
            "repeat": repeat
        })

        await update.message.reply_text(f"✅ Reminder set for {reminder_time.strftime('%d-%m-%Y %H:%M')}")
        asyncio.create_task(send_reminder(chat_id, reminder_time, message, repeat))

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def send_reminder(chat_id, reminder_time, message, repeat):
    while True:
        delay = (reminder_time - datetime.now()).total_seconds()
        if delay > 0:
            await asyncio.sleep(delay)
        
        await context.bot.send_message(chat_id=chat_id, text=f"⏰ Reminder: {message}")
        
        if not repeat:
            if chat_id not in user_expired_reminders:
                user_expired_reminders[chat_id] = []
            user_expired_reminders[chat_id].append({
                "time": reminder_time,
                "message": message
            })
            if chat_id in user_reminders:
                user_reminders[chat_id] = [r for r in user_reminders[chat_id] 
                                         if r["time"] != reminder_time or r["message"] != message]
            break
        else:
            if repeat == "daily": reminder_time += timedelta(days=1)
            elif repeat == "weekly": reminder_time += timedelta(weeks=1)
            elif repeat == "monthly": reminder_time += timedelta(days=30)
            elif repeat == "yearly": reminder_time += timedelta(days=365)

async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    response = ["📋 Your Reminders"]
    
    # Active reminders
    if user_reminders.get(chat_id):
        response.append("\n🔵 Active:")
        for idx, reminder in enumerate(user_reminders[chat_id], 1):
            repeat_status = f"(Repeat: {reminder['repeat']})" if reminder['repeat'] else ""
            response.append(f"{idx}. {reminder['time'].strftime('%d-%m-%Y %H:%M')}: {reminder['message']} {repeat_status}")
    else:
        response.append("\n🔵 No active reminders")
        
    # Expired reminders
    if user_expired_reminders.get(chat_id):
        response.append("\n🔴 Expired:")
        for idx, reminder in enumerate(user_expired_reminders[chat_id], 1):
            response.append(f"{idx}. {reminder['time'].strftime('%d-%m-%Y %H:%M')}: {reminder['message']}")
    else:
        response.append("\n🔴 No expired reminders")
        
    await update.message.reply_text("\n".join(response))

async def delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.message.chat_id
        args = context.args
        
        if not args or not args[0].isdigit():
            await update.message.reply_text("Usage: /delete <reminder_number>")
            return
            
        index = int(args[0]) - 1
        if chat_id in user_reminders and 0 <= index < len(user_reminders[chat_id]):
            deleted = user_reminders[chat_id].pop(index)
            await update.message.reply_text(f"🗑️ Deleted reminder: {deleted['message']}")
        else:
            await update.message.reply_text("❌ Invalid reminder number")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def list_expired_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if user_expired_reminders.get(chat_id):
        response = ["🔴 Expired Reminders:"]
        for idx, reminder in enumerate(user_expired_reminders[chat_id], 1):
            response.append(f"{idx}. {reminder['time'].strftime('%d-%m-%Y %H:%M')}: {reminder['message']}")
        await update.message.reply_text("\n".join(response))
    else:
        await update.message.reply_text("🔴 No expired reminders")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("remind", set_reminder))
    application.add_handler(CommandHandler("list", list_reminders))
    application.add_handler(CommandHandler("delete", delete_reminder))
    application.add_handler(CommandHandler("expired", list_expired_reminders))
    application.run_polling()

if __name__ == "__main__":
    main()
