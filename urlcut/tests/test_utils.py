from yarl import URL

from urlcut.utils.generate_link import (
    generate_link, generate_link_path, get_number, salted_number,
)


def test_salted_number():
    assert salted_number(1, 1111, 2222) == 2329936982


def test_generate_link_path():
    result_path = generate_link_path(
        alphabet=["a", "A", "C", "g"],
        salted_num=2329936982,
    )
    assert result_path == "CaCCgCaaaaAaAAAC"


def test_generate_link():
    link = generate_link(
        domain=URL("http://example.com"),
        short_path="CaCCgCaaaaAaAAAC",
    )
    assert link == URL("http://example.com/CaCCgCaaaaAaAAAC")
