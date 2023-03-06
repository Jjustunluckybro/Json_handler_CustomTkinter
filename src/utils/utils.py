from src.utils.exceptions import UnexpectedErrorMessage
from src.utils.models import DecoderErrorLocation


def parse_error_message(msg: str):
    """Invalid control character at: line 13 column 44 (char 432)-T"""

    location = "1. 'В который переносим ключи'" if msg[-1] == "T" else "2. 'Из которого переносим ключ'и"

    line_index = msg.find("line") + 5
    column_index = msg.find("column") + 7
    char_index = msg.find("char ") + 5

    line = ''
    column = ''
    char = ''

    for symb in msg[line_index:]:
        if symb.isdigit():
            line += symb
        else:
            break

    for symb in msg[column_index:]:
        if symb.isdigit():
            column += symb
        else:
            break

    for symb in msg[char_index:]:
        if symb.isdigit():
            char += symb
        else:
            break

    try:
        return DecoderErrorLocation(
            location=location,
            line=int(line),
            column=int(column),
            char=int(char)
        )
    except ValueError as err:
        raise UnexpectedErrorMessage(f"This message text was not expected: {msg}, can't handel")


if __name__ == '__main__':
    print(parse_error_message("Invalid control character at: line 13 column 44 (char 432)-T"))
