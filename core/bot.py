from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

import config
from core.modules import load_modules


bot = Bot(config.BOT_TOKEN)
if config.REDIS_HOST and config.REDIS_PORT:
    storage = RedisStorage.from_url(
        url=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/",
        data_ttl=10800,  # 3 hours
    )
else:
    print("[WARNING] Redis is not configured!!!")
    storage = MemoryStorage()

dp = Dispatcher(storage=storage)


def run():
    load_modules(dp)
    dp.run_polling(bot)
