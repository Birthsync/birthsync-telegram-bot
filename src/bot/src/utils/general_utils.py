import datetime

from loguru import logger


def birthdate_to_unix_timestamp(date_str: str) -> int | None:
    try:
        dt = datetime.datetime.strptime(date_str, "%d.%m.%Y")
        return int(dt.timestamp())
    except ValueError:
        return None


def birthdate_from_unix_timestamp(timestamp: int | str) -> str:
    if not timestamp:
        return ''

    try:
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime("%d.%m.%Y")
    except (ValueError, TypeError):
        return ''


@logger.catch()
def insert_line_breaks(text, max_length=32):
    lines = text.split('\n')
    result = []

    for line in lines:
        words = line.split()
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_length:
                if current_line:
                    current_line += " "
                current_line += word
            else:
                result.append(current_line)
                current_line = word

        if current_line:
            result.append(current_line)

    return "\n".join(result)