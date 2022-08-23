import sqlite3

MAINDB = "main.db"

USERSDB = "users"
OBJECTSDB = "object"
RESERVEDB = "reserve"

connect = sqlite3.connect(MAINDB)


def createdb_user(tableName, connect):
    cursor = connect.cursor()
    cursor.execute(
        f"""CREATE TABLE IF NOT EXISTS {tableName}(
        tg_id INTEGER NOT NULL PRIMARY KEY,              
        slack_name VARCHAR(20),     
        access_rights INTEGER,      
        city_id INTEGER             
    )"""
    )
    # 87567880
    # dogekassß
    # 999
    # 2
    connect.commit()


def createdb_objects(tableName, connect):
    cursor = connect.cursor()
    cursor.execute(
        f"""CREATE TABLE IF NOT EXISTS {tableName}(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        object VARCHAR(20),               
        floor INTEGER,              
        city_id INTEGER,                
        NNA INTEGER                 
    )"""
    )
    # 0000
    # 00
    # 2
    # PLAYROM
    # 0 OR 1
    connect.commit()


def createdb_reserve(tableName, connect):
    cursor = connect.cursor()
    cursor.execute(
        f"""CREATE TABLE IF NOT EXISTS {tableName}(
        id_reserve INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
        id INTEGER,            
        object_name VARCHAR(20),    
        tg_id INTEGER,              
        slack_name VARCHAR(20),
        start_res TEXT,         
        end_res TEXT,
        data TEXT,
        comment TEXT,
        live INTEGER DEFAULT 0 NOT NULL
    )"""
    )
    # 0000
    # PLAYROM
    # 87567880
    # dogekass
    # 16:30:00
    # 17:00:00
    connect.commit()


createdb_user(USERSDB, connect)
createdb_objects(OBJECTSDB, connect)
createdb_reserve(RESERVEDB, connect)
connect.close()
