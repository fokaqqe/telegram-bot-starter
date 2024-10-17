"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
from dotenv import load_dotenv
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# This will hold our queue of users
users_queue = []
priority_users = []

# Define a few command handlers. These usually take the two arguments update and context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_html(
        "Добро пожаловать в электронную очередь! Используйте команду /register для регистрации.",
        reply_markup=ForceReply(selective=True),
    )


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Register user in the queue."""
    if context.args:
        name = ' '.join(context.args)
        users_queue.append(name)
        await update.message.reply_text(f"{name} успешно зарегистрирован в очереди!")
    else:
        await update.message.reply_text("Пожалуйста, укажите ваше имя.")


async def check_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check the current users in the queue."""
    if users_queue:
        queue_status = '\n'.join(users_queue)
        await update.message.reply_text(f"Текущие записавшиеся в очередь:\n{queue_status}")
    else:
        await update.message.reply_text("В очереди пока никого нет.")


async def position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check user's position in the queue."""
    if context.args:
        user_name = ' '.join(context.args)
        if user_name in users_queue:
            position = users_queue.index(user_name) + 1
            await update.message.reply_text(f"{user_name}, ваша позиция в очереди: {position}.")
        else:
            await update.message.reply_text("Вы не зарегистрированы в очереди.")
    else:
        await update.message.reply_text("Пожалуйста, укажите ваше имя для проверки позиции.")


def main() -> None:
    """Start the bot."""
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_TOKEN")  # Убедитесь, что вы установили переменную окружения TELEGRAM_TOKEN

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("check_queue", check_queue))
    application.add_handler(CommandHandler("position", position))

    application.run_polling()


if __name__ == '__main__':
    main()
