from cart.services.session_cart import add_line
from catalog.models import ProductVariant
from catalog.services.pricing import unit_price


def add_variant_to_cart(
    session, *, variant: ProductVariant, quantity: int, with_knot: bool
) -> None:
    product = variant.product
    # Validate the option before touching the session. Price is not stored.
    unit_price(
        base_price=product.base_price,
        offers_knot=product.offers_knot,
        knot_price=product.knot_price,
        with_knot=with_knot,
    )
    add_line(session, variant_id=variant.id, quantity=quantity, with_knot=with_knot)
