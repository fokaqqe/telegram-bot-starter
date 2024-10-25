import logging
from telegram import Update
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
user_names = {}  # Для хранения имен пользователей по их ID

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user.full_name
    welcome_message = f"Привет, {user}! Я бот, который поможет тебе записаться в очередь.\n\n" \
                      "Вот список команд, которые я понимаю:\n" \
                      "/register - зарегистрировать себя\n" \
                      "/remove - удалить себя из очереди\n" \
                      "/queue - посмотреть текущую очередь\n\n" \
                      "/subscribe - подписаться на уведомления\n" \
                      "/unsubscribe - отписаться от уведомлений\n" 
    await update.message.reply_text(welcome_message)

# Команда /register
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
  #  if user_id in user_ids:
   #     await update.message.reply_text("Вы уже зарегистрированы в очереди.")
   #     return ConversationHandler.END

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
        queue_output = "Текущая очередь:\n\n"
        for i in range(0, len(queue), 3):
            chunk = queue[i:i + 3]
            queue_output += "\n".join(chunk) + "\n\n--Подход по второму кругу--\n\n"
        
        # Убираем только последний --Подход по второму кругу-- без удаления других символов
        queue_output = queue_output.rsplit("\n\n--Подход по второму кругу--\n\n", 1)[0]
        
        await update.message.reply_text(queue_output)
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
      
# Команда /remove
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id in user_ids:
        user_ids.remove(user_id)
        user_name = user_names.pop(user_id, None)  # Удаляем имя пользователя по ID
        if user_name and user_name in queue:
            queue.remove(user_name)  # Удаляем из очереди, если имя найдено
        await update.message.reply_text(f"Вы успешно удалены из очереди ({user_name}).")
    else:
        await update.message.reply_text("Вы не зарегистрированы в очереди.")      

# Команда /all
async def all_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Пожалуйста, введите код для отправки сообщения всем подписчикам:")
    return CODE_FOR_ALL

# Обработка кода для команды /all
async def process_all_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.strip() != secret_code:
        await update.message.reply_text("Неверный код. Сообщение не отправлено.")
        return ConversationHandler.END

    await update.message.reply_text("Введите сообщение, которое нужно отправить всем подписчикам:")
    return MESSAGE_FOR_ALL

# Обработка сообщения для команды /all
async def process_all_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.strip()
    for subscriber_id in subscribers:
        await context.bot.send_message(chat_id=subscriber_id, text=message_text)

    await update.message.reply_text("Сообщение успешно отправлено всем подписчикам.")
    return ConversationHandler.END

# Глобальный обработчик ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Произошла ошибка при обработке обновления", exc_info=context.error)

# Основная функция запуска бота
def main():
    application = ApplicationBuilder().token("7074843158:AAE64r9PhjmWiwZCrzPAZFbv1itQCGsTtH4").build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("remove", remove))
    
    # ConversationHandler для регистрации
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        },
        fallbacks=[]
    ))

    # ConversationHandler для очистки очереди
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("clear", clear)],
        states={
            CODE_FOR_CLEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_clear_code)],
        },
        fallbacks=[]
    ))

    # ConversationHandler для команды /all
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("all", all_message)],
        states={
            CODE_FOR_ALL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_all_code)],
            MESSAGE_FOR_ALL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_all_message)]
        },
        fallbacks=[]
    ))

    application.add_handler(CommandHandler("queue", show_queue))

    # Обработчик ошибок
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
