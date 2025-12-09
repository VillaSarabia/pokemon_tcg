"""
Este archivo inicializa el paquete views y hace que todas las vistas
estén disponibles para importación desde core.views
"""

# Re-exportar todas las vistas para facilitar las importaciones
from .auth_views import *
from .carta_views import *
from .carrito_views import *
from .pago_views import *
from .admin_views import *
from .normal_views import *