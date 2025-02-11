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

# Environment variables
TOKEN = os.getenv("YOUR_API_TOKEN")
PORT = int(os.getenv("PORT", 10000))
HOST = os.getenv("HOST", "0.0.0.0")

if PORT in {18012, 18013, 19099}:
    raise ValueError(f"Port {PORT} is reserved by Render")

# Data storage structure
user_reminders = {}
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
        # Fixed indentation here
        self.chat_id = chat_id
        self.start_time = start_time
        self.next_time = start_time
        self.message = message
        self.interval = interval
        self.total_count = count
        self.remaining = count
        self.task = None

async def health_check(request):
    return web.Response(text="OK", status=200)

async def run_web_server():
    logger.info(f"Starting web server on {HOST}:{PORT}")
    app = web.Application()
    app.router.add_get('/health', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()
    logger.info(f"Server running on port {PORT}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📅 Reminder Bot Commands:\n"
        "/remind - Set a new reminder\n"
        "/list - Show all reminders\n"
        "/repetitive - List repeating reminders\n"
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
            await update.message.reply_text('❌ Usage: /remind dd-mm-yyyy HH:MM "Message" [repeat] [count]')
            return

        date_str, time_str = args[0], args[1]
        message_parts = []
        repeat_type = None
        repeat_count = -1
        
        in_quote = False
        for arg in args[2:]:
            if arg.
