# Balance-TelegramBot

A simple Telegram bot to manage and track group balances (e.g., for shared Spotify subscriptions) using Python.
This bot is designed for all the friends who end up paying subscriptions for others.
Instead of manually keeping track of everyone’s balances, the bot automatically manages payments, updates reports, and reminds the group when it’s time to settle up.
You can also add and remove users easily.

(Yes, I built it because I was that friend too!)

## Features

- 💰 **Balance Management**: Add and subtract limits/funds for users.
- 📅 **Automated Monthly Updates**: Automatically adds a configured amount (e.g., subscription fee) to every user on a specific day of the month.
- 🔒 **Secure Access**: Admin-only commands protected by chat role validation.
- 🇬🇧 **English Language**: All responses and logs are in English.
- 🐳 **Docker Ready**: (Optional) Can be easily containerized.

## Prerequisites

- Python 3.9+
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- A Telegram Group ID (to send automatic reports)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YourUsername/Balance-TelegramBot.git
    cd Balance-TelegramBot
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Configuration:**
    Copy the example environment file and configure it.
    ```bash
    cp .env.example .env
    ```
    Open `.env` and fill in your details:
    - `TELEGRAM_TOKEN`: Your API Token from BotFather.
    - `GROUP_ID`: The numeric ID of the Telegram group where reports will be posted.
    - `DEFAULT_IMPORT_AMOUNT`: The amount to add automatically every month (e.g., 3.50).
    - `CURRENCY`: The currency symbol (e.g., $, €, £).
    - `PAYDAY_DAY`: The day of the month (1-28) to run the automatic update.

4.  **Run the bot:**
    ```bash
    python main.py
    ```

## Usage

### Public Commands
These commands can be used by anyone in the chat.
- `/balance <name>`: Show the current balance for a specific user.
- `/all_balances`: Show balances for all registered users.
- `/help`: Show available commands.

### Admin Commands
Restricted to Group Admins and the Creator.
- `/add_user <name> [initial_balance]`: Register a new user to the system.
- `/remove_user <name>`: Remove a user.
- `/add_amount <name> <amount>`: Add funds to a user's balance.
- `/subtract_amount <name> <amount>`: Deduct funds from a user's balance.

## Data Storage
User balances are stored in a local `balances.json` file. This is simple and effective for small groups.

## License
MIT
Made with ❤️ by Marcop-00