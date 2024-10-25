import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
NAME, CODE_FOR_CLEAR = range(2)

# Глобальная переменная для хранения пользователей
queue = []
subscribers = set()  # Для отслеживания подписчиков на уведомления
secret_code = '2015'  # Замените вашим особым кодом
user_ids = set()  # Для отслеживания зарегистрированных пользователей
user_names = {}  # Для хранения имен пользователей по их ID

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user.full_name
    welcome_message = f"Привет, {user}! Я бот, который поможет тебе записаться в очередь.\n\n" \
                      "Вот список команд, которые я понимаю:\n" \
                      "/register - зарегистрировать себя\n" \
                      "/queue - посмотреть текущую очередь\n" \
                      "/remove - удалить себя из очереди\n" \
                      "/subscribe - подписаться на уведомления\n"
    await update.message.reply_text(welcome_message)

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
    
    if len(user_name) > 15:
        await update.message.reply_text("Пожалуйста, введите имя короче 15 символов.")
        return NAME

    user_ids.add(user_id)
    queue.append(user_name)
    user_names[user_id] = user_name  # Сохраняем имя пользователя по ID
    await update.message.reply_text(f"Вы успешно зарегистрированы как {user_name}!")

    return ConversationHandler.END

# Команда /clear
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Пожалуйста, введите код для очистки очереди:")
    return CODE_FOR_CLEAR

# Обработка кода для очистки
async def process_clear_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.strip() != secret_code:
        await update.message.reply_text("Неверный код. Очередь не очищена.")
        return ConversationHandler.END

    queue.clear()
    user_ids.clear()  # Очищаем список зарегистрированных пользователей
    user_names.clear()  # Очищаем имена пользователей
    await update.message.reply_text("Очередь успешно очищена.")
    
    # Уведомляем подписчиков о очистке очереди
    for subscriber_id in subscribers:
        await context.bot.send_message(chat_id=subscriber_id, text="Открыта запись в новую очередь!")

    return ConversationHandler.END

# Команда /queue
async def show_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if queue:
        queue_output = ""
        for i in range(0, len(queue), 3):
            chunk = queue[i:i + 3]
            queue_output += "\n".join(chunk) + "\n\n--Подход по второму кругу--\n\n"
        queue_output = queue_output.rstrip("\n\n--Подход по второму кругу--\n\n")  # Убираем последний ненужный текст
        await update.message.reply_text(queue_output)
    else:
        await update.message.reply_text("Очередь пуста.")

# Глобальный обработчик ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Произошла ошибка при обработке обновления", exc_info=context.error)

# Основная функция запуска бота
def main():
    application = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()

    # Обработчики команд
 application.add_handler(CommandHandler("start", start))
    
    # ConversationHandler для регистрации
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        },
        fallbacks=[]
    ))

    # ConversationHandler для очистки
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("clear", clear)],
        states={
            CODE_FOR_CLEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_clear_code)],
        },
        fallbacks=[]
    ))

    application.add_handler(CommandHandler("queue", show_queue))

    # Обработчик ошибок
    application.add_error_handler(error_handler)

    application.run_polling()

if name == '__main__':
    main()
