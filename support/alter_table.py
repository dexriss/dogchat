import sqlite3
import os

dirapp = os.path.dirname(os.path.normpath(os.path.dirname(__file__)))
print(os.path.join(dirapp,'app/database.db'))
# Создание или подключение к базе данных
conn = sqlite3.connect(os.path.join(dirapp,"app/database.db"))

#Создание курсора
c = conn.cursor()

# Создание таблицы Content
c.execute('''  ALTER TABLE profies ADD COLUMN image TEXT; ''')
c.execute('''  ALTER TABLE profies ADD COLUMN type_prf TEXT; ''')

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

