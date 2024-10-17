import logging
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
NAME = range(1)

# Глобальная переменная для хранения пользователей
queue = []
secret_code = '2015'  # Замените вашим особым кодом
user_ids = set()  # Для отслеживания зарегистрированных пользователей

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user.full_name
    welcome_message = f"Привет, {user}! Я бот, который поможет с регистрацией пользователей.\n\n" \
                      "Вот список команд, которые я понимаю:\n" \
                      "/register - зарегистрировать себя\n" \
                      "/queue - посмотреть текущую очередь\n" \
                      "/notify - уведомить всех пользователей о новой очереди"
    await update.message.reply_text(welcome_message, reply_markup=ForceReply(selective=True))

# Команда /register
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if user_id in user_ids:
        await update.message.reply_text("Вы уже зарегистрированы в очереди.")
        return ConversationHandler.END

    await update.message.reply_text("Пожалуйста, введите ваше имя:")
    return NAME

# Обработка имени пользователя
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_name = update.message.text.strip()
    user_id = update.effective_user.id
    user_ids.add(user_id)
    queue.append(user_name)
    await update.message.reply_text(f"Вы успешно зарегистрированы как {user_name}!")

    # Проверяем длину очереди и добавляем пользователя "подход по второму кругу"
    if len(queue) % 3 == 0:
        queue.append("подход по второму кругу")

    return ConversationHandler.END

# Команда /clear_queue
async def clear_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1 or context.args[0] != secret_code:
        await update.message.reply_text("Неверный код. Очередь не очищена.")
        return

    queue.clear()
    user_ids.clear()  # Очищаем список зарегистрированных пользователей
    await update.message.reply_text("Очередь успешно очищена.")

# Команда /queue
async def show_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if queue:
        await update.message.reply_text("Текущая очередь:\n" + "\n".join(queue))
    else:
        await update.message.reply_text("Очередь пуста.")

# Команда /notify
async def notify_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1 or context.args[0] != secret_code:
        await update.message.reply_text("Неверный код. Уведомление не отправлено.")
        return

    notify_message = "Запись в новую очередь открыта!"
    for user_id in user_ids:
        await context.bot.send_message(chat_id=user_id, text=notify_message)

    await update.message.reply_text("Уведомление отправлено всем пользователям.")

# Обработка ошибок
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning(f'Update {update} caused error {context.error}')

def main() -> None:
    """Запускаем бота."""
    application = ApplicationBuilder().token("7074843158:AAE64r9PhjmWiwZCrzPAZFbv1itQCGsTtH4").build()  # Замените вашим токеном

    # Определяем обработчики
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', register)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        },
        fallbacks=[],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    application.add_handler(CommandHandler("clear_queue", clear_queue))
    application.add_handler(CommandHandler("queue", show_queue))
    application.add_handler(CommandHandler("notify", notify_users))

    # Логирование ошибок
    application.add_error_handler(error)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
