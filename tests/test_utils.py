from yarl import URL

from urlcut.utils.generate_link import (
    generate_link, generate_link_path, salted_number,
)


def test_salted_number(salt, pepper):
    assert salted_number(1, salt, pepper) == 2329936982


def test_generate_link_path(alphabet):
    result_path = generate_link_path(
        alphabet=alphabet,
        salted_num=2329936982,
    )
    assert result_path == "CaCCgCaaaaAaAAAC"


def test_generate_link(domain):
    link = generate_link(
        domain=URL(domain),
        short_path="CaCCgCaaaaAaAAAC",
    )
    assert link == URL("http://example.com/CaCCgCaaaaAaAAAC")
