from decimal import Decimal

KNOT_CATEGORY_CODES = frozenset({"collar", "harness"})


class KnotOptionError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def validate_knot_option(*, category_code: str, offers_knot: bool, knot_price: Decimal | None) -> None:
    if not offers_knot:
        if knot_price is not None:
            raise KnotOptionError("Le supplément nœud doit rester vide quand l'option est désactivée.")
        return
    if category_code not in KNOT_CATEGORY_CODES:
        raise KnotOptionError("L'option avec nœud n'est disponible que pour les colliers et les harnais.")
    if knot_price is None or knot_price <= 0:
        raise KnotOptionError("Indiquez un supplément nœud supérieur à 0.")
