import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta
import asyncio

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("YOUR_API_TOKEN")

# Data structure improvements
user_reminders = {
    # chat_id: {
    #     'active': [],
    #     'repetitive': [],
    #     'expired': []
    # }
}

repeat_intervals = {
    'daily': timedelta(days=1),
    'weekly': timedelta(weeks=1),
    'monthly': timedelta(days=30),
    'quarterly': timedelta(days=90),
    'half-yearly': timedelta(days=182),
    'yearly': timedelta(days=365)
}

class ReminderTask:
    def __init__(self, chat_id, reminder_time, message, repeat, repeat_count=-1):
        self.chat_id = chat_id
        self.original_time = reminder_time
        self.next_time = reminder_time
        self.message = message
        self.repeat = repeat
        self.repeat_count = repeat_count
        self.remaining_repeats = repeat_count
        self.task = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📅 Reminder Bot Commands:\n"
        "/remind - Set a new reminder\n"
        "/list - Show all reminders\n"
        "/repetitive - List only repetitive reminders\n"
        "/expired - Show completed reminders\n"
        "/cancel - Stop a repetitive reminder\n"
        "/help - Show this message"
    )
    await update.message.reply_text(help_text)

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("❌ Usage: /remind dd-mm-yyyy HH:MM \"Message\" [repeat_type] [repeat_count]")
            return

        # Parse arguments
        date_str, time_str = args[0], args[1]
        message_parts = []
        repeat_type = None
        repeat_count = -1  # -1 means infinite
        
        # Smart argument parsing
        in_quote = False
        for arg in args[2:]:
            if arg.startswith('"'):
                in_quote = True
                arg = arg[1:]
            if arg.endswith('"'):
                in_quote = False
                arg = arg[:-1]
            
            if in_quote:
                message_parts.append(arg)
            else:
                if arg in repeat_intervals:
                    repeat_type = arg
                elif arg.isdigit():
                    repeat_count = int(arg)
                else:
                    message_parts.append(arg)
        
        message = " ".join(message_parts)
        
        # Validate and parse time
        reminder_time = datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M")
        chat_id = update.message.chat_id
        
        # Initialize user storage if needed
        if chat_id not in user_reminders:
            user_reminders[chat_id] = {
                'active': [],
                'repetitive': [],
                'expired': []
            }
        
        # Create reminder object
        if repeat_type:
            reminder = ReminderTask(
                chat_id=chat_id,
                reminder_time=reminder_time,
                message=message,
                repeat=repeat_type,
                repeat_count=repeat_count
            )
            user_reminders[chat_id]['repetitive'].append(reminder)
            reminder.task = asyncio.create_task(
                send_repetitive_reminder(reminder)
            )
        else:
            user_reminders[chat_id]['active'].append({
                'time': reminder_time,
                'message': message
            })
            asyncio.create_task(
                send_single_reminder(chat_id, reminder_time, message)
            )
        
        # Build response
        response = f"✅ Reminder set for {reminder_time.strftime('%d-%m-%Y %H:%M')}"
        if repeat_type:
            response += f"\n🔁 Repeat: {repeat_type}"
            if repeat_count > 0:
                response += f" ({repeat_count} times)"
            else:
                response += " (indefinitely)"
        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def send_single_reminder(chat_id, reminder_time, message):
    delay = (reminder_time - datetime.now()).total_seconds()
    if delay > 0:
        await asyncio.sleep(delay)
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"⏰ Reminder: {message}"
    )
    # Move to expired
    user_reminders[chat_id]['active'] = [
        r for r in user_reminders[chat_id]['active']
        if r['time'] != reminder_time or r['message'] != message
    ]
    user_reminders[chat_id]['expired'].append({
        'time': reminder_time,
        'message': message
    })

