from pickle import OBJ
from random import randint, random
import sqlite3
from dbCreate import *
from unteractiondb import *

nodes = sqlite3.connect(MAINDB)
cursor = nodes.cursor()

# constant to add table reserve
# user
tg_id = 706588178
slack_name = "romildab"
access_rig = 999
city_id = 1
# object
object_id = 4
# time
time_s = "16:30:00"
time_e = "17:00:00"
date = "2022:11:15"


# add to users
ADMINS = [
    {"tg_id": 706588178, "slack_name": "romildab", "access_rights": 999, "city_id": 1},
    {"tg_id": 868341381, "slack_name": "karleenk", "access_rights": 999, "city_id": 1},
    {"tg_id": 1701854147, "slack_name": "tandrasc", "access_rights": 999, "city_id": 1},
    {"tg_id": 409813448, "slack_name": "elenemar", "access_rights": 999, "city_id": 1},
    {"tg_id": 882287144, "slack_name": "shanelac", "access_rights": 999, "city_id": 1},
]

nodes.commit()

# add to object
OBJECTS = [
    {"object": "Игровая", "floor": 17, "city_id": 1, "NNA": randint(0, 1)},
    {"object": "Холл", "floor": 17, "city_id": 1, "NNA": randint(0, 1)},
    {"object": "Кухня", "floor": 17, "city_id": 1, "NNA": randint(0, 1)},
    {"object": "Игровая", "floor": 18, "city_id": 1, "NNA": randint(0, 1)},
    {"object": "Переговорка", "floor": 18, "city_id": 1, "NNA": randint(0, 1)},
    {"object": "Холл", "floor": 18, "city_id": 1, "NNA": randint(0, 1)},
    {"object": "Кухня", "floor": 18, "city_id": 1, "NNA": randint(0, 1)},
    {"object": "Переговорка", "floor": 20, "city_id": 1, "NNA": randint(0, 1)},
    {"object": "Игровая", "floor": 20, "city_id": 1, "NNA": randint(0, 1)},
    {"object": "Кикер", "floor": 20, "city_id": 1, "NNA": randint(0, 1)},
    {"object": "XBox", "floor": 20, "city_id": 1, "NNA": randint(0, 1)},
    {"object": "Теннисный стол", "floor": 20, "city_id": 1, "NNA": randint(0, 1)},
    {"object": "Кухня", "floor": 20, "city_id": 1, "NNA": randint(0, 1)},
    {"object": "Мастерская", "floor": 22, "city_id": 1, "NNA": randint(0, 1)},
    {"object": "Шафран", "floor": 22, "city_id": 1, "NNA": randint(0, 1)},
]

# add_booking(tg_id, object_id, time_s, time_e, date)

for object in ADMINS:
    cursor.execute(
        f"INSERT INTO users (tg_id, slack_name, access_rights, city_id)\
        VALUES ({object['tg_id']}, '{object['slack_name']}', {object['access_rights']}, {object['city_id']});"
    )
nodes.commit()


for object in OBJECTS:
    cursor.execute(
        f"insert into object (object, floor, city_id, NNA) values ('{object['object']}', {object['floor']}, {object['city_id']}, {object['NNA']});"
    )
nodes.commit()
