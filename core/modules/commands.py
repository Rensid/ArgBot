from pathlib import Path
from typing import Dict, List

from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    FSInputFile,
    InputMediaPhoto,
    InputMediaDocument,
    InputMediaVideo,
    ReplyKeyboardRemove,
)
from aiogram.filters import CommandStart, StateFilter, or_f, Command

import config
from core.services import SERVICES
from core.services.base import Parameter, BaseService, PhotoService, MultipleServices
from logs.logs import log_decorator

router = Router()


class Stages(StatesGroup):
    selected_category = State()
    selected_service = State()
    select_parameters = State()
    ready_to_do = State()


@log_decorator
@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer(
        "ℹ️ Для генерации скриншота используйте команду из панели `💡 Сгенерировать скриншот`, "
        "если панель пропала напишите /start", parse_mode='MARKDOWN',
        reply_markup=ReplyKeyboardMarkup(keyboard=[[
            KeyboardButton(text="💡 Сгенерировать скриншот")
        ]], one_time_keyboard=True, resize_keyboard=True)
    )
    await state.clear()


@log_decorator
@router.message(F.text == "Назад", StateFilter(Stages.selected_category))
@router.message(F.text == "💡 Сгенерировать скриншот" or F.text == "Выбрать шаблон", StateFilter(None))
async def get_category_list(message: Message, state: FSMContext):
    await message.answer(
        'Выберите вариацию обработки канала:',
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text=category)] for category in set(serv.category for serv in SERVICES)
        ], one_time_keyboard=True, resize_keyboard=True)
    )
    await state.set_state(None)


@log_decorator
@router.message(or_f(*[F.text == service.category for service in SERVICES]), StateFilter(None))
async def select_category(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(category=message.text)
    await state.set_state(Stages.selected_category)
    services = list(filter(lambda x: x.category == message.text, SERVICES))
    keyboard = [[KeyboardButton(text=services[config.BUTTONS_IN_ROW*i + j].name) for j in range(config.BUTTONS_IN_ROW)]
                for i in range(len(services) // config.BUTTONS_IN_ROW)]
    stop_index = (len(services) // config.BUTTONS_IN_ROW) * \
        config.BUTTONS_IN_ROW
    if stop_index < len(services):
        keyboard.append([KeyboardButton(text=serv.name)
                        for serv in services[stop_index:]])
    keyboard.append([KeyboardButton(text="Назад")])
    await message.answer(
        f'Выбранная вариация обработки канала - {message.text}\n'
        'Выберите необходимый шаблон:',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )


@log_decorator
async def get_service(state: FSMContext) -> BaseService:
    data = await state.get_data()
    service_name = data.get('service_name')
    return next(filter(lambda serv: serv.name == service_name, SERVICES))


@log_decorator
@router.message(or_f(*[F.text == service.name for service in SERVICES]), StateFilter(Stages.selected_category))
async def select_service(message: Message, state: FSMContext):
    # Выбор сервиса
    await state.update_data(service_name=message.text, query={})
    service = await get_service(state)

    if isinstance(service, MultipleServices):
        method = message.answer_media_group
        files = []
        for serv in service.services:
            if isinstance(serv, PhotoService):
                print(serv.demo_image_path)
                files.append(InputMediaPhoto(
                    media=FSInputFile(
                        path=serv.get_photo_path(serv.demo_image_path),
                    )
                ))

    elif isinstance(service, PhotoService):
        method = message.answer_photo
        files = FSInputFile(service.get_photo_path(service.demo_image_path))
    else:
        raise

    await method(
        files
    )
    await message.answer(
        text="Вот пример документа. Перейти к вводу данных?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Перейти к вводу")],
                [KeyboardButton(text="Назад")],
            ],
            one_time_keyboard=True,
            resize_keyboard=True,
        )
    )
    await state.set_state(Stages.selected_service)


@log_decorator
@ router.message(F.text == 'Перейти к вводу', StateFilter(Stages.selected_service))
async def accept_to_service(message: Message, state: FSMContext):
    service = await get_service(state)
    try:
        param: Parameter = service.parameters[0]
    except IndexError:
        await run(message, service, {})
        await state.clear()
        return

    await message.answer(
        text=param.get_text(),
        reply_markup=param.get_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(Stages.select_parameters)


@log_decorator
@ router.message(Command(commands=['cancel']), StateFilter(Stages.select_parameters))
@ router.message(F.text == 'Назад', StateFilter(Stages.selected_service))
async def back_from_service(message: Message, state: FSMContext):
    await state.set_state(None)
    await state.clear()
    await get_category_list(message, state)


@log_decorator
@ router.message(StateFilter(Stages.selected_service))
async def undefined_message(message: Message):
    await message.answer(
        "Мне ответ не понятен. Выберите на клавиатуре",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Перейти к вводу")],
                [KeyboardButton(text="Назад")],
            ],
            one_time_keyboard=True,
            resize_keyboard=True,
        )
    )


@log_decorator
async def run(message: Message, service_type: BaseService, query: Dict[str, str] = None):
    if query is None:
        query = {}
    service_type.init(**query)
    assert service_type.is_valid()
    action_type = "генерации" if isinstance(
        service_type, PhotoService) else "рендеринга"
    wait_message: Message = await message.answer(
        text=f"Принято в работу. Ожидайте завершения {action_type}..."
    )
    try:
        result = service_type.run()
    except AssertionError:
        await message.answer("В данный момент сервис не может сгенерировать Вам нужный документ по причине "
                             "технической ошибки. Прошу попробовать сделать запрос позднее")
    else:
        if isinstance(service_type, PhotoService):
            result: Path
            file = FSInputFile(path=result)
            await message.answer_document(file)
        elif isinstance(service_type, MultipleServices):
            result: List[Path]
            files = [
                InputMediaDocument(
                    media=FSInputFile(
                        path=res
                    )
                ) for res in result
            ]
            await message.answer_media_group(
                media=files
            )

        # Удаление локальных файлов
        if isinstance(result, list):
            for res in result:
                res.unlink()
        else:
            result.unlink()
    finally:
        await wait_message.delete()


@log_decorator
@router.message(StateFilter(Stages.select_parameters))
async def input_parameters(message: Message, state: FSMContext):
    service = await get_service(state)
    data = await state.get_data()
    query = data.get('query', {})
    msg = 'Принято!\n'
    need_to_save = True

    for parameter in service.parameters:
        if parameter.key in query:
            continue
        elif need_to_save:
            need_to_save = False
            query[parameter.key] = message.text
            await state.update_data(query=query)
        else:
            msg += parameter.get_text()
            await message.answer(
                text=msg,
                reply_markup=parameter.get_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
            break
    else:
        await message.answer(msg)
        await run(message, service, query)
        await state.clear()
        await start(message, state)


@log_decorator
@router.message(Command(commands=['restart']))
async def restart(message: Message):
    ADMIN_IDS = {  # Множество Telegram ID пользователей
        621629634,  # https://t.me/ilyakanyshev
        8048517221,  # https://t.me/ikanyshev
    }
    if message.from_user and message.from_user.id in ADMIN_IDS:
        await message.answer(
            text="Перезапуск бота...",
            reply_markup=ReplyKeyboardRemove()
        )
        exit(0)
    else:
        await message.answer(
            "Ой, я не могу перезапустить бота. Вы не являетесь его администратором"
        )
