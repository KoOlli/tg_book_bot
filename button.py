import telebot
import sqlite3
from telebot import types


bot = telebot.TeleBot("5640308255:AAEf6tatwKtCzbepukds5ux4cuhME6xtasA")


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Новосибирск', callback_data='1')
    item2 = types.InlineKeyboardButton('Москва', callback_data='0')
    item3 = types.InlineKeyboardButton('Казань', callback_data='2')
    markup.add(item, item2, item3)
    bot.send_message(message.chat.id, 'Выберите город', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)

def reserve(call: types.CallbackQuery):
    connect = sqlite3.connect('users.db') #наименование sql файла
    cursor = connect.cursor()

    connect.execute("""CREATE TABLE IF NOT EXISTS reserve_id(
        id INTEGER,
        city INTEGER
    )""")
    connect.commit()
    cursor.execute(f"INSERT INTO reserve_id (id, city) VALUES({call.from_user.id}, {call.data});")
    connect.commit()


bot.polling()