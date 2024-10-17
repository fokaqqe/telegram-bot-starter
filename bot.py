#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

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


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    load_dotenv()

 from telegram import Update
   from telegram.ext import Updater, CommandHandler, CallbackContext

   TOKEN = '7074843158:AAE64r9PhjmWiwZCrzPAZFbv1itQCGsTtH4'

   users_queue = []
   priority_users = []

   def start(update: Update, context: CallbackContext) -> None:
       update.message.reply_text("Добро пожаловать в электронную очередь! Используйте команду /register для регистрации.")

   def register(update: Update, context: CallbackContext) -> None:
       if context.args:
           name = ' '.join(context.args)
           users_queue.append(name)
           update.message.reply_text(f"{name} успешно зарегистрирован в очереди!")
       else:
           update.message.reply_text("Пожалуйста, укажите ваше имя.")

   def check_queue(update: Update, context: CallbackContext) -> None:
       if users_queue:
           queue_status = '\n'.join(users_queue)
           update.message.reply_text(f"Текущие записавшиеся в очередь:\n{queue_status}")
       else:
           update.message.reply_text("В очереди пока никого нет.")

   def position(update: Update, context: CallbackContext) -> None:
       user_name = update.message.text.split(" ", 1)[1]
       if user_name in users_queue:
           position = users_queue.index(user_name) + 1
           update.message.reply_text(f"{user_name}, ваша позиция в очереди: {position}.")
       else:
           update.message.reply_text("Вы не зарегистрированы в очереди.")

   def main():
       updater = Updater(TOKEN)
       dispatcher = updater.dispatcher

       dispatcher.add_handler(CommandHandler("start", start))
       dispatcher.add_handler(CommandHandler("register", register))
       dispatcher.add_handler(CommandHandler("check_queue", check_queue))
       dispatcher.add_handler(CommandHandler("position", position))

       updater.start_polling()
       updater.idle()

   if __name__ == '__main__':
       main()
   
