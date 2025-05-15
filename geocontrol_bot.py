# Импортируем необходимые классы.
import logging
from telegram import ForceReply, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from datetime import datetime
from config import BOT_TOKEN
from db_connection import *
from functions import *

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
        user_location = '{} {}'.format(location.latitude, location.longitude)
        await update.message.reply_text("{}, Ваше местоположение учтено! ({})".format(db_user['name'], user_location)) # Location(latitude=55.563644, longitude=37.569185)

        conn = get_db_connection()

        # определим расстояние до каждого из офисов и выберем ближайший:
        distances = []
        offices = conn.execute('SELECT * FROM Offices').fetchall()
        for office in offices:
            try:
                #distance = calculate_distance(office['location'], user_location)
                lat1, lon1 = map(float, office['location'].split())
                lat2, lon2 = map(float, user_location.split()[:2])
                distance_m = int(haversine(lat1, lon1, lat2, lon2))
                distances.append({'id_office': office['id'], 'office_name': office['name'], 'distance_m': distance_m})
            except:
                pass

            distances = sorted(distances, key=lambda x: x['distance_m'])
        #await update.message.reply_text("distances: {}".format(distances))

        distance = distances[0] # Ближе всего
        await update.message.reply_text('Вы находитесь в {} метрах от офиса "{}"'.format(distance['distance_m'], distance['office_name']))

        conn.execute('INSERT INTO Locations (id_user, datetime, location, office_distance, id_office) VALUES (?, ?, ?, ?, ?)', # id_office
            (db_user['id'], datetime.now(), user_location, distance['distance_m'], distance['id_office'])).fetchall()
        conn.commit()

    # Если получили телефон:
    contact = update.message.contact
    if contact:
        conn = get_db_connection()
        conn.execute('UPDATE users SET phone = ? WHERE id = ?', (contact.phone_number, db_user['id'])).fetchall()
        conn.commit()
        db_user = get_db_user(update)
        await update.message.reply_text("Спасибо, Вы вошли в систему под номером телефона: {}".format(contact.phone_number))

    if not db_user['phone']:
        await update.message.reply_text("Здравствуйте, {}! Я бот GeoControl. Пожалуйста, авторизуйтесь с помощью кнопки ниже:".format(db_user['name']),
                  reply_markup = ReplyKeyboardMarkup([[KeyboardButton("Войти в систему", request_contact = True)]], one_time_keyboard=True))
    elif not location:
        await update.message.reply_text("На связи бот GeoControl! {}, пожалуйста, сообщите свое местоположение по кнопке ниже:".format(db_user['name']), reply_markup = build_keyboard())
    #await update.message.reply_text("Привет, db_user[name]={}, db_user[chat_id]={}, я бот geocontrol. Твое echo: {}".format(db_user['name'], db_user['chat_id'], update.message.text), reply_markup = build_keyboard())

    # скачать аватарку:
    if not db_user['avatar']:
        res = await update.effective_user.get_profile_photos(limit=1)
        if int(res.total_count) > 0:
            photo = res.photos[0][-1]
            photo_file = await photo.get_file()
            avatar = db_user['chat_id']+photo_file.file_path.split('/')[-1].split('.')[-1]
            await photo_file.download_to_drive('static/avatars/'+avatar)

            conn = get_db_connection()
            conn.execute('UPDATE users SET avatar = ? WHERE id = ?', (avatar, db_user['id'])).fetchall()
            conn.commit()

            #await photo_file.download_to_drive()
            #await update.effective_user.send_photo(photo.file_id) # отправляет фото в чат с пользователем
            #await update.message.reply_text("photo.file_id: {}, photo_file.file_path={}, custom_path".format(photo.file_id, photo_file.file_path, custom_path))


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