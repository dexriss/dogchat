import sqlite3
import os

dirapp = os.path.dirname(os.path.normpath(os.path.dirname(__file__)))
print(os.path.join(dirapp,'app\database.db'))
# Создание или подключение к базе данных
conn = sqlite3.connect(os.path.join(dirapp,'app\database.db'))

#Создание курсора
c = conn.cursor()


c.execute('''ALTER TABLE users ADD COLUMN point TEXT''')



conn.close()



# os.path.dirname(os.path.normpath('a/b/'))          => 'a'
# os.path.normpath(os.path.join('a/b/', os.pardir))  => 'a'

# os.path.dirname(os.path.normpath('a/b'))           => 'a'
# os.path.normpath(os.path.join('a/b', os.pardir))   => 'a'

# os.path.dirname(os.path.normpath('a/'))            => ''
# os.path.normpath(os.path.join('a/', os.pardir))    => '.'

# os.path.dirname(os.path.normpath('a'))             => ''
# os.path.normpath(os.path.join('a', os.pardir))     => '.'

# os.path.dirname(os.path.normpath('.'))             => ''
# os.path.normpath(os.path.join('.', os.pardir))     => '..'

# os.path.dirname(os.path.normpath(''))              => ''
# os.path.normpath(os.path.join('', os.pardir))      => '..'

# os.path.dirname(os.path.normpath('..'))            => ''
# os.path.normpath(os.path.join('..', os.pardir))    => '../..'
