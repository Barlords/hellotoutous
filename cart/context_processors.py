from cart.services.session_cart import item_count


def cart_count(request):
    return {"cart_item_count": item_count(request.session)}
