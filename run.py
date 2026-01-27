from app import app
from dotenv import load_dotenv
import os

load_dotenv()  # Загружает переменные окружения из файла .env

if __name__ == '__main__':
    app.run()
