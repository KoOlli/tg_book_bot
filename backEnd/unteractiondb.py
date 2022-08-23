from os import access
import sqlite3

database = "../backEnd/main.db"


class UsersField:
    tg_id = 00000000
    slack_name = ""
    access_rights = 000
    city_id = 0


class ObjectsField:
    id = 0
    object_name = ""
    floor = 0
    city_id = 0
    NNA = 0


class ReserveField:
    id_reserve = 0
    id = 0
    object_name = "object_name"
    tg_id = 0
    slack_name = "slack_name"
    start_res = "00:00:00"
    end_res = "00:00:00"
    data = "0000-00-00"
    comment = None
    live = 0


# table - name your table list (users)
# elem -
def delete_record(table: str, elem, value):
    """Удалить запись из базы данных

    Args:
        table (str): Имя таблицы
        elem (Any): Поле удаления
        value (Any): Критерий удаления
    """
    with sqlite3.connect(database) as connect:
        cursor = connect.cursor()
        connect.commit()
        # print("connect to sqlite")
        delete_table = f"""DELETE from {table} WHERE {elem} = {value}"""
        cursor.execute(delete_table)
        connect.commit()


def add_user(elem, values: list):
    """Добавить пользователя в таблицу пользователей

    Args:
        elem (Any): Поле для проверки
        values (list): Данные пользователя
    """
    try:
        connect = sqlite3.connect(database)
        cursor = connect.cursor()
        connect.commit()
        # check user id
        cursor.execute(f"SELECT {elem} FROM users WHERE {elem} = {values[0]}")
        data = cursor.fetchone()
        if data is None:
            cursor.execute(
                f"INSERT INTO users (tg_id, slack_name, access_rights, city_id) VALUES \
                ({values[0]}, '{values[1]}', {values[2]}, {values[3]});"
            )
            connect.commit()
    finally:
        if connect:
            connect.close()
            # print("connect close")


def add_booking(
    user_id: int, object_id: int, time_start: str, time_end: str, date: str
):
    """Добавить бронь в таблицу броней

    Args:
        user_id (int): ID пользователя в Telegram
        object_id (int): ID бронируемого объекта
        time_start (str): Время начала брони
        time_end (str): Время конца брони
        date (str): Дата брони
    """
    with sqlite3.connect(database) as connect:
        cursor = connect.cursor()
        cursor.execute(f"select * from users where tg_id = {user_id}")
        dataUser = cursor.fetchone()
        cursor.execute(f"select * from object where id = {object_id}")
        dataObj = cursor.fetchone()
        if (dataUser is None) | (dataObj is None):
            # возможно тут нужна проверка на уже имеющиеся записи
            #
            # ->
            return False
        else:
            cursor.execute(
                f"INSERT INTO reserve (id, object_name, tg_id, slack_name, start_res, end_res, data, comment, live) \
                VALUES ({dataObj[0]}, '{dataObj[1]}', {dataUser[0]}, '{dataUser[1]}', '{time_start}', '{time_end}', '{date}', '', 0)"
            )
            connect.commit()
            return True


def comparison_of_table_elements(
    first_table: str, second_table: str, elem1, elem2, coincidence
):
    """Сравнение элементов двух таблиц

    Args:
        first_table (str): Первая таблица
        second_table (str): Вторая таблица
        elem1 (_type_): Первое поле
        elem2 (_type_): Второе поле
        coincidence (_type_): Значение для сравнения

    Returns:
        Bool: True если равны, False иначе
    """
    with sqlite3.connect(database) as connect:
        cursor = connect.cursor()
        cursor.execute(
            f"select {elem1} from {first_table} where {elem1} = {coincidence}"
        )
        dataOne = cursor.fetchone()[0]
        cursor.execute(
            f"select {elem2} from {second_table} where {elem2} = {coincidence}"
        )
        dataTwo = cursor.fetchone()[0]
        connect.commit()
    if connect:
        connect.close()
    if dataOne == dataTwo:
        return True
    else:
        return False


