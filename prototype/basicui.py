from datetime import date
import sqlite3
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from eduparser import get_user_info
from sys import path
from buttons import *
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from re import fullmatch


path.append("..")
from backEnd.unteractiondb import (
    add_user,
    check_for_existence,
    get_user_city,
    add_booking,
    get_object_name,
    get_books_for_user,
    delete_record,
    get_user_role,
    get_user_username,
    delete_line_queue_departures,
)


path.pop()

TOKEN = "5334942029:AAHxi8bIGm8RYohC_mtQTWuc2j8IuQgojgM"
bot = TeleBot(TOKEN, "Markdown")

users_status = {}
database = "../backEnd/main.db"
table = "users"


def add_user_to_db(tg_id: int, user_info: dict):
    """Добавление пользователя в базу данных

    Args:
        tg_id (int): Telegram ID
        user_info (dict): Словарь данных для добавления
    """
    info = [
        tg_id,
        user_info.get("username"),
        user_info.get("role"),
        user_info.get("city"),
    ]
    add_user("tg_id", info)


@bot.message_handler(["restore_buttons"])
def handle_restore_buttons(message: Message):
    if get_user_role(message.from_user.id) == 999:
        rmarkup = ADMIN_MARKUP
    else:
        rmarkup = STUDENT_MARKUP
    bot.send_message(message.chat.id, "Кнопки восстановлены.", reply_markup=rmarkup)


@bot.message_handler(["start", "register"])
def handle_start(message: Message):
    """Обработка команды /start и команды /register

    Args:
        message (telebot.types.Message): Сообщение пользователя
    """
    # Приветственное сообщение
    hello_message = "Добро пожаловать в *BookBot21*!\n\nТут *Ты* сможешь забронировать нужный тебе *объект* кампуса _(переговорку, игровую, теннистый стол и т.д.)_ на нужное тебе время.\n\nДля начала необходимо *зарегистрировать* тебя в системе."
    bot.send_message(message.chat.id, hello_message)

    # Если id юзера в списке админов, то он уже зарегистрирован.
    # Иначе - необходим ввод пароля и логина от платформы.
    try:
        if check_for_existence(table, message.from_user.id, "tg_id"):
            bot.send_message(
                message.chat.id,
                "Для *Вас* регистрация не требуется.\n\nДобро пожаловать, *Администратор*.",
                reply_markup=ADMIN_MARKUP,
            )
        else:
            bot.send_message(message.chat.id, "Введи свой *логин* от платформы")
            users_status[str(message.from_user.id)] = {"status": "login"}
    except sqlite3.OperationalError:
        bot.send_message(message.chat.id, "Проблемы с базой данных.")


def handle_credentials(message: Message):
    """Обработка логина и пароля пользователя

    Args:
        message (telebot.types.Message): Сообщение пользователя
    """

    def write_login(message: Message):
        users_status[str(message.from_user.id)][
            "username"
        ] = message.text.strip().lower()
        users_status[str(message.from_user.id)]["status"] = "password"
        bot.send_message(message.chat.id, "Теперь введи свой *пароль* от платформы")

    def write_password(message: Message):
        username = users_status[str(message.from_user.id)]["username"]
        password = message.text
        check_msg = bot.send_message(message.chat.id, "Проверяю учётку на платформе...")
        try:
            user_info = get_user_info(username, password)
        except:
            bot.send_message(message.chat.id, "Произошла непредвиденная ошибка.")
            try:
                del users_status[str(message.from_user.id)]
            except KeyError:
                pass
        if not user_info:
            bot.edit_message_text(
                "Неверная пара *логин-пароль*. Попробуйте ещё раз.",
                message.chat.id,
                check_msg.id,
            )
        else:
            bot.send_message(
                message.chat.id,
                "Вы успешно зарегистрировались!\n\nТеперь вы можете забронировать объект школы, используя команду `/book` или соответствующую кнопку.",
                reply_markup=STUDENT_MARKUP,
            )

            # Отправляем инфу в базу данных
            try:
                add_user_to_db(message.from_user.id, user_info)
            except sqlite3.OperationalError:
                bot.edit_message_text(
                    "Не удалось добавить данные в базу.", message.chat.id, check_msg.id
                )
                print(user_info)

            # Удаляем из временного хранилища статус регистрации пользователя
            try:
                del users_status[str(message.from_user.id)]
            except KeyError:
                pass

    # Сама функция
    user_info = users_status.get(str(message.from_user.id))
    if user_info:
        user_status = user_info.get("status")
        if user_status == "login":
            write_login(message)
        elif user_status == "password":
            write_password(message)
        else:
            bot.send_message(message.chat.id, "Произошла неизвестная ошибка.")
            try:
                del users_status[str(message.from_user.id)]
            except KeyError:
                pass
    else:
        bot.send_message(message.chat.id, "Произошла неизвестная ошибка.")
        try:
            del users_status[str(message.from_user.id)]
        except KeyError:
            pass


