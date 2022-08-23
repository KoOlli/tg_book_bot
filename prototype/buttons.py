from telebot.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
import time
from sys import path

path.append("..")
from backEnd.unteractiondb import (
    get_city_floors,
    get_objects_from_floor,
    get_books_for_object,
    get_object_floor,
)


path.pop()

database = "../backEnd/main.db"

# Кнопки админов
ADMIN_MARKUP = ReplyKeyboardMarkup(row_width=1)
ADMIN_MARKUP.add(
    *[
        "Календарь бронирования",
        "Забронировать",
        "Отменить свою бронь",
        "Отменить бронирование студента",
    ]
)

# Кнопки студентов
STUDENT_MARKUP = ReplyKeyboardMarkup(row_width=1)
STUDENT_MARKUP.add(*["Календарь бронирования", "Забронировать", "Отменить свою бронь"])


def build_floors_buttons(city: str):
    floors_list = get_city_floors(city)
    result = InlineKeyboardMarkup(row_width=1)
    for floor in floors_list:
        result.add(InlineKeyboardButton(f"{floor} этаж", callback_data=floor))
    return result


def build_objects_buttons(city: int, floor: int):
    objects_list = get_objects_from_floor(city, floor)
    print(objects_list)
    result = InlineKeyboardMarkup(row_width=1)
    for object in objects_list:
        result.add(InlineKeyboardButton(str(object[1]), callback_data=str(object[0])))
    return result


def get_objects_id(objects_markup: InlineKeyboardMarkup):
    result = []
    for objects_list in objects_markup.keyboard:
        for object in objects_list:
            result.append(object.callback_data)
    return result


def build_booking_markup(booking_list: list, is_adm: bool = False):
    result = InlineKeyboardMarkup(row_width=1)
    for booking in booking_list:
        floor = get_object_floor(booking[1])
        callback = str(booking[0])
        if is_adm:
            callback += "$$"
        result.add(
            InlineKeyboardButton(
                f"{booking[-3]} {booking[-5]} - {booking[-4]} | {booking[2]} | {floor}",
                callback_data=callback,
            )
        )
    return result


def int_from_date():
    today = time.strftime("%Y-%m-%d", time.gmtime())
    today_year = int(today.split("-")[0])
    today_month = int(today.split("-")[1])
    today_day = int(today.split("-")[2])
    return today_year, today_month, today_day


def count_minutes(
    today_day: int,
    day: int,
    today_month: int,
    month: int,
    today_year: int,
    year: int,
    previous_time: str,
):
    if today_day == day and today_month == month and today_year == year:
        minutes_total = int(time.time()) % (60 * 60 * 24) // 60
        while minutes_total % 30 != 0:
            minutes_total = (minutes_total + 1) % (60 * 60 * 24)
    else:
        minutes_total = 0
    if previous_time is not None:
        minutes_total += (
            int(previous_time.split(":")[0]) * 60
            + int(previous_time.split(":")[-1])
            - minutes_total
            + 30
        )
    return minutes_total


def time_from_int(hour: int, minutes: int):
    hour = str(hour)
    if len(hour) == 1:
        hour = "0" + hour

    minutes = str(minutes)
    if len(minutes) == 1:
        minutes = "0" + minutes
    return f"{hour}:{minutes}"


def minutes_from_time(time: str):
    hours = int(time.split(":")[0])
    minutes = int(time.split(":")[-1])
    return hours * 60 + minutes


def date_from_int(year: int, month: int, day: int):
    month = str(month)
    if len(month) == 1:
        month = "0" + month

    day = str(day)
    if len(day) == 1:
        day = "0" + day
    return f"{year}-{month}-{day}"


def normalize_markup(result: InlineKeyboardMarkup):
    indexes, callbacks = [], []
    for i in range(len(result.keyboard)):
        for j in range(len(result.keyboard[i])):
            indexes.append([i, j])
            callbacks.append(result.keyboard[i][j].callback_data)

    # Проверяем края
    if callbacks[1] == "empty_time":
        result.keyboard[indexes[0][0]][indexes[0][-1]].callback_data = "empty_time"
        result.keyboard[indexes[0][0]][indexes[0][-1]].text = "     "
    if callbacks[-2] == "empty_time":
        result.keyboard[indexes[-2][0]][indexes[-2][-1]].callback_data = "empty_time"
        result.keyboard[indexes[-2][0]][indexes[-2][-1]].text = "     "

    for i in range(1, len(callbacks) - 1):
        if callbacks[i - 1] == callbacks[i + 1] == "empty_time":
            result.keyboard[indexes[i][0]][indexes[i][-1]].callback_data = "empty_time"
            result.keyboard[indexes[i][0]][indexes[i][-1]].text = "     "

    return result


def build_time_markup(
    object_id: int, day: int, month: int, year: int, previous_time: str = None
):
    today_year, today_month, today_day = int_from_date()
    print("today_year =", today_year, "| year =", year)
    print("today_month =", today_month, "| month =", month)
    print("today_day =", today_day, "| day =", day)

    minutes_total = count_minutes(
        today_day, day, today_month, month, today_year, year, previous_time
    )

    result = InlineKeyboardMarkup()

    print("minutes_total =", minutes_total)
    i = ((60 * 24) - minutes_total) // 120 + 1
    print("i =", i)
    # Получаем список диапазонов времён забронированного объекта
    books_for_object = get_books_for_object(
        object_id,
        time.strftime(
            "%Y-%m-%d", time.struct_time(sequence=[year, month, day, 0, 0, 0, 0, 0, 0])
        ),
    )
    books_times = []
    exit_check = False
    for book in books_for_object:
        start_time = int(book[-5].split(":")[0]) * 60 + int(book[-5].split(":")[-1])
        end_time = int(book[-4].split(":")[0]) * 60 + int(book[-4].split(":")[-1])
        for minute in range(start_time, end_time, 30):
            books_times.append(minute)
    not_empty_count = 0
    for m in range(i):
        row = []
        print(
            "first row buttons count =",
            ((((60 * 24) - minutes_total) // 30) + 3) % 4 + 1,
        )
        print("m =", m)
        empty_row_check = True
        for _ in range(((((60 * 24) - minutes_total) // 30) + 3) % 4 + 1):
            if m >= 12 or minutes_total >= 60 * 24:
                exit_check = True
                break
            hours = str(minutes_total // 60)
            if len(hours) == 1:
                hours = "0" + hours
            minutes = str(minutes_total % 60)
            if len(minutes) == 1:
                minutes = "0" + minutes

            if minutes_total not in books_times:
                empty_row_check = False
                not_empty_count += 1
                row.append(
                    InlineKeyboardButton(
                        f"{hours}:{minutes}", callback_data=f"{hours}:{minutes}"
                    )
                )
            else:
                row.append(InlineKeyboardButton("     ", callback_data="empty_time"))
            minutes_total += 30
        if not empty_row_check:
            result.keyboard.append(row)
        if exit_check:
            break

    result = normalize_markup(result)

    print(len(result.keyboard))
    if len(result.keyboard) == 0 or not_empty_count <= 1:
        result = None
    return result
