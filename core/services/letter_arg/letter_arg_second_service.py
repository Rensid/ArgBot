from core.services.base import PhotoService, Parameter


class LetterARGSecond(PhotoService):
    base_image_path: str = "letter_arg_second.jpg"
    demo_image_path: str = "letter_arg_second_demo.jpg"

    category: str = "p2p"

    name: str = "Письмо ARG"
    parameters = [
        Parameter(font='SFProText/SFProText-Semibold.ttf', size=26, x_start=48, x_end=240, y_start=560, y_end=560,
                  description="имя клиента", key="client_name",
                  color="000000", default="Isabella Laos", base_format_text='"{}"'),
        Parameter(font='Arial/Arial.ttf', size=26, x_start=543, x_end=706, y_start=763, y_end=763,
                  description="сумму", key="sum",
                  color="000000", default="5732", base_format_text='{} $a.'),
        Parameter(font='SFProText/SFProText-Medium.ttf', size=26, x_start=730, x_end=838, y_start=857, y_end=857,
                  description="еще одна сумма", key="another sum",
                  color="000000", align="right", base_format_text='{} $a.', default="50000"),
    ]