@bot.message_handler(regexp="Забронировать")
def show_floors(message: Message):
    """Показать пользователю этажи для выбора

    Args:
        message (telebot.types.Message): Сообщение пользователя
    """
    floors_markup = build_floors_buttons(get_user_city(message.from_user.id))
    bot.send_message(message.chat.id, "Выбери *этаж*", reply_markup=floors_markup)


@bot.message_handler(regexp="Календарь|Список")
def show_books(message: Message):
    booking_list = get_books_for_user(message.from_user.id)
    if booking_list:
        for booking in booking_list:
            print(booking)
        users_status[str(message.from_user.id)] = {
            "objects": [booking[0] for booking in booking_list]
        }
        bot.send_message(
            message.chat.id,
            "Вот твои *брони*.\n\nЕсли хочешь удалить какую-нибудь из броней - *нажми* на неё.",
            reply_markup=build_booking_markup(booking_list),
        )
    else:
        bot.send_message(message.chat.id, "У тебя ещё *нет* броней.")


@bot.message_handler(["mybooks"])
def handle_unbook(message: Message):
    show_books(message)


@bot.message_handler(regexp="Отменить бронирование студента")
def student_unbook(message: Message):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute(f"select distinct slack_name, tg_id from reserve where live = 0")
    data = cursor.fetchall()
    markup = InlineKeyboardMarkup()
    for booking in data:
        print(f"{booking[0]}")
        markup.add(InlineKeyboardButton(f"{booking[0]}", callback_data=booking[1]))

    if data:
        answer = "Чью бронь нужно *удалить*?"
    else:
        answer = "Пока что никто не забронировал ни один объект."
    bot.send_message(message.chat.id, answer, reply_markup=markup)


@bot.message_handler(regexp="Отменить свою бронь")
def unbook(message: Message, user_id: str = None):
    if user_id is not None:
        booking_list = get_books_for_user(user_id)
    else:
        booking_list = get_books_for_user(message.from_user.id)
    if booking_list:
        for booking in booking_list:
            print(booking)
        users_status[str(message.from_user.id)] = {
            "objects": [booking[0] for booking in booking_list]
        }

        if user_id is not None:
            is_adm = True
        else:
            is_adm = False
        markup = build_booking_markup(booking_list, is_adm)
        markup.add(
            InlineKeyboardButton("Отменить все брони", callback_data="cancel_all")
        )
        if user_id is None:
            answer = "Выбери бронь, которую нужно *удалить*"
        else:
            answer = f"Выбери бронь пользователя *{get_user_username(user_id)}* чтобы удалить её"
        bot.send_message(message.chat.id, answer, reply_markup=markup)
    else:
        if user_id is not None:
            answer = "У пользователя ещё нет забронированных объектов."
        else:
            answer = "У тебя ещё *нет* броней."
        bot.send_message(message.chat.id, answer, reply_markup=None)


@bot.message_handler(["unbook"])
def handle_unbook(message: Message):
    unbook(message)


def decode_month(month: int):
    months = [
        "января",
        "февраля",
        "марта",
        "апреля",
        "мая",
        "июня",
        "июля",
        "августа",
        "сентября",
        "октября",
        "ноября",
        "декабря",
    ]
    return months[month - 1]


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def display_calendar(call: CallbackQuery):
    """Отобразить календарь для выбора брони

    Args:
        call (telebot.types.CallbackQuery): Нажатие inline-кнопки
    """
    result, key, step = DetailedTelegramCalendar(
        locale="ru",
        min_date=date.today(),
        max_date=date.replace(date.today(), date.today().year, date.today().month + 2),
    ).process(call.data)
    if not result and key:
        if LSTEP[step] == "month":
            unit = "месяц"
        else:
            unit = "день"
        bot.edit_message_text(
            f"Выбери *{unit}* брони",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=key,
        )
    elif result:
        users_status[str(call.from_user.id)]["date"] = result
        times_markup = build_time_markup(
            users_status[str(call.from_user.id)]["object_id"],
            users_status[str(call.from_user.id)]["date"].day,
            users_status[str(call.from_user.id)]["date"].month,
            users_status[str(call.from_user.id)]["date"].year,
        )
        if times_markup:
            bot.edit_message_text(
                "Выбери *время начала* брони",
                call.message.chat.id,
                call.message.id,
                reply_markup=times_markup,
            )
        else:
            bot.edit_message_text(
                "На данный объект нет свободного времени для брони данного объекта.",
                call.message.chat.id,
                call.message.id,
                reply_markup=None,
            )
        users_status[str(call.from_user.id)]["start_time"] = -1


def edit_message_after_deletion(call: CallbackQuery):
    new_books_list = get_books_for_user(call.from_user.id)
    if new_books_list:
        new_reply_markup = build_booking_markup(new_books_list)
        bot.edit_message_reply_markup(
            call.message.chat.id, call.message.id, reply_markup=new_reply_markup
        )
    else:
        bot.edit_message_text(
            "Все брони удалены.",
            call.message.chat.id,
            call.message.id,
            reply_markup=None,
        )


