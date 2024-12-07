from .letter_arg_first_service import LetterARGFirst
from .letter_arg_second_service import LetterARGSecond
from ..base import MultipleServices


service = MultipleServices(
    LetterARGFirst.name,
    LetterARGFirst.category,
    LetterARGFirst(),
    LetterARGSecond(),
)

is_enabled = True
