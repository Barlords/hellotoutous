from dataclasses import dataclass

SESSION_KEY = "cart"


@dataclass(frozen=True)
class CartLine:
    variant_id: int
    quantity: int
    with_knot: bool


def get_lines(session) -> list[CartLine]:
    raw = session.get(SESSION_KEY, [])
    return [
        CartLine(
            variant_id=int(item["variant_id"]),
            quantity=int(item["quantity"]),
            with_knot=bool(item["with_knot"]),
        )
        for item in raw
    ]


def item_count(session) -> int:
    return sum(line.quantity for line in get_lines(session))


def add_line(session, *, variant_id: int, quantity: int, with_knot: bool) -> None:
    if quantity < 1:
        raise ValueError("Quantity must be at least 1.")
    lines = get_lines(session)
    merged: list[CartLine] = []
    found = False
    for line in lines:
        if line.variant_id == variant_id and line.with_knot == with_knot:
            merged.append(
                CartLine(
                    variant_id=variant_id,
                    quantity=line.quantity + quantity,
                    with_knot=with_knot,
                )
            )
            found = True
        else:
            merged.append(line)
    if not found:
        merged.append(CartLine(variant_id=variant_id, quantity=quantity, with_knot=with_knot))
    session[SESSION_KEY] = [
        {
            "variant_id": line.variant_id,
            "quantity": line.quantity,
            "with_knot": line.with_knot,
        }
        for line in merged
    ]
    session.modified = True
