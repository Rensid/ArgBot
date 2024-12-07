from core.services.base import Parameter, PhotoService


class LetterARGFirst(PhotoService):
    base_image_path: str = "letter_arg_first.jpg"
    demo_image_path: str = "letter_arg_first_demo.jpg"

    category: str = "p2p"

    name: str = "Письмо ARG"
    parameters = [
        Parameter(font='SFProText/SFProText-Semibold.ttf', size=18, x_start=740, x_end=800, y_start=285, y_end=285,
                  base_format_text="{}", key="date", color="003655", description="дату документа",
                  default="de deciembre de 2024"),

    ]
