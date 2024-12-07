from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union
from inspect import getfile

import moviepy.editor as mp
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


VIDEO_TYPE = Union[mp.VideoFileClip, mp.CompositeVideoClip]

BASE_PATH = Path("./styles")
RESULT_PATH = Path('./result')

FONTS_PATH = BASE_PATH / "fonts"
IMAGES_PATH = BASE_PATH / "images"
VIDEO_PATH = BASE_PATH / "video"


class Result:
    Photo = "photo"
    Video = "video"


@dataclass
class Parameter:
    font: str
    size: int
    color: str

    key: str
    description: str

    # Coordinates
    x_start: int
    x_end: int
    y_start: int
    y_end: int

    default: Union[str, List[str], None] = None
    align: str = "left"
    spacing: int = 4
    stroke_width: int = 0
    base_format_text: str = ""

    def get_text(self) -> str:
        text = f"Введите {self.description}"
        if self.default:
            if isinstance(self.default, list):
                default = ", ".join(f"`{item}`" for item in self.default)
            else:
                default = f"`{self.default}`"
            text += f" (по умолчанию {default})"
        text += ("\n\nВажно: не бросайте ввод параметров генерации картинок. "
                 "Если хотите прекратить ввод, воспользуйтесь командой /cancel, "
                 "затем можете смело покидать бота")
        return text

    def get_keyboard(self) -> Optional[ReplyKeyboardMarkup]:
        if self.default and isinstance(self.default, str):
            return ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=self.default)]],
                one_time_keyboard=True,
                resize_keyboard=True,
            )
        elif self.default and isinstance(self.default, list):
            return ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=item)
                           for item in self.default]],
                one_time_keyboard=True,
                resize_keyboard=True
            )


class BaseService(ABC):
    name: str
    category: str
    result_type: str
    parameters: List[Parameter] = []

    RESULT_PATH = Path('./result')

    def __init__(self):
        self._is_valid = None
        self.query = {}

        self.PROJECT_DIR = Path(getfile(type(self))).parent
        self.RESOURCES_DIR = self.PROJECT_DIR / "resources"

        self.global_resources_path = Path('.') / "styles"
        self.FONTS_DIR = self.global_resources_path / "fonts"

    def init(self, **kwargs: str):
        self.query = kwargs

    def is_valid(self):
        if self._is_valid is None:
            self._is_valid = True
            for param in self.parameters:
                self._is_valid = self._is_valid and param.key in self.query

        return self._is_valid

    @abstractmethod
    def run(self) -> Path:
        pass


class BaseEffect(ABC):
    @staticmethod
    @abstractmethod
    def run(*args, **kwargs):
        pass

    def __new__(cls, *args, **kwargs):
        return cls.run(*args, **kwargs)
