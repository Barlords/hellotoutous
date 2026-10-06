from decimal import Decimal


class KnotNotOffered(Exception):
    pass


def unit_price(*, base_price: Decimal, offers_knot: bool, knot_price: Decimal | None, with_knot: bool) -> Decimal:
    if not with_knot:
        return base_price
    if not offers_knot or knot_price is None or knot_price <= 0:
        raise KnotNotOffered("Knot option is not available for this product.")
    return base_price + knot_price
