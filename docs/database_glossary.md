# Глосарий базы данных
### Ниже будут описаны константы, наименование, расшифровка полей бд и способы работы с бд

## Структура бд

### main.db - файл, содержащий три(3) таблицы: 
    users - содержет информацию о пользователях
    object - содержет инофрмацию о бранируемых объектах
    reserve - содержет информацию о уже забронированных объектах на конкретную дату

## Таблицы и поля
# users
- ##    tg_id
            INTEGER NOT NULL PRIMARY KEY
            Ключ не может быть пустым
            Хранит id пользователя из tg
- ##    slack_name
            VARCHAR(10)
            Хранит имя пользователя с платформы
- ##    access_rights
            INTEGER
            Хранит права доступа пользователя в формате:
            (0 - абитуриет)
            (111 - студент)
            (999 - АДМ)
- ##    city_id
            INTEGER
            Хранит город пользователя:
            (0 - МСК)
            (1 - НСК)
            (2 - КЗН)
# object
- ##    id
            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
            Ключ не может быть пустым и заполняется автоматически при добавлении элемента
            Хранит id объекта или территории
- ##    object
            VARCHAR(20)
            Хранит название объекта/территории
- ##    floor
            INTEGER
            Хранит этаж на котором хранится/находится объект/территория
- ##    city_id
            INTEGER
            Хранит город пользователя:
            (0 - МСК)
            (1 - НСК)
            (2 - КЗН)
- ##    NNA
            INTEGER
            NNA - Need to Notify ADM
            ПУА - Потребность Уведомлять АДМ
            хранит либо 0 либо 1
# reverse
- ##    id_reverse
            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
            Ключ не может быть пустым и заполняется автоматически при добавлении элемента
            Хранит id записи
- ##    id
            INTEGER
            Хранит id объекта или территории переданного из таблицы object
- ##    object_name
            VARCHAR(20)
            Хранит название объекта/территории переданного из таблицы object
- ##    tg_id
            INTEGER
            Хранит id пользователя переданного из таблицы users
- ##    slack_name
            VARCHAR(20)
            Хранит имя пользователя переданного из таблицы users
- ##    start_res
            TEXT
            Хранит время начала регистрации:
            16:00:00
            (храним только часы и минуты в промежутке по 30 минут, поле с секундами всегда оставляем пустым)
- ##    end_res
            TEXT
            Хранит время конца регистрации:
            16:30:00
            (храним только часы и минуты в промежутке по 30 минут, поле с секундами всегда оставляем пустым)
- ##    data
            TEXT
            Хранит дату начала регистрации:
            2022-05-07
- ##    comment
            TEXT
            Хранит комментарий к записи об удалении
- ##    live
            INTEGER
            Изначально всегда равен 0
            Если параметр == 1 (АДМ удалили вашу запись из очереди), иначе запись в очереди


# Константы из файла src/backEnd/dbCreate.py
- ##    MAINDB
            хранит строку (str) с название базы данных
- ##    USERSDB
            хранит строку (str) с название таблицы пользователей
- ##    OBJECTSDB
            хранит строку (str) с название таблицы объектов
- ##    RESERVEDB
            хранит строку (str) с название таблицы резервации(брони)

# Функции из файла src/backEnd/unteractiondb.py
- ##    delete_record
            (table: str, elem, value)

            удаление строки из таблицы table, по колонке elem с ключом value
- ##    add_user
            (elem, values: list)

            добавление пользователя, уго парметры хранятся в value(list):
               tg_id,     slack_name,  access_rights,  city_id
            {values[0]}, '{values[1]}', {values[2]}, {values[3]}

            по elem производится проверка на наличие этого пользователя в базе
            (АТЕНШЕН, В elem НУЖНО ПЕРЕДАВАТЬ ТОЛЬКО ТЕЛЕГРАМ ID ПОЛЗОВАТЕЛЯ)
- ##    add_booking
            (user_id: int, object_id: int, time_start: str, time_end: str, date: str)

            Добавить бронь в таблицу броней

            user_id (int): ID пользователя в Telegram
            object_id (int): ID бронируемого объекта
            time_start (str): Время начала брони
            time_end (str): Время конца брони
            date (str): Дата брони

            добавляет user_id, object_id, time_start, time_end, date в новую строчку в таблице reserve

- ##    comparison_of_table_elements
            (first_table: str, second_table: str, elem1, elem2, coincidence)

            функция стравнивает элементы elem1, elem2 таблицы first_table с second_table по критерию coincidence
            и возвращает True если совпадение есть, иначе False
- ##    check_for_existence
            (table_name: str, crit, elem)

            функция проверяет на существование elem в таблице table_name по ключу(критерию) crit
- ##    get_city_floors
            (city: int)

            функция возвращает этаж city из таблицы object
- ##    get_objects_from_floor
            (city: int, floor: int)

            функция возвращает все объекты(в виде коллекции) по city (id города) и floor (этаж)
- ##    get_user_city
            (user_tg_id: int)

            функция возвращает город где находится пользователь по tg_id (user_tg_id) из таблицы users
- ##    get_object_name
            (object_id: int)

            функция возвращает имя объекта из таблицы object по id (object_id)
- ##    get_books_for_user
            (user_id: int)
            функция возвращает всю строку из таблицы reserve по tg_id (user_id)
- ##    delete_line_queue_departures
            (dbname: str, table_name: str, ADMmessage: str, id_reserve: int, elem: str)
            функция возвращает True если нашла в таблице table_name elem равный id_reserve
            и обновляет в table_name поле 'comment' = ADMmessage, 'live' = 1 где elem = id_reserve
            иначе false 