from pathlib import Path
from typing import List, Tuple, Any
from uuid import uuid4

from PIL import ImageFont, Image, ImageDraw, ImageColor

from core.services.base.types import BaseService, Result, IMAGES_PATH, FONTS_PATH
from logs.logs import log_decorator


class PhotoService(BaseService):
    result_type: str = Result.Photo

    base_image_path: str
    demo_image_path: str

    @staticmethod
    def auto_pasting_text(draw: ImageDraw,
                          format_text: List[Tuple[str, Any, str]],
                          x_start: int, y_start: int, width: int,
                          line_spacing: int = 2) -> None:
        y = y_start
        x = x_start
        for text, font, color in format_text:
            font: ImageFont
            length = font.getlength(text)
            if x + length > width:
                part_of_text = ""
                for word in text.split(" "):
                    tmp_text = part_of_text + word + " "
                    length = font.getlength(tmp_text)
                    if x + length < width:
                        part_of_text = tmp_text
                    else:
                        draw.text((x, y),
                                  part_of_text,
                                  fill=ImageColor.getrgb('#' + color),
                                  font=font,
                                  anchor='la')
                        part_of_text = word + " "
                        x = x_start
                        y += font.size + line_spacing
                if part_of_text:
                    draw.text((x, y),
                              part_of_text,
                              fill=ImageColor.getrgb('#' + color),
                              font=font,
                              anchor='la')
                    x = x_start + font.getlength(part_of_text)
            else:
                draw.text((x, y),
                          text,
                          fill=ImageColor.getrgb('#' + color),
                          font=font,
                          anchor='la')
                x += length

    @log_decorator
    def get_photo_path(self, filename: str) -> Path:
        file_path = self.RESOURCES_DIR / filename
        if not file_path.exists():
            file_path: Path = IMAGES_PATH / filename
        assert file_path.exists(), f"Файл {filename} не найден"
        return file_path

    @log_decorator
    def get_font_path(self, font_path: str) -> Path:
        file_path = self.RESOURCES_DIR / font_path
        if not file_path.exists():
            file_path: Path = FONTS_PATH / font_path
        assert file_path.exists(), f"Файл {font_path} не найден"
        return file_path

    @log_decorator
    def run(self, filename: str = '') -> Path:
        assert self.is_valid()

        image = Image.open(self.get_photo_path(self.base_image_path))
        draw = ImageDraw.Draw(image)

        for param in self.parameters:
            # Игнорирование полей по специальной логике вставки
            if param.key not in self.query:
                continue
            font = ImageFont.truetype(
                str(self.get_font_path(param.font)), param.size)
            value = self.query[param.key]
            if param.base_format_text:
                value = param.base_format_text.format(self.query[param.key])
            for number, value_line in enumerate(value.split('\n')):
                draw.text((param.x_start, (param.size + 10) * number + param.y_start),
                          value_line,
                          fill=ImageColor.getrgb('#' + param.color),
                          font=font,
                          spacing=param.spacing,
                          stroke_width=param.stroke_width,
                          anchor={'left': 'la', 'center': 'ma', 'right': 'ra'}[param.align])

        file_path: Path = self.RESULT_PATH / f'{filename or uuid4()}.jpg'
        if file_path.exists():
            file_path.unlink()
        image.save(file_path)

        return file_path