def check_for_existence(table_name: str, crit, elem):
    """Проверка на существование столбца с данным значением в таблица

    Args:
        table_name (str): Имя таблицы
        crit (Any): Значение для поиска
        elem (Any): Столбец для поиска

    Returns:
        Bool: True если есть, False иначе
    """
    with sqlite3.connect(database) as connect:
        cursor = connect.cursor()
        cursor.execute(f"select {elem} from {table_name} where {elem} = {crit}")
        data = cursor.fetchone()
        if data is None:
            return False
        else:
            return True


def get_city_floors(city: int):
    """Возвращает этажи указанного города из таблицы объектов

    Args:
        city (str): Название города

    Returns:
        list: Список этажей
    """
    with sqlite3.connect(database) as connect:
        cursor = connect.cursor()
        cursor.execute(
            f"select distinct floor from object where city_id = {city} order by floor asc"
        )
        data = cursor.fetchall()
        if data is not None:
            for i in range(len(data)):
                data[i] = str(data[i]).strip("(),")
        return data


def get_objects_from_floor(city: int, floor: int):
    """Получить объекты этажа города

    Args:
        city (str): ID города
        floor (int): Номер этажа

    Returns:
        _type_: _description_
    """
    with sqlite3.connect(database) as connect:
        cursor = connect.cursor()
        cursor.execute(
            f"select * from object where city_id = {city} and floor = {floor}"
        )
        data = cursor.fetchall()
        return data


def get_user_city(user_tg_id: int):
    with sqlite3.connect(database) as connect:
        cursor = connect.cursor()
        cursor.execute(f"select city_id from users where tg_id = {user_tg_id}")
        data = cursor.fetchone()
        if data is not None:
            return data[0]
        else:
            return data


def get_user_role(user_tg_id: int):
    with sqlite3.connect(database) as connect:
        cursor = connect.cursor()
        cursor.execute(f"select access_rights from users where tg_id = {user_tg_id}")
        data = cursor.fetchone()
        if data is not None:
            return int(data[0])
        else:
            return data


def get_user_username(user_tg_id: int):
    with sqlite3.connect(database) as connect:
        cursor = connect.cursor()
        cursor.execute(f"select slack_name from users where tg_id = {user_tg_id}")
        data = cursor.fetchone()
        if data is not None:
            return str(data[0]).strip("(),")
        else:
            return data


def get_object_name(object_id: int):
    with sqlite3.connect(database) as connect:
        cursor = connect.cursor()
        cursor.execute(f"select object from object where id = {object_id}")
        data = cursor.fetchone()
        if data is not None:
            return data[0]
        else:
            return data


def get_object_floor(object_id: int):
    with sqlite3.connect(database) as connect:
        cursor = connect.cursor()
        cursor.execute(f"select floor from object where id = {object_id}")
        data = cursor.fetchone()
        return int(str(data).strip("(),"))


def get_books_for_user(user_id: int):
    with sqlite3.connect(database) as connect:
        cursor = connect.cursor()
        cursor.execute(f"select * from reserve where tg_id = {user_id} and live = 0")
        data = cursor.fetchall()
        return data


def get_books_for_object(object_id: int, date: str):
    with sqlite3.connect(database) as connect:
        cursor = connect.cursor()
        cursor.execute(
            f"select * from reserve where id = {object_id} and data = '{date}' and live = 0"
        )
        data = cursor.fetchall()
        return data


def delete_line_queue_departures(
    dbname: str, table_name: str, ADMmessage: str, id_reserve: int, elem: str
):
    with sqlite3.connect(dbname) as connect:
        cursor = connect.cursor()
        cursor.execute(f"SELECT {elem} FROM {table_name} WHERE {elem} = {id_reserve}")
        data = cursor.fetchone()
        if data is None:
            return False
        else:
            cursor.execute(
                f"UPDATE {table_name} SET comment = '{ADMmessage}', live = 1 WHERE {elem} = {id_reserve}"
            )
            connect.commit()
            return True
