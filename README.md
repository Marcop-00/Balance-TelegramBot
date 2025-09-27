# Balance-TelegramBot

A simple Telegram bot to manage and track group balances (e.g., for shared Spotify subscriptions) using Python.
This bot is designed for all the friends who end up paying subscriptions for others.
Instead of manually keeping track of everyone’s balances, the bot automatically manages payments, updates reports, and reminds the group when it’s time to settle up.
You can also add and remove users easily.

(Yes, I built it because I was that friend too!)

## Features
- Add a fixed amount to all users automatically every month
- Subtract payments from individual users
- Show the balance for a single user or all users
- Add or delete users
- Uses a JSON file for persistent storage

## Setup

1. **Clone the repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Update the following global variables as you need in `python_telegram_bot.py`**
   ```python
   TOKEN=your_telegram_bot_token
   GROUP_ID=your_group_id
   IMPORT = 3.50
   CURRENCY = "$"
   DAY = your_payday
   ```

4. **Create a `balances.json` file** (or use the provided one) with the initial balances, e.g.:
   ```json
   {
     "Alice": 0,
     "Bob": 0,
     "Charlie": 0
   }
   ```

5. **Run the bot**
   ```bash
   python3 python_telegram_bot.py
   ```

## Commands
- /add_amount <name> <amount> - Add an amount to a user
- /subtract_amount <name> <amount> - Subtract an amount from a user
- /balance <name> - Show the balance for a user
- /all_balances - Show all balances
- /add_user <name> [initial_balance] - Add a new user
- /remove_user <name> - Remove a user
- /help - Show this help message

## Notes
- The bot will automatically add the import to all users on the payday that you specified each month.
- Make sure the bot is an admin in your group to send messages.
- **Hosting**: You need to run it on a Raspberry Pi or on a hosting service to keep it online.
- If you want to contribute, I'll be glad to consider your improvements!
---

Made with ❤️ by Marcop-00