async def send_repetitive_reminder(reminder):
    try:
        while reminder.remaining_repeats != 0:
            delay = (reminder.next_time - datetime.now()).total_seconds()
            if delay > 0:
                await asyncio.sleep(delay)
            
            await context.bot.send_message(
                chat_id=reminder.chat_id,
                text=f"🔁 Repetitive Reminder: {reminder.message}"
            )
            
            if reminder.remaining_repeats > 0:
                reminder.remaining_repeats -= 1
            
            if reminder.remaining_repeats == 0:
                break
                
            reminder.next_time += repeat_intervals[reminder.repeat]
            
    except asyncio.CancelledError:
        # Cleanup when task is cancelled
        user_reminders[reminder.chat_id]['repetitive'].remove(reminder)
    finally:
        if reminder.remaining_repeats == 0:
            user_reminders[reminder.chat_id]['expired'].append({
                'time': reminder.original_time,
                'message': reminder.message,
                'repeat': reminder.repeat
            })
            user_reminders[reminder.chat_id]['repetitive'].remove(reminder)

async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    response = ["📋 Your Reminders"]
    
    # Active reminders
    if user_reminders.get(chat_id, {}).get('active'):
        response.append("\n🔵 One-time Reminders:")
        for idx, reminder in enumerate(user_reminders[chat_id]['active'], 1):
            response.append(f"{idx}. {reminder['time'].strftime('%d-%m-%Y %H:%M')}: {reminder['message']}")
    else:
        response.append("\n🔵 No one-time reminders")
        
    # Repetitive reminders
    if user_reminders.get(chat_id, {}).get('repetitive'):
        response.append("\n🔄 Repetitive Reminders:")
        for idx, reminder in enumerate(user_reminders[chat_id]['repetitive'], 1):
            status = f"({reminder.repeat}"
            if reminder.repeat_count > 0:
                status += f", {reminder.remaining_repeats} remaining"
            else:
                status += ", infinite"
            status += ")"
            response.append(f"{idx}. {reminder.next_time.strftime('%d-%m-%Y %H:%M')}: {reminder.message} {status}")
    else:
        response.append("\n🔄 No repetitive reminders")
        
    await update.message.reply_text("\n".join(response))

async def repetitive_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    response = ["🔄 Repetitive Reminders"]
    
    if user_reminders.get(chat_id, {}).get('repetitive'):
        for idx, reminder in enumerate(user_reminders[chat_id]['repetitive'], 1):
            status = f"({reminder.repeat}"
            if reminder.repeat_count > 0:
                status += f", {reminder.remaining_repeats} remaining"
            else:
                status += ", infinite"
            status += ")"
            response.append(f"{idx}. {reminder.next_time.strftime('%d-%m-%Y %H:%M')}: {reminder.message} {status}")
    else:
        response.append("No active repetitive reminders")
        
    await update.message.reply_text("\n".join(response))

async def cancel_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.message.chat_id
        args = context.args
        
        if not args or not args[0].isdigit():
            await update.message.reply_text("❌ Usage: /cancel <reminder_number>")
            return
            
        index = int(args[0]) - 1
        if (user_reminders.get(chat_id, {}).get('repetitive') and 
            0 <= index < len(user_reminders[chat_id]['repetitive'])):
            reminder = user_reminders[chat_id]['repetitive'][index]
            reminder.task.cancel()
            await update.message.reply_text(f"❌ Cancelled repetitive reminder: {reminder.message}")
        else:
            await update.message.reply_text("❌ Invalid reminder number")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def expired_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    response = ["🔴 Expired/Completed Reminders"]
    
    if user_reminders.get(chat_id, {}).get('expired'):
        for idx, reminder in enumerate(user_reminders[chat_id]['expired'], 1):
            response.append(f"{idx}. {reminder['time'].strftime('%d-%m-%Y %H:%M')}: {reminder['message']}")
    else:
        response.append("No expired reminders")
        
    await update.message.reply_text("\n".join(response))

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("remind", set_reminder))
    application.add_handler(CommandHandler("list", list_reminders))
    application.add_handler(CommandHandler("repetitive", repetitive_reminders))
    application.add_handler(CommandHandler("expired", expired_reminders))
    application.add_handler(CommandHandler("cancel", cancel_reminder))
    application.add_handler(CommandHandler("help", start))
    
    application.run_polling()

if __name__ == "__main__":
    main()
