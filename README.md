# Telegram Reminder Bot

A simple Telegram bot to help you set reminders for specific dates and times. You can set one-time reminders or repeating reminders (daily/weekly). The bot also allows you to view active and expired reminders.

---

## Table of Contents
1. [Commands](#commands)
   - [/start](#start)
   - [/remind](#remind)
   - [/list](#list)
   - [/expired](#expired)
2. [Use Cases](#use-cases)
3. [How to Host](#how-to-host)
4. [Contributing](#contributing)

---

## Commands

### `/start`
Starts the bot and provides a welcome message with instructions.

**Syntax**:
```
/start
```

**Example**:
```
/start
```

**Response**:
```
Hi! I'm your reminder bot. Use /remind to set a reminder, /list to view active reminders, or /expired to view expired reminders.
```

---

### `/remind`
Sets a reminder for a specific date and time. You can also set repeating reminders (daily or weekly).

**Syntax**:
```
/remind YYYY-MM-DD HH:MM "Your Message" [repeat]
```

- **`YYYY-MM-DD`**: The date for the reminder (e.g., `2025-02-12`).
- **`HH:MM`**: The time for the reminder (e.g., `09:00`).
- **`"Your Message"`**: The reminder message (enclosed in quotes).
- **`[repeat]`**: (Optional) The repetition interval (`daily` or `weekly`).

**Examples**:
1. **One-Time Reminder**:
   ```
   /remind 2025-02-12 09:00 "Take your vitamins"
   ```
   - Sets a reminder for February 12, 2025, at 9:00 AM.

2. **Daily Reminder**:
   ```
   /remind 2025-02-12 07:00 "Good morning! Time for a jog" daily
   ```
   - Sets a daily reminder starting from February 12, 2025, at 7:00 AM.

3. **Weekly Reminder**:
   ```
   /remind 2025-02-12 10:00 "Weekly report due" weekly
   ```
   - Sets a weekly reminder starting from February 12, 2025, at 10:00 AM.

**Response**:
```
Reminder set for 2025-02-12 09:00!
```

---

### `/list`
Lists all active reminders.

**Syntax**:
```
/list
```

**Example**:
```
/list
```

**Response**:
```
Your active reminders:
1. 2025-02-12 09:00: Take your vitamins (Repeat: No)
2. 2025-02-12 07:00: Good morning! Time for a jog (Repeat: daily)
```

---

### `/expired`
Lists all expired reminders.

**Syntax**:
```
/expired
```

**Example**:
```
/expired
```

**Response**:
```
Your expired reminders:
1. 2025-02-12 09:00: Take your vitamins
2. 2025-02-12 18:00: Weekly team meeting
```

---

## Use Cases

1. **Personal Reminders**:
   - Set reminders for daily tasks like taking medication, exercising, or attending meetings.
   - Example:
     ```
     /remind 2025-02-12 08:00 "Take your vitamins" daily
     ```

2. **Work Reminders**:
   - Set reminders for deadlines, meetings, or weekly reports.
   - Example:
     ```
     /remind 2025-02-12 10:00 "Submit weekly report" weekly
     ```

3. **Event Reminders**:
   - Set reminders for special events like birthdays or anniversaries.
   - Example:
     ```
     /remind 2025-02-12 18:00 "Call John for his birthday"
     ```

---

## How to Host

### Prerequisites
- Python 3.7 or higher.
- A Telegram bot token from [BotFather](https://core.telegram.org/bots#botfather).

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
   cd YOUR_REPOSITORY_NAME
   ```

2. **Install Dependencies**:
   ```bash
   pip install python-telegram-bot
   ```

3. **Set Environment Variable**:
   - Set the `YOUR_API_TOKEN` environment variable with your Telegram bot token.
   - On Linux/macOS:
     ```bash
     export YOUR_API_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
     ```
   - On Windows (Command Prompt):
     ```cmd
     set YOUR_API_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
     ```

4. **Run the Bot**:
   ```bash
   python3 bot.py
   ```

5. **Deploy on Render**:
   - Follow the [Render deployment guide](#render-deployment).

---

### Render Deployment
1. Sign up at [Render](https://render.com).
2. Create a new **Web Service** and connect your GitHub repository.
3. Set the `YOUR_API_TOKEN` environment variable in the Render dashboard.
4. Deploy the service.

---

## Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
