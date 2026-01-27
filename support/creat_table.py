import sqlite3
import os

dirapp = os.path.dirname(os.path.normpath(os.path.dirname(__file__)))
print(os.path.join(dirapp,'app/database.db'))
# Создание или подключение к базе данных
conn = sqlite3.connect(os.path.join(dirapp,"app/database.db"))

#Создание курсора
c = conn.cursor()

# Создание таблицы Content
c.execute('''  CREATE TABLE user (
    "id" INTEGER  PRIMARY KEY AUTOINCREMENT,
    "login" TEXT NOT NULL,
    "phone" TEXT,
    "password" TEXT NOT NULL,
    "first_name" TEXT,
    "last_name" TEXT,
    "city" TEXT,
    "date_of_birth" TEXT,
    "purpose_of_dating" TEXT,
    "about" TEXT,
    "ava_img" TEXT,
    "created_at" TEXT,
    "edited_at" TEXT
) ''')

c.execute(''' CREATE TABLE pet
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nikname TEXT NOT NULL,
    breed TEXT,
    age INTEGER,
    about TEXT,
    neutered INTEGER,
    user_id INTEGER,
    ava_img TEXT,
    FOREIGN KEY (user_id)  REFERENCES user (id) ON DELETE CASCADE
 ) ''')

conn.close()

#  CREATE TABLE user (
#     "id" INTEGER  PRIMARY KEY AUTOINCREMENT,
#     "login" TEXT NOT NULL,
#     "password" TEXT NOT NULL,
#     "first name" TEXT,
#     "last name" TEXT,
#     "city" TEXT,
#     "date of birth" TEXT,
#     "the purpose of dating" TEXT,
#     "about" TEXT,
#     "phone" TEXT
# )

