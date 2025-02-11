import os
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("YOUR_API_TOKEN")

# Data storage structure
user_reminders = {}  # Format: {chat_id: {'active': [], 'repetitive': [], 'expired': []}}

repeat_intervals = {
    'daily': timedelta(days=1),
    'weekly': timedelta(weeks=1),
    'monthly': timedelta(days=30),
    'quarterly': timedelta(days=90),
    'half-yearly': timedelta(days=182),
    'yearly': timedelta(days=365)
}

class RepetitiveReminder:
    def __init__(self, chat_id, start_time, message, interval, count=-1):
        self.chat_id = chat_id
        self.start_time = start_time
        self.next_time = start_time
        self.message = message
        self.interval = interval
        self.total_count = count
        self.remaining = count
        self.task = None

# HTTP Server for Render compatibility
async def health_check(request):
    return web.Response(text="Bot is running")

async def run_web_server():
    app = web.Application()
    app.router.add_get('/health', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8080)))
    await site.start()
    logger.info(f"HTTP server running on port {os.getenv('PORT', 8080)}")

# Bot Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📅 Reminder Bot Commands:\n"
        "/remind - Set a new reminder\n"
        "/list - Show all reminders\n"
        "/repetitive - List only repeating reminders\n"
        "/expired - Show completed reminders\n"
        "/delete <number> - Delete any reminder\n"
        "/cancel <number> - Cancel repeating reminder\n"
        "/help - Show this message"
    )
    await update.message.reply_text(help_text)

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("❌ Usage: /remind dd-mm-yyyy HH:MM \"Message\" [repeat] [count]")
            return

        # Parse arguments
        date_str, time_str = args[0], args[1]
        message_parts = []
        repeat_type = None
        repeat_count = -1
        
        # Smart message parsing
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
        chat_id = update.message.chat_id
        
        # Parse datetime
        reminder_time = datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M")
        
        # Initialize user storage
        if chat_id not in user_reminders:
            user_reminders[chat_id] = {
                'active': [],
                'repetitive': [],
                'expired': []
            }
        
        # Create reminder
        if repeat_type:
            reminder = RepetitiveReminder(
                chat_id=chat_id,
                start_time=reminder_time,
                message=message,
                interval=repeat_type,
                count=repeat_count
            )
            user_reminders[chat_id]['repetitive'].append(reminder)
            reminder.task = asyncio.create_task(
                handle_repetitive_reminder(context.bot, reminder)
            )
        else:
            user_reminders[chat_id]['active'].append({
                'time': reminder_time,
                'message': message
            })
            asyncio.create_task(
                handle_single_reminder(context.bot, chat_id, reminder_time, message)
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

async def handle_single_reminder(bot, chat_id, reminder_time, message):
    try:
        delay = (reminder_time - datetime.now()).total_seconds()
        if delay > 0:
            await asyncio.sleep(delay)
        
        await bot.send_message(
            chat_id=chat_id,
            text=f"⏰ Reminder: {message}"
        )
        
        # Move to expired
        user_data = user_reminders.get(chat_id, {})
        if 'active' in user_data:
            user_data['active'] = [
                r for r in user_data['active']
                if r['time'] != reminder_time or r['message'] != message
            ]
        if 'expired' in user_data:
            user_data['expired'].append({
                'time': reminder_time,
                'message': message
            })
            
    except Exception as e:
        logger.error(f"Error in single reminder: {str(e)}")

async def handle_repetitive_reminder(bot, reminder):
    try:
        while reminder.remaining != 0:
            delay = (reminder.next_time - datetime.now()).total_seconds()
            if delay > 0:
                await asyncio.sleep(delay)
            
            await bot.send_message(
                chat_id=reminder.chat_id,
                text=f"🔁 Repeating: {reminder.message}"
            )
            
            if reminder.remaining > 0:
                reminder.remaining -= 1
                if reminder.remaining == 0:
                    break
            
            # Schedule next occurrence
            reminder.next_time += repeat_intervals[reminder.interval]
            
    except asyncio.CancelledError:
        logger.info(f"Cancelled reminder: {reminder.message}")
    finally:
        # Cleanup after completion or cancellation
        user_data = user_reminders.get(reminder.chat_id, {})
        if 'repetitive' in user_data and reminder in user_data['repetitive']:
            user_data['repetitive'].remove(reminder)
        if 'expired' in user_data:
            user_data['expired'].append({
                'time': reminder.start_time,
                'message': reminder.message,
                'repeat': reminder.interval
            })

async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_data = user_reminders.get(chat_id, {})
    response = ["📋 All Reminders"]
    
    # Active reminders
    if user_data.get('active'):
        response.append("\n🔵 One-time Reminders:")
        for idx, rem in enumerate(user_data['active'], 1):
            response.append(f"{idx}. {rem['time'].strftime('%d-%m-%Y %H:%M')}: {rem['message']}")
    
    # Repetitive reminders
    if user_data.get('repetitive'):
        response.append("\n🔄 Repeating Reminders:")
        for idx, rem in enumerate(user_data['repetitive'], len(user_data.get('active', [])) + 1):
            status = f"({rem.interval}"
            if rem.total_count > 0:
                status += f", {rem.remaining} left"
            else:
                status += ", endless"
            status += ")"
            response.append(f"{idx}. {rem.next_time.strftime('%d-%m-%Y %H:%M')}: {rem.message} {status}")
    
    # Expired reminders
    if user_data.get('expired'):
        response.append("\n🔴 Completed Reminders:")
        for idx, rem in enumerate(user_data['expired'], 1):
            response.append(f"{idx}. {rem['time'].strftime('%d-%m-%Y %H:%M')}: {rem['message']}")
    
    if len(response) == 1:
        response.append("\nNo reminders found!")
    
    await update.message.reply_text("\n".join(response))

async def delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.message.chat_id
        args = context.args
        
        if not args or not args[0].isdigit():
            await update.message.reply_text("❌ Usage: /delete <number>")
            return
            
        index = int(args[0]) - 1
        user_data = user_reminders.get(chat_id, {})
        
        # Try active reminders first
        if 'active' in user_data and 0 <= index < len(user_data['active']):
            deleted = user_data['active'].pop(index)
            await update.message.reply_text(
                f"🗑️ Deleted one-time reminder:\n"
                f"{deleted['time'].strftime('%d-%m-%Y %H:%M')}: {deleted['message']}"
            )
            return
            
        # Adjust index for repetitive reminders
        index -= len(user_data.get('active', []))
        if 'repetitive' in user_data and 0 <= index < len(user_data['repetitive']):
            reminder = user_data['repetitive'].pop(index)
            reminder.task.cancel()
            await update.message.reply_text(
                f"❌ Cancelled repeating reminder:\n"
                f"{reminder.next_time.strftime('%d-%m-%Y %H:%M')}: {reminder.message}"
            )
            return
            
        # Check expired reminders
        index -= len(user_data.get('repetitive', []))
        if 'expired' in user_data and 0 <= index < len(user_data['expired']):
            deleted = user_data['expired'].pop(index)
            await update.message.reply_text(
                f"🗑️ Deleted completed reminder:\n"
                f"{deleted['time'].strftime('%d-%m-%Y %H:%M')}: {deleted['message']}"
            )
            return
            
        await update.message.reply_text("❌ Invalid reminder number")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def repetitive_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_data = user_reminders.get(chat_id, {})
    
    response = ["🔄 Active Repeating Reminders"]
    if user_data.get('repetitive'):
        for idx, rem in enumerate(user_data['repetitive'], 1):
            status = f"({rem.interval}, "
            status += f"{rem.remaining} left" if rem.total_count > 0 else "endless"
            status += ")"
            response.append(f"{idx}. {rem.next_time.strftime('%d-%m-%Y %H:%M')}: {rem.message} {status}")
    else:
        response.append("No active repeating reminders")
    
    await update.message.reply_text("\n".join(response))

async def expired_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_data = user_reminders.get(chat_id, {})
    
    response = ["🔴 Completed/Expired Reminders"]
    if user_data.get('expired'):
        for idx, rem in enumerate(user_data['expired'], 1):
            response.append(f"{idx}. {rem['time'].strftime('%d-%m-%Y %H:%M')}: {rem['message']}")
    else:
        response.append("No completed reminders")
    
    await update.message.reply_text("\n".join(response))

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Command handlers
    handlers = [
        CommandHandler("start", start),
        CommandHandler("remind", set_reminder),
        CommandHandler("list", list_reminders),
        CommandHandler("delete", delete_reminder),
        CommandHandler("repetitive", repetitive_reminders),
        CommandHandler("expired", expired_reminders),
        CommandHandler("help", start)
    ]
    
    for handler in handlers:
        application.add_handler(handler)
    
    # Start both Telegram bot and HTTP server
    loop = asyncio.get_event_loop()
    loop.create_task(application.run_polling())
    loop.create_task(run_web_server())
    loop.run_forever()

if __name__ == "__main__":
    main()
