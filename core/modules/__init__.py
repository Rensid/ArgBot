from aiogram import Dispatcher


def load_modules(dp: Dispatcher):
    from .commands import router

    dp.include_router(router)
