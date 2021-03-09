import logging
from typing import List

from yarl import URL


log = logging.getLogger(__name__)


def generate_link(domain: URL, short_path: str) -> URL:
    path = f"/{short_path}"
    return URL.build(
        scheme=domain.scheme,
        host=domain.host,  # type: ignore
        path=path,
    )


def generate_link_path(alphabet: List[str], salted_num: int) -> str:
    len_alphabet = len(alphabet)
    temp = ""
    while salted_num != 0:
        rest = salted_num % len_alphabet
        temp += alphabet[rest]
        salted_num = salted_num // len_alphabet
    result = "".join(temp[::-1])
    log.debug("Generated result for short link path is %r", result)
    return result


def salted_number(number: int, salt: int, pepper: int) -> int:
    pepper2bin = format(pepper, "b")
    number2bin = format(number, "b")
    zeros = 32 - len(pepper2bin) - len(number2bin)
    number_with_pepper = pepper2bin + "0" * zeros + number2bin
    return int(number_with_pepper, 2) ^ salt
