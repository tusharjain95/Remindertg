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

# Environment variables (keep original TOKEN name)
TOKEN = os.getenv("YOUR_API_TOKEN")
PORT = int(os.getenv("PORT", 10000))  # Render default port
HOST = os.getenv("HOST", "0.0.0.0")

# Validate Render-reserved ports
if PORT in {18012, 18013, 19099}:
    raise ValueError(f"Port {PORT} is reserved by Render")

# Data storage structure (unchanged)
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
        self.chat_id = chat_id
        self.start_time = start_time
        self.next_time = start_time
        self.message = message
        self.interval = interval
        self.total_count = count
        self.remaining = count
        self.task = None

# Enhanced HTTP Server
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

# Bot commands and handlers (unchanged except async context)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... [original start command implementation] ...

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... [original set_reminder implementation] ...

async def handle_single_reminder(bot, chat_id, reminder_time, message):
    # ... [original single reminder handler] ...

async def handle_repetitive_reminder(bot, reminder):
    # ... [original repetitive reminder handler] ...

async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... [original list command implementation] ...

async def delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... [original delete command implementation] ...

async def repetitive_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... [original repetitive command implementation] ...

async def expired_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... [original expired command implementation] ...

# Modified main function for Render compatibility
async def main():
    application = Application.builder().token(TOKEN).build()
    
    # Register handlers
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
    
    # Start web server first
    await run_web_server()
    
    # Start bot polling
    logger.info("Starting Telegram bot polling")
    await application.run_polling()

if __name__ == "__main__":
    # Configure proper shutdown handling
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
    finally:
        loop.close()
        
