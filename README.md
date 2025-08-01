# GeoControl

# Описание проекта
Telegram бот для учета рабочего времени сотрудников с веб-кабинетом администратора. Система позволяет:
* Регистрировать сотрудников через Telegram
* Фиксировать время прихода/ухода по геолокации
* Проверять соответствие местоположения офисным помещениям
* Предоставлять администратору доступ к статистике через веб-интерфейс

# Основные функции

## Для сотрудников (Telegram бот):

* Регистрация аккаунта (никнейм, телефон, аватар)
* Отправка геолокации при приходе на работу
* Отправка геолокации при уходе с работы
* Автоматическая проверка местоположения через Yandex Geocoder API

## Для администратора (Веб-кабинет):

* Просмотр информации о сотрудниках (аватар, телефон, никнейм)
* Контроль последних 10 геолокаций каждого сотрудника
* Просмотр деталей геолокации (время, место, расстояние до офиса)
* HTTP-авторизация для доступа к кабинету

# Технологии

* **Backend**: Python (AIogram для бота, Flask для веб-кабинета)
* **База данных**: SQLite + SQLAlchemy (ORM)
* **Геокодирование**: Yandex Geocoder API
* **Frontend**: HTML (веб-интерфейс администратора)
* **Telegram API**: для взаимодействия с ботом

# Установка и запуск

## Требования
* Python 3.9+
* Учетная запись Telegram бота (@BotFather)
* API ключ Yandex Geocoder

# Использование

## Для сотрудников:
* Начать чат с ботом в Telegram
* Зарегистрироваться с помощью команды "/start"
* При приходе на работу отправить геолокацию через меню бота
* При уходе с работы снова отправить геолокацию

## Для администратора:
* Открыть веб-интерфейс по заданному адресу 
* Просматривать статистику сотрудников

## Учасники проекта 
* Парийская Екатерина - @Jannuaryy
* Белова Анна - @belova28
* Сотникова Маргарита - @RitaSot
