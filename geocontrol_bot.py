# Импортируем необходимые классы.
import logging
from telegram import ForceReply, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from datetime import datetime
from config import BOT_TOKEN
from db_connection import *

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def build_keyboard():
    #reply_keyboard = [["Man", "Woman", "Child"]]
    #return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="You status?")
    return ReplyKeyboardMarkup([[KeyboardButton("Сообщить местоположение", request_location = True)]], one_time_keyboard=True)


def get_db_user(update):
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM Users WHERE chat_id = ?', (update.message.chat.id,)).fetchall()
    result = next(iter(users), None)

    if not result:
        conn.execute('INSERT INTO Users (chat_id, name) VALUES (?, ?)', (update.message.chat.id, update.effective_user.full_name)).fetchall()
        conn.commit()
        result = conn.execute('SELECT * FROM Users WHERE chat_id = ?', (update.message.chat.id,)).fetchall()[0]

    return result


# Определяем функцию-обработчик сообщений.
# У неё два параметра, updater, принявший сообщение и контекст - дополнительная информация о сообщении.
async def process(update, context):
    # У объекта класса Updater есть поле message,
    # являющееся объектом сообщения.
    # У message есть поле text, содержащее текст полученного сообщения,
    # а также метод reply_text(str),
    # отсылающий ответ пользователю, от которого получено сообщение.
    db_user = get_db_user(update)

    # Если получили информацию о местоположении:
    location = update.message.location
    if location:
        conn = get_db_connection()
        conn.execute('INSERT INTO Locations (id_user, datetime, location, office_distance) VALUES (?, ?, ?, 500)', # id_office
            (db_user['id'], datetime.now(), '{} {} {}'.format(location.latitude, location.longitude, location.horizontal_accuracy if location.horizontal_accuracy else 0))).fetchall()
        conn.commit()
        await update.message.reply_text("{}, Ваше местоположение учтено! ({})".format(db_user['name'], location)) # Location(latitude=55.563644, longitude=37.569185)
        return

    # Если получили телефон:
    contact = update.message.contact
    if contact:
        conn = get_db_connection()
        conn.execute('UPDATE users SET phone = ? WHERE id = ?', (contact.phone_number, db_user['id'])).fetchall()
        conn.commit()
        db_user = get_db_user(update)

    if not db_user['phone']:
        await update.message.reply_text("Здравствуйте, {}! Я бот GeoControl. Пожалуйста, авторизуйтесь с помощью кнопки ниже:".format(db_user['name']),
                  reply_markup = ReplyKeyboardMarkup([[KeyboardButton("Войти в систему", request_contact = True)]], one_time_keyboard=True))
        return

    await update.message.reply_text("Здравствуйте, {}! Я бот GeoControl. Пожалуйста, сообщите свое местоположение по кнопке ниже:".format(db_user['name']), reply_markup = build_keyboard())
    #await update.message.reply_text("Привет, db_user[name]={}, db_user[chat_id]={}, я бот geocontrol. Твое echo: {}".format(db_user['name'], db_user['chat_id'], update.message.text), reply_markup = build_keyboard())


def main():
    # Создаём объект Application.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    application = Application.builder().token(BOT_TOKEN).build()

    # Создаём обработчик сообщений типа filters.TEXT
    # из описанной выше асинхронной функции echo()
    # После регистрации обработчика в приложении
    # эта асинхронная функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, process)

    # Регистрируем обработчик в приложении.
    application.add_handler(text_handler)
    application.add_handler(CommandHandler("start", process))
    application.add_handler(MessageHandler(filters.LOCATION, process))
    application.add_handler(MessageHandler(filters.CONTACT, process))

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()