from src.utils.exceptions import UnexpectedErrorMessage
from src.utils.models import DecoderErrorLocation


def parse_error_message(msg: str) -> DecoderErrorLocation:
    """line 2 column 1 (char 2)-F"""
    print(msg)
    print(msg[-4])
    print(msg[-12])
    print(msg[-12])
    error_location = DecoderErrorLocation(
        location="1. 'В который переносим ключи'" if msg[-1] == "T" else "2. 'Из которого переносим ключ'и",
        char=int(msg[-4]),
        column=int(msg[-12]),
        line=int(msg[-21])
    )
    try:
        return error_location
    except TypeError as err:
        raise UnexpectedErrorMessage(f"This message text was not expected: {msg}, can't handel")


print(parse_error_message("line 2 column 1 (char 2)-T"))
