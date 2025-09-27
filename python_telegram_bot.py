import asyncio
import json
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import datetime

TOKEN = "Your-Telegram-bot-token" # insert here the telegram bot token
GROUP_ID = -1234567890 # insert here the telegram group_id
IMPORT = 3.50 # insert here the import
CURRENCY = "$" # insert here the currency
DAY = 1 # insert here your payday

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Unknown command. Please use /add_user, /remove_user, /subtract_amount, /add_amount, /balance, /all_balances.")

# add user -----------------------------------------------------
def add_user(name, initial_balance=0.0):
    with open("balances.json", "r") as f:
        balances = json.load(f)
    if name in balances:
        return False, balances[name]
    balances[name] = round(initial_balance, 2)
    with open("balances.json", "w") as f:
        json.dump(balances, f, indent=2)
    return True, balances[name]

async def add_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) not in [1, 2]:
        await update.message.reply_text("Usage: /adduser <name> [initial_balance]")
        return
    name = context.args[0]
    initial_balance = 0.0
    if len(context.args) == 2:
        try:
            initial_balance = float(context.args[1].replace(",", "."))
        except ValueError:
            await update.message.reply_text("Invalid initial balance.")
            return
    ok, balance = add_user(name, initial_balance)
    if ok:
        await update.message.reply_text(f"User '{name}' added with balance {balance}{CURRENCY}.")
    else:
        await update.message.reply_text(f"User '{name}' already exists with balance {balance}{CURRENCY}.")

# -----------------------------------------------------

# remove user --------------------------------------------
def remove_user(name):
    with open("balances.json", "r") as f:
        balances = json.load(f)
    if name not in balances:
        return False
    del balances[name]
    with open("balances.json", "w") as f:
        json.dump(balances, f, indent=2)
    return True

async def remove_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /removeuser <name>")
        return
    name = context.args[0]
    ok = remove_user(name)
    if ok:
        await update.message.reply_text(f"User '{name}' removed.")
    else:
        await update.message.reply_text(f"User '{name}' not found.")

# -----------------------------------------------------

# get all amounts -----------------------------------------
def get_all_balances():
    with open("balances.json", "r") as f:
        balances = json.load(f)
    return balances

async def all_balances_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balances = get_all_balances()
    lines = ["Current balances:"]
    for name, balance in balances.items():
        lines.append(f"{name}: {balance}{CURRENCY}")
    msg = "\n".join(lines)
    await update.message.reply_text(msg)

# -----------------------------------------


# get a user's amount -----------------------------------------
def get_user_balance(name):
    with open("balances.json", "r") as f:
        balances = json.load(f)
    return balances.get(name, None)

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /balance <name>")
        return
    name = context.args[0]
    balance = get_user_balance(name)
    if balance is not None:
        await update.message.reply_text(f"Balance for {name}: {balance}{CURRENCY}")
    else:
        await update.message.reply_text(f"Name '{name}' not found in the report.")
 
 # -----------------------------------------
 
 
 
 # add amount to a user -----------------------------------------
def add_to_user(name, amount):
    with open("balances.json", "r") as f:
        balances = json.load(f)
    if name in balances:
        balances[name] = round(balances[name] + amount, 2)
        with open("balances.json", "w") as f:
            json.dump(balances, f, indent=2)
        return True, balances[name]
    else:
        return False, None

async def add_amount_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /addamount <name> <amount>")
        return
    name = context.args[0]
    try:
        amount = float(context.args[1].replace(",", "."))
    except ValueError:
        await update.message.reply_text("Invalid amount.")
        return
    ok, new_balance = add_to_user(name, amount)
    if ok:
        await update.message.reply_text(f"{amount}{CURRENCY} added to {name}. New balance: {new_balance}")
    else:
        await update.message.reply_text(f"Name '{name}' not found in the report.")

# -----------------------------------------

# subtract amount for a user ----------------------------------
def subtract_from_user(name, amount):
    with open("balances.json", "r") as f:
        balances = json.load(f)
    if name in balances:
        balances[name] = round(balances[name] - amount, 2)
        with open("balances.json", "w") as f:
            json.dump(balances, f, indent=2)
        return True, balances[name]
    else:
        return False, None
   
async def subtract_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /subtract <name> <amount>")
        return
    name = context.args[0]
    try:
        amount = float(context.args[1].replace(",", "."))
    except ValueError:
        await update.message.reply_text("Invalid amount.")
        return
    ok, new_balance = subtract_from_user(name, amount)
    if ok:
        await update.message.reply_text(f"{amount}{CURRENCY} paid by {name}. New balance: {new_balance}")
    else:
        await update.message.reply_text(f"Name '{name}' not found in the report.")

# -------------------------------------------------------------


# automatic monthly report ---------------------------------------------
def generate_report():
    with open("balances.json", "r") as f:
        balances = json.load(f)
    lines = ["Updated report:"]
    for name, balance in balances.items():
        lines.append(f"{name}: {balance}")
    return "\n".join(lines)

def add_to_all(amount=IMPORT):
    with open("balances.json", "r") as f:
        balances = json.load(f)
    for name in balances:
        balances[name] = round(balances[name] + amount, 2)
    with open("balances.json", "w") as f:
        json.dump(balances, f, indent=2)
    return balances

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = generate_report()
    await update.message.reply_text(message)

async def send_message():
    bot = Bot(token=TOKEN)
    message = generate_report()
    await bot.send_message(chat_id=GROUP_ID, text=message)

async def automatic_task(app: Application):
    while True:
        today = datetime.datetime.now()
        if today.day == DAY:
            add_to_all(IMPORT)
            bot = Bot(token=TOKEN)
            message = generate_report()
            await bot.send_message(chat_id=GROUP_ID, text=(f"✨Hello, how are you?✨ \nThe subscription renews this month!💰 {IMPORT} {CURRENCY} added to everyone!\n") + message)
            await asyncio.sleep(60 * 60 * 12)
        else:
            await asyncio.sleep(60 * 60 * 12)

async def post_init(application: Application):
    application.create_task(automatic_task(application))
# -------------------------------------------------------------

# help command -------------------------------------------------------------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Available commands:\n"
        "/add_amount <name> <amount> - Add an amount to a user\n"
        "/subtract_amount <name> <amount> - Subtract an amount from a user\n"
        "/balance <name> - Show the balance for a user\n"
        "/all_balances - Show all balances\n"
        "/add_user <name> [initial_balance] - Add a new user\n"
        "/remove_user <name> - Remove a user\n"
        "/help - Show this help message\n"
    )
    await update.message.reply_text(help_text)
# -------------------------------------------------------------
    
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("add_amount", add_amount_command))
    app.add_handler(CommandHandler("subtract_amount", subtract_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("all_balances", all_balances_command))
    app.add_handler(CommandHandler("add_user", add_user_command))
    app.add_handler(CommandHandler("remove_user", remove_user_command))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.run_polling()
