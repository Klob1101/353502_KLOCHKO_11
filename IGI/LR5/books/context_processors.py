from .models import Genre

def genres(request):
    return {
        'genres': Genre.objects.all()
    }

def cart(request):
    """Context processor для корзины"""
    cart = request.session.get('cart', {})
    return {
        'cart': cart,
        'cart_count': len(cart)
    } 