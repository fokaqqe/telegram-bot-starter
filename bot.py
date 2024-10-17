import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.ext import ConversationHandler

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
NAME, CLEAR_QUEUE = range(2)

# Глобальная переменная для хранения пользователей
queue = []
secret_code = '2015'  # Замените вашим особым кодом

# Команда /start
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user.full_name
    welcome_message = f"Привет, {user}! Я бот, который поможет с регистрацией пользователей.\n\n" \
                      "Вот список команд, которые я понимаю:\n" \
                      "/register - зарегистрировать себя\n" \
                      "/queue - посмотреть текущую очередь"
    update.message.reply_text(welcome_message, reply_markup=ForceReply(selective=True))

# Команда /register
def register(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Пожалуйста, введите ваше имя:")
    return NAME

# Обработка имени пользователя
def get_name(update: Update, context: CallbackContext) -> int:
    user_name = update.message.text.strip()
    queue.append(user_name)
    update.message.reply_text(f"Вы успешно зарегистрированы как {user_name}!")

    # Проверяем длину очереди и добавляем пользователя "подход по второму кругу"
    if len(queue) % 3 == 0:
        queue.append("подход по второму кругу")
        update.message.reply_text("Добавлен пользователь 'подход по второму кругу' в очередь.")

    return ConversationHandler.END

# Команда /clear_queue
def clear_queue(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1 or context.args[0] != secret_code:
        update.message.reply_text("Неверный код. Очередь не очищена.")
        return

    queue.clear()
    update.message.reply_text("Очередь успешно очищена.")

# Команда /queue
def show_queue(update: Update, context: CallbackContext) -> None:
    if queue:
        update.message.reply_text("Текущая очередь: " + ", ".join(queue))
    else:
        update.message.reply_text("Очередь пуста.")

# Обработка ошибок
def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update {update} caused error {context.error}')

def main() -> None:
    """Запускаем бота."""
    updater = Updater("7074843158:AAE64r9PhjmWiwZCrzPAZFbv1itQCGsTtH4")  # Замените вашим токеном

    dispatcher = updater.dispatcher

    # Определяем обработчики
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', register)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
        },
        fallbacks=[],
    )

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("clear_queue", clear_queue))
    dispatcher.add_handler(CommandHandler("queue", show_queue))
    
    # Логирование ошибок
    dispatcher.add_error_handler(error)

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
