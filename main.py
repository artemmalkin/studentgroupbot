import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, ConversationHandler
from config import TELEGRAM_TOKEN
import db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Определение состояний для машины состояний ConversationHandler
START_CREATE_GROUP, START_JOIN_GROUP, ENTER_NEW_GROUP_NAME, ENTER_NEW_GROUP_PASSWORD, ENTER_GROUP_PASSWORD, ENTER_STUDENT_NAME = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправка стартового сообщения и кнопок для создания или вступления в группу."""
    keyboard_new_user = [
        [
            InlineKeyboardButton("Создать группу", callback_data="create_group"),
            InlineKeyboardButton("Вступить в группу", callback_data="join_group"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard_new_user)
    await update.message.reply_text("Привет! Я ваш учебный бот. Чем могу помочь?", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "create_group":
        await query.edit_message_text(text="Введите название группы:")
        return START_CREATE_GROUP
    elif query.data == "join_group":
        await query.edit_message_text(text="Введите ID группы:")
        return START_JOIN_GROUP

async def enter_new_group_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняем название группы и просим ввести пароль группы."""
    context.user_data['group_name'] = update.message.text
    await update.message.reply_text("Введите пароль группы:")
    return ENTER_NEW_GROUP_PASSWORD

async def enter_new_group_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создаем группу в базе данных и завершаем создание группы."""
    group_name = context.user_data['group_name']
    group_password = update.message.text
    group_id = db.add_group(group_name, group_password)
    await update.message.reply_text(f"Группа '{group_name}' создана с ID {group_id}")
    return ConversationHandler.END

async def enter_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получаем ID группы и переходим к запросу пароля группы."""
    context.user_data['group_id'] = int(update.message.text)
    await update.message.reply_text("Введите пароль:")
    return ENTER_GROUP_PASSWORD

async def enter_group_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получаем пароль группы и переходим к запросу имени студента."""
    context.user_data['group_password'] = update.message.text
    group = db.get_group_by_id(context.user_data['group_id'])
    print(group)
    if group[2] == context.user_data['group_password']:
        await update.message.reply_text("Фамилия Имя:")
        return ENTER_STUDENT_NAME
    else:
        await update.message.reply_text("Неверный пароль. Отмена операции.")
        return ConversationHandler.END

async def enter_student_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавляем студента в группу и завершаем процесс вступления."""
    student_name = update.message.text
    group_id = context.user_data['group_id']
    db.add_student(student_name, group_id, "student")
    await update.message.reply_text(f"{student_name}, вы успешно вступили в группу '{db.get_group_by_id(group_id)[1]}'.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена текущего диалога."""
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

if __name__ == '__main__':
    # Подключение к базе данных
    db.drop_tables()
    db.create_tables_if_not_exists()

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Определение обработчиков для действий
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
        states={
            START_CREATE_GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_new_group_name)],
            ENTER_NEW_GROUP_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_new_group_password)],
            START_JOIN_GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_group_id)],
            ENTER_GROUP_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_group_password)],
            ENTER_STUDENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_student_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Обработчики команд
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.add_handler(conv_handler)

    # Запуск бота
    application.run_polling()
