# Telegram Reminder Bot

A Telegram bot to schedule reminders with support for **daily, weekly, monthly, quarterly, half-yearly, and yearly repeats**. Set one-time or recurring reminders and view active/expired reminders effortlessly.

---

## Table of Contents
1. [Commands](#commands)
   - [/start](#start)
   - [/remind](#remind)
   - [/list](#list)
   - [/expired](#expired)
2. [Use Cases](#use-cases)
3. [Hosting Guide](#hosting-guide)
4. [Contributing](#contributing)
5. [License](#license)

---

## Commands

### `/start`
Start the bot and view instructions.

**Syntax**:
```
/start
```

**Response**:
```
Hi! I'm your reminder bot. Use /remind to set a reminder, /list to view active reminders, or /expired to view expired reminders.
```

---

### `/remind`
Set a reminder with optional repeats.  
**Supports**: `daily`, `weekly`, `monthly`, `quarterly`, `half-yearly`, `yearly`.

**Syntax**:
```
/remind dd-mm-yyyy HH:MM "Your Message" [repeat]
```

- **`dd-mm-yyyy`**: Date (e.g., `15-03-2025`).
- **`HH:MM`**: Time (e.g., `09:00`).
- **`"Your Message"`**: Reminder text (in quotes).
- **`[repeat]`**: Optional repeat interval.

**Examples**:
| Type               | Command Example                                                                 |
|--------------------|---------------------------------------------------------------------------------|
| One-Time           | `/remind 15-03-2025 09:00 "Submit tax form"`                                   |
| Daily              | `/remind 15-03-2025 07:00 "Morning jog" daily`                                 |
| Weekly             | `/remind 15-03-2025 10:00 "Team meeting" weekly`                               |
| Monthly            | `/remind 15-03-2025 18:00 "Pay rent" monthly`                                  |
| Quarterly          | `/remind 15-03-2025 11:00 "Quarterly report" quarterly`                        |
| Half-Yearly        | `/remind 15-03-2025 12:00 "Dentist checkup" half-yearly`                       |
| Yearly             | `/remind 15-03-2025 08:00 "Anniversary celebration" yearly`                   |

**Response**:
```
Reminder set for 15-03-2025 09:00!
```

---

### `/list`
View all active reminders.

**Syntax**:
```
/list
```

**Response**:
```
Your active reminders:
1. 15-03-2025 09:00: Submit tax form (Repeat: No)
2. 15-03-2025 07:00: Morning jog (Repeat: daily)
```

---

### `/expired`
View expired (completed) reminders.

**Syntax**:
```
/expired
```

**Response**:
```
Your expired reminders:
1. 15-03-2024 09:00: Submit tax form
```

---

## Use Cases

### 🏠 **Personal**
- **Daily**: `"Take medication"`, `"Water plants"`
- **Yearly**: `"Birthday reminders"`, `"Insurance renewal"`

### 💼 **Work**
- **Weekly**: `"Team sync-up"`, `"Timesheet submission"`
- **Quarterly**: `"Business reviews"`, `"Client reports"`

### 🎉 **Events**
- **Monthly**: `"Pay rent"`, `"Book club meeting"`
- **Half-Yearly**: `"Car service"`, `"Medical checkup"`

---

## Hosting Guide

### Prerequisites
- Python 3.7+
- Telegram bot token from [BotFather](https://t.me/BotFather)

### Steps
1. **Clone Repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/telegram-reminder-bot.git
   cd telegram-reminder-bot
   ```

2. **Install Dependencies**:
   ```bash
   pip install python-telegram-bot
   ```

3. **Set Environment Variable**:
   ```bash
   export YOUR_API_TOKEN="YOUR_BOT_TOKEN"  # Linux/macOS
   set YOUR_API_TOKEN=YOUR_BOT_TOKEN       # Windows
   ```

4. **Run Locally**:
   ```bash
   python3 bot.py
   ```

### Free Hosting Options
| Platform       | Guide                                                                         |
|----------------|-------------------------------------------------------------------------------|
| **Render**     | [Deploy on Render](https://render.com/docs/deploy-telegram-bot)               |
| **Fly.io**     | [Fly.io Deployment](https://fly.io/docs/apps/launch/)                         |

---

## Contributing
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/new-feature`.
3. Commit changes: `git commit -m "Add new feature"`.
4. Push to the branch: `git push origin feature/new-feature`.
5. Open a pull request.

---

## License
Distributed under the MIT License. See [LICENSE](LICENSE) for details.
