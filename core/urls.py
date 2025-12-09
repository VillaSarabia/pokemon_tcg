from django.urls import path
from django.contrib.auth import views as auth_views_django
from django.contrib.auth.decorators import login_required
from .views import auth_views, carta_views, carrito_views, pago_views, admin_views, normal_views

urlpatterns = [
    # ==============================================
    # PÁGINAS PRINCIPALES
    # ==============================================
    path('', carta_views.home_view, name='home'), 
    
    # ==============================================
    # AUTENTICACIÓN
    # ==============================================
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('register/', auth_views.register_view, name='register'),
    
    # ==============================================
    # CARTAS POKÉMON
    # ==============================================
    path('cartas/', carta_views.lista_cartas, name='lista_cartas'),
    path('cartas/<int:carta_id>/', carta_views.detalle_carta, name='detalle_carta'),
    path('cartas/filtrar/', carta_views.filtrar_cartas, name='filtrar_cartas'),
    path('cartas/buscar/', carta_views.buscar_cartas, name='buscar_cartas'),
    
    # Wishlist
    path('wishlist/', carta_views.wishlist_view, name='wishlist'),
    path('wishlist/agregar/<int:carta_id>/', carta_views.agregar_wishlist, name='agregar_wishlist'),
    path('wishlist/eliminar/<int:carta_id>/', carta_views.eliminar_wishlist, name='eliminar_wishlist'),
    
    # ==============================================
    # CARRITO DE COMPRAS
    # ==============================================
    path('carrito/', carrito_views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:carta_id>/', carrito_views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/', carrito_views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:item_id>/', carrito_views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/vaciar/', carrito_views.vaciar_carrito, name='vaciar_carrito'),
    path('carrito/checkout/', carrito_views.checkout_view, name='checkout'),
    
    # Pedidos
    path('mis-pedidos/', carrito_views.mis_pedidos, name='mis_pedidos'),
    path('pedido/<uuid:pedido_id>/', carrito_views.detalle_pedido, name='detalle_pedido'),
    
    # ==============================================
    # PAGOS
    # ==============================================
    path('pago/efectivo/', pago_views.pago_efectivo, name='pago_efectivo'),
    path('pago/tarjeta/', pago_views.pago_tarjeta, name='pago_tarjeta'),
    path('pago/paypal/', pago_views.pago_paypal, name='pago_paypal'),
    path('pago/transferencia/', pago_views.pago_transferencia, name='pago_transferencia'),
    path('pago/procesar/<str:metodo>/', pago_views.procesar_pago, name='procesar_pago'),
    
    # ==============================================
    # PANEL DE ADMINISTRACIÓN
    # ==============================================
    path('admin-dashboard/', admin_views.dashboard_view, name='admin_dashboard'),
    path('dashboard/<str:model_name>/', admin_views.lista_admin, name='lista_admin'),
    path('dashboard/<str:model_name>/crear/', admin_views.crear_admin, name='crear_admin'),
    path('dashboard/<str:model_name>/<int:obj_id>/', admin_views.detalle_admin, name='detalle_admin'),
    path('dashboard/<str:model_name>/<int:obj_id>/editar/', admin_views.editar_admin, name='editar_admin'),
    path('dashboard/<str:model_name>/<int:obj_id>/eliminar/', admin_views.eliminar_admin, name='eliminar_admin'),

    # Gestión de pedidos
    path('dashboard/pedidos/<uuid:pedido_id>/confirmar/', admin_views.confirmar_pedido, name='confirmar_pedido'),
    path('dashboard/pedidos/<uuid:pedido_id>/enviar/', admin_views.marcar_enviado, name='marcar_enviado'),
    path('dashboard/pedidos/<uuid:pedido_id>/completar/', admin_views.marcar_completado, name='marcar_completado'),
    
    # ==============================================
    # ERROR PAGES
    # ==============================================
    path('404/', auth_views.error_404, name='error_404'),
    path('500/', auth_views.error_500, name='error_500'),
]

# Error handlers
handler404 = 'core.views.auth_views.error_404'
handler500 = 'core.views.auth_views.error_500'