import logging
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
NAME, CODE_FOR_CLEAR, CODE_FOR_ALL, MESSAGE_FOR_ALL = range(4)

# Глобальная переменная для хранения пользователей
queue = []
subscribers = set()  # Для отслеживания подписчиков на уведомления
secret_code = '2015'  # Замените вашим особым кодом
user_ids = set()  # Для отслеживания зарегистрированных пользователей

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user.full_name
    welcome_message = f"Привет, {user}! Я бот, который поможет тебе записаться в очередь к твоему любимому преподавателю.\n\n" \
                      "Вот список команд, которые я понимаю:\n" \
                      "/register - зарегистрировать себя\n" \
                      "/queue - посмотреть текущую очередь\n" \
                      "/subscribe - подписаться на уведомления (подпишись чтобы знать когда будет новая запись)\n" 
    await update.message.reply_text(welcome_message, reply_markup=ForceReply(selective=True))

# Команда /register
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if user_id in user_ids:
        await update.message.reply_text("Вы уже зарегистрированы в очереди.")
        return ConversationHandler.END

    await update.message.reply_text("Как вас записать?")
    return NAME

# Обработка имени пользователя
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_name = update.message.text.strip()
    user_id = update.effective_user.id
    user_ids.add(user_id)
    queue.append(user_name)
    await update.message.reply_text(f"Вы успешно зарегистрированы как {user_name}!")

    if len(queue) % 3 == 0:
        queue.append("--Подход по второму кругу--")

    return ConversationHandler.END

# Команда /clear
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Пожалуйста, введите код для очистки очереди:")
    return CODE_FOR_CLEAR

# Обработка кода для очистки
async def process_clear_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text.strip() != secret_code:
        await update.message.reply_text("Неверный код. Очередь не очищена.")
        return

    queue.clear()
    user_ids.clear()  # Очищаем список зарегистрированных пользователей
    await update.message.reply_text("Очередь успешно очищена.")
    
    # Уведомляем подписчиков о очистке очереди
    for subscriber_id in subscribers:
        await context.bot.send_message(chat_id=subscriber_id, text="Очередь была очищена!")

# Команда /queue
async def show_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if queue:
        await update.message.reply_text("Текущая очередь:\n" + "\n".join(queue))
    else:
        await update.message.reply_text("Очередь пуста.")

# Команда /subscribe
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id in subscribers:
        await update.message.reply_text("Вы уже подписаны на уведомления.")
    else:
        subscribers.add(user_id)
        await update.message.reply_text("Вы успешно подписались на уведомления.")

# Команда /unsubscribe
async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user_id = update.effective_user.id
    if user_id in subscribers:
        subscribers.remove(user_id)
        await update.message.reply_text("Вы успешно отписаны от уведомлений.")
    else:
        await update.message.reply_text("Вы не подписаны на уведомления.")

# Команда /all
async def all_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Пожалуйста, введите код для отправки сообщения всем подписчикам:")
    return CODE_FOR_ALL

# Обработка кода для команды all
async def process_all_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.strip() != secret_code:
        await update.message.reply_text("Неверный код. Сообщение не отправлено.")
        return ConversationHandler.END

    await update.message.reply_text("Введите сообщение, которое нужно отправить всем подписчикам:")
    return MESSAGE_FOR_ALL

# Обработчик сообщения для команды all
async def process_all_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.strip()
    for subscriber_id in subscribers:
        await context.bot.send_message(chat_id=subscriber_id, text=message_text)

    await update.message.reply_text("Сообщение успешно отправлено всем подписчикам.")

# Обработка ошибок
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning(f'Update {update} caused error {context.error}')

def main() -> None:
    """Запускаем бота."""
    application = ApplicationBuilder().token("7074843158:AAE64r9PhjmWiwZCrzPAZFbv1itQCGsTtH4").build()  # Замените вашим токеном

    # Определяем обработчики
    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('register', register),
            CommandHandler('clear', clear),
            CommandHandler('all', all_message)
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CODE_FOR_CLEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_clear_code)],
            CODE_FOR_ALL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_all_code)],
            MESSAGE_FOR_ALL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_all_message)],
        },
        fallbacks=[],
    )

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conversation_handler)
    application.add_handler(CommandHandler("queue", show_queue))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
