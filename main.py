import os
import json
import logging
import asyncio
import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.constants import ChatMemberStatus

# Load environment variables
load_dotenv()

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Constants and Configuration
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
DEFAULT_IMPORT_AMOUNT = os.getenv("DEFAULT_IMPORT_AMOUNT")
CURRENCY = os.getenv("CURRENCY", "$")
PAYDAY_DAY = os.getenv("PAYDAY_DAY")

# Validation
if not all([TOKEN, GROUP_ID, DEFAULT_IMPORT_AMOUNT, PAYDAY_DAY]):
    logger.error("Missing environment variables. Please check your .env file.")
    exit(1)

try:
    GROUP_ID = int(GROUP_ID)
    DEFAULT_IMPORT_AMOUNT = float(DEFAULT_IMPORT_AMOUNT)
    PAYDAY_DAY = int(PAYDAY_DAY)
except ValueError:
    logger.error("Invalid format for environment variables.")
    exit(1)

BALANCES_FILE = "balances.json"

# --- Utils ---

def load_balances():
    try:
        if not os.path.exists(BALANCES_FILE):
            return {}
        with open(BALANCES_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading balances: {e}")
        return {}

def save_balances(balances):
    try:
        with open(BALANCES_FILE, "w") as f:
            json.dump(balances, f, indent=2)
        return True
    except IOError as e:
        logger.error(f"Error saving balances: {e}")
        return False

# --- Decorators ---

def restricted(func):
    """Restricts access to administrators and the group creator."""
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id # Should ideally be the group ID, but we check permissions in the current chat
        
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                await update.message.reply_text("⛔ Permission denied. Admins only.")
                return
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            # Identify if it's a private chat, get_chat_member might fail if bot is not in group or passed private chat_id
            # For simplicity, if we carry on commands in the group context, this works.
            # If commands are DM'd to bot, checking 'GROUP_ID' membership is safer.
            try:
                 member = await context.bot.get_chat_member(GROUP_ID, user_id)
                 if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                    await update.message.reply_text("⛔ Permission denied. Admins only.")
                    return
            except Exception:
                await update.message.reply_text("Error verifying permissions.")
                return

        return await func(update, context, *args, **kwargs)
    return wrapped

# --- Commands ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I am the Balance Bot. Use /help to see available commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📋 **Available Commands:**\n\n"
        "🟢 **Public:**\n"
        "/balance <name> - Show a user's balance\n"
        "/all_balances - Show limits for all users\n"
        "/help - Show this message\n\n"
        "🔒 **Admin Only:**\n"
        "/add_user <name> [initial_balance] - Register a new user\n"
        "/remove_user <name> - Remove a user\n"
        "/add_amount <name> <amount> - Add funds to a user\n"
        "/subtract_amount <name> <amount> - Deduct funds from a user\n"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Unknown command. Try /help.")

# --- Public Commands ---

async def all_balances_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balances = load_balances()
    if not balances:
        await update.message.reply_text("📭 No balances found.")
        return

    lines = ["📊 **Current Balances:**"]
    for name, balance in balances.items():
        lines.append(f"👤 {name}: {balance} {CURRENCY}")
    
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /balance <name>")
        return
    
    name = context.args[0]
    balances = load_balances()
    balance = balances.get(name)
    
    if balance is not None:
        await update.message.reply_text(f"💰 Balance for **{name}**: {balance} {CURRENCY}", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ User '{name}' not found.")

# --- Admin Commands ---

@restricted
async def add_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /add_user <name> [initial_balance]")
        return
    
    name = context.args[0]
    initial_balance = 0.0
    
    if len(context.args) >= 2:
        try:
            initial_balance = float(context.args[1].replace(",", "."))
        except ValueError:
            await update.message.reply_text("❌ Invalid amount format.")
            return

    balances = load_balances()
    if name in balances:
        await update.message.reply_text(f"⚠️ User '{name}' already exists. Balance: {balances[name]} {CURRENCY}")
        return

    balances[name] = round(initial_balance, 2)
    if save_balances(balances):
        await update.message.reply_text(f"✅ User '{name}' added with {initial_balance} {CURRENCY}.")
    else:
        await update.message.reply_text("❌ Error saving data.")

@restricted
async def remove_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /remove_user <name>")
        return
    
    name = context.args[0]
    balances = load_balances()
    
    if name in balances:
        del balances[name]
        if save_balances(balances):
            await update.message.reply_text(f"🗑️ User '{name}' removed.")
        else:
            await update.message.reply_text("❌ Error saving data.")
    else:
        await update.message.reply_text(f"❌ User '{name}' not found.")

@restricted
async def add_amount_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add_amount <name> <amount>")
        return
    
    name = context.args[0]
    try:
        amount = float(context.args[1].replace(",", "."))
    except ValueError:
        await update.message.reply_text("❌ Invalid amount format.")
        return

    balances = load_balances()
    if name in balances:
        balances[name] = round(balances[name] + amount, 2)
        if save_balances(balances):
            await update.message.reply_text(f"📈 Added {amount} {CURRENCY} to {name}. New balance: {balances[name]} {CURRENCY}")
        else:
            await update.message.reply_text("❌ Error saving data.")
    else:
        await update.message.reply_text(f"❌ User '{name}' not found.")

@restricted
async def subtract_amount_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /subtract_amount <name> <amount>")
        return
    
    name = context.args[0]
    try:
        amount = float(context.args[1].replace(",", "."))
    except ValueError:
        await update.message.reply_text("❌ Invalid amount format.")
        return

    balances = load_balances()
    if name in balances:
        balances[name] = round(balances[name] - amount, 2)
        if save_balances(balances):
            await update.message.reply_text(f"📉 Deducted {amount} {CURRENCY} from {name}. New balance: {balances[name]} {CURRENCY}")
        else:
            await update.message.reply_text("❌ Error saving data.")
    else:
        await update.message.reply_text(f"❌ User '{name}' not found.")

# --- Background Task ---

async def monthly_subscription_task(application: Application):
    """
    Checks automatically if it's the payday to add the default import.
    Runs every hour to check the date. ensure it only runs once per month by checking hour.
    """
    while True:
        now = datetime.datetime.now()
        
        # Check if it is the payday and 8 AM (to avoid double execution and respect timezone roughly)
        if now.day == PAYDAY_DAY and now.hour == 8:
            logger.info("Executing monthly subscription update...")
            
            balances = load_balances()
            if balances:
                changes = False
                for name in balances:
                    balances[name] = round(balances[name] + DEFAULT_IMPORT_AMOUNT, 2)
                    changes = True
                
                if changes and save_balances(balances):
                    # Prepare report
                    lines = [f"✨ **Monthly Subscription Update** ✨",  f"💰 Added {DEFAULT_IMPORT_AMOUNT} {CURRENCY} to everyone!\n"]
                    lines.append("📊 **Current Balances:**")
                    for name, balance in balances.items():
                        lines.append(f"{name}: {balance} {CURRENCY}")
                    
                    message = "\n".join(lines)
                    
                    try:
                        await application.bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")
                        logger.info("Monthly update message sent.")
                    except Exception as e:
                        logger.error(f"Failed to send monthly update message: {e}")
            
            # Sleep for 20 hours to ensure we don't run again today
            await asyncio.sleep(20 * 60 * 60)
            
        else:
            # Check again in 1 hour
            await asyncio.sleep(60 * 60)

async def post_init(application: Application):
    asyncio.create_task(monthly_subscription_task(application))

# --- Main ---

def main():
    logger.info("Starting Balance Bot...")
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    # Public
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("all_balances", all_balances_command))

    # Restricted
    app.add_handler(CommandHandler("add_user", add_user_command))
    app.add_handler(CommandHandler("remove_user", remove_user_command))
    app.add_handler(CommandHandler("add_amount", add_amount_command))
    app.add_handler(CommandHandler("subtract_amount", subtract_amount_command))

    # Unknown
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    app.run_polling()

if __name__ == "__main__":
    main()
