from environs import Env

environ = Env()
environ.read_env('.env')

BOT_TOKEN = environ.str("BOT_TOKEN", "")  # Токен бота

# Redis
REDIS_HOST = environ.str("REDIS_HOST", "localhost")
REDIS_PORT = environ.str("REDIS_PORT", "6379")

# Количество кнопок в строке
BUTTONS_IN_ROW = environ.int("BUTTONS_IN_ROW", 3)