@bot.callback_query_handler(func=lambda call: True)
def show_objects(call: CallbackQuery):
    """Показать объекты для выбора брони

    Args:
        call (telebot.types.CallbackQuery): Нажатие inline-кнопки
    """
    user_city = get_user_city(call.from_user.id)

    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute(f"select distinct tg_id from reserve where live = 0")
    data = cursor.fetchall()
    data = [str(el).strip("(),") for el in data]
    print(data)

    if call.data in data:
        unbook(call.message, call.from_user.id)
    elif user_city is not None:
        floors_list = get_city_floors(user_city)
        print(call.data)
        if call.data == "cancel_all" or call.data == "cancel_all$$":
            booking_list = get_books_for_user(call.from_user.id)
            for booking in booking_list:
                delete_line_queue_departures(
                    database, "reserve", "", "id_reserve", booking[0]
                )
            if call.data == "cancel_all$$":
                users_status[str(call.from_user.id)][""]
            edit_message_after_deletion(call)
        elif fullmatch(r"^[0-2][0-9]:[0-5][0-5]$", call.data):
            if users_status[str(call.from_user.id)]["start_time"] == -1:
                users_status[str(call.from_user.id)].get("start_time")
                users_status[str(call.from_user.id)]["start_time"] = call.data
                bot.edit_message_text(
                    "Выбери *время конца* брони",
                    call.message.chat.id,
                    call.message.id,
                    reply_markup=build_time_markup(
                        users_status[str(call.from_user.id)]["object_id"],
                        users_status[str(call.from_user.id)]["date"].day,
                        users_status[str(call.from_user.id)]["date"].month,
                        users_status[str(call.from_user.id)]["date"].year,
                        users_status[str(call.from_user.id)]["start_time"],
                    ),
                )
            else:
                add_booking(
                    call.from_user.id,
                    users_status[str(call.from_user.id)]["object_id"],
                    users_status[str(call.from_user.id)]["start_time"],
                    call.data,
                    users_status[str(call.from_user.id)]["date"],
                )
                bot.edit_message_text(
                    f"Успешная бронь объекта \"{get_object_name(users_status[str(call.from_user.id)]['object_id'])}\" на *{users_status[str(call.from_user.id)]['floor']} этаже* на *{users_status[str(call.from_user.id)]['date']} {users_status[str(call.from_user.id)]['start_time']} - {call.data}*.",
                    call.message.chat.id,
                    call.message.id,
                    reply_markup=None,
                )
                del users_status[str(call.from_user.id)]
        elif call.data[-2:] == "$$" or (
            int(call.data)
            in [booking[0] for booking in get_books_for_user(call.from_user.id)]
        ):
            # delete_record("reserve", "id_reserve", int(call.data))
            if call.data[-2:] == "$$":
                call.data = call.data[:-2]
            delete_line_queue_departures(
                database, "reserve", "", "id_reserve", call.data
            )
            edit_message_after_deletion(call)
        elif call.data in floors_list:
            objects_markup = build_objects_buttons(user_city, call.data)
            bot.edit_message_text(
                f"Выбери *объект* для брони на *{call.data} этаже*",
                call.message.chat.id,
                call.message.id,
                reply_markup=objects_markup,
            )
            users_status[str(call.from_user.id)] = {"floor": call.data}
            users_status[str(call.from_user.id)]["objects"] = get_objects_id(
                objects_markup
            )
        elif call.data in users_status[str(call.from_user.id)]["objects"]:
            calendar = DetailedTelegramCalendar(
                locale="ru",
                min_date=date.today(),
                max_date=date.replace(
                    date.today(), date.today().year, date.today().month + 2
                ),
            ).build()
            users_status[str(call.from_user.id)]["object_name"] = get_object_name(
                int(call.data)
            )
            users_status[str(call.from_user.id)]["object_id"] = call.data
            bot.edit_message_text(
                f"Выбери *год* брони для объекта *\"{users_status[str(call.from_user.id)]['object_name']}\"* на этаже *{users_status[str(call.from_user.id)]['floor']}*",
                call.message.chat.id,
                call.message.id,
                reply_markup=calendar,
            )
    else:
        bot.send_message(call.message.chat.id, "Произошла непредвиденная ошибка.")


@bot.message_handler(["book"])
def handle_book(message: Message):
    """Обработка команды /book

    Args:
        message (telebot.types.Message): Сообщение пользователя
    """
    show_floors(message)


@bot.message_handler(content_types=["text"])
def handle_text(message: Message):
    """Обработка обычного текста

    Args:
        message (telebot.types.Message): Сообщение пользователя
    """
    try:
        users_status.get(str(message.from_user.id)).get("status")
    except BaseException:
        bot.send_message(
            message.chat.id,
            "Я не знаю такой команды. Попробуй *понажимать на кнопочки* или *ввести команду* из списка с помощью `/`.",
        )
    else:
        handle_credentials(message)


def main():
    bot.infinity_polling()


if __name__ == "__main__":
    main()
