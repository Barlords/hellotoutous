import pytest

from cart.services.session_cart import CartLine, add_line, get_lines, item_count


class MemorySession(dict):
    modified = False


def test_add_line_merges_the_same_variant_and_option():
    session = MemorySession()
    add_line(session, variant_id=3, quantity=1, with_knot=False)
    add_line(session, variant_id=3, quantity=2, with_knot=False)

    assert get_lines(session) == [CartLine(variant_id=3, quantity=3, with_knot=False)]
    assert item_count(session) == 3


def test_knot_option_does_not_add_another_line():
    session = MemorySession()
    add_line(session, variant_id=3, quantity=2, with_knot=True)

    assert get_lines(session) == [CartLine(variant_id=3, quantity=2, with_knot=True)]
    assert item_count(session) == 2


def test_same_variant_with_and_without_knot_are_distinct_lines():
    session = MemorySession()
    add_line(session, variant_id=3, quantity=1, with_knot=False)
    add_line(session, variant_id=3, quantity=1, with_knot=True)

    assert item_count(session) == 2
    assert len(get_lines(session)) == 2


def test_quantity_below_one_is_rejected():
    session = MemorySession()
    with pytest.raises(ValueError):
        add_line(session, variant_id=3, quantity=0, with_knot=False)
