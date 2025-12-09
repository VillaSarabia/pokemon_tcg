from django.shortcuts import get_object_or_404
from .models import Pedido, Categoria

def carrito_context(request):
    """
    Context processor para añadir información del carrito a todos los templates
    """
    if request.user.is_authenticated:
        try:
            carrito = Pedido.objects.filter(
                cliente=request.user,
                estado='CARRITO'
            ).first()
            
            if carrito:
                cantidad_items = sum(item.cantidad for item in carrito.items.all())
                total_carrito = carrito.total
            else:
                cantidad_items = 0
                total_carrito = 0
        except:
            cantidad_items = 0
            total_carrito = 0
    else:
        # Para usuarios no autenticados, usar sesión
        cart = request.session.get('cart', {})
        cantidad_items = sum(item['cantidad'] for item in cart.values())
        total_carrito = sum(item['precio'] * item['cantidad'] for item in cart.values())
    
    return {
        'cantidad_carrito': cantidad_items,
        'total_carrito': total_carrito,
    }

def categorias_context(request):
    """
    Context processor para mostrar categorías en el menú
    """
    categorias = Categoria.objects.all()[:10]  # Limitar a 10 categorías para el menú
    return {
        'categorias_menu': categorias,
    }

# En core/context_processors.py (crea este archivo si no existe)
from .models import Categoria

def categorias_menu(request):
    """Context processor para las categorías del menú"""
    return {
        'categorias_menu': Categoria.objects.all()[:10]  # Limitar a 10 categorías
    }