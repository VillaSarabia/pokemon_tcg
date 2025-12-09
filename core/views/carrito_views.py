# core/views/carrito_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from ..models import Carta, Pedido, ItemPedido, Inventario
from decimal import Decimal
from django.utils import timezone


@login_required
def ver_carrito(request):
    """Vista del carrito de compras"""
    try:
        # Buscar carrito existente
        carrito = Pedido.objects.filter(
            cliente=request.user,
            estado='CARRITO'
        ).first()
        
        # Si no existe, crear uno nuevo CON TODOS LOS CAMPOS REQUERIDOS
        if not carrito:
            nombre_usuario = f"{request.user.first_name or ''} {request.user.last_name or ''}".strip()
            if not nombre_usuario:
                nombre_usuario = request.user.username
            
            carrito = Pedido.objects.create(
                cliente=request.user,
                estado='CARRITO',
                nombre_completo=nombre_usuario,
                email=request.user.email or '',
                telefono='',
                direccion='',
                ciudad='No especificada',  # VALOR POR DEFECTO REQUERIDO
                provincia='',
                codigo_postal='',
                pais='España',
                subtotal=Decimal('0.00'),
                envio=Decimal('0.00'),
                impuestos=Decimal('0.00'),
                total=Decimal('0.00')
            )
            messages.info(request, "Se ha creado un nuevo carrito para ti.")
        
        # Calcular totales
        carrito.calcular_totales()
        
        context = {
            'carrito': carrito,
            'items': carrito.items.all().select_related('carta', 'inventario'),
        }
        
        return render(request, 'carrito/ver.html', context)
        
    except Exception as e:
        messages.error(request, f"Error al cargar el carrito: {str(e)}")
        return redirect('lista_cartas')


@login_required
def agregar_al_carrito(request, carta_id):
    """Agregar una carta al carrito"""
    try:
        carta = get_object_or_404(Carta, id=carta_id)
        cantidad = int(request.POST.get('cantidad', 1))
        
        # Verificar stock
        if not hasattr(carta, 'inventario') or carta.inventario is None:
            messages.error(request, f'No hay inventario para {carta.nombre}')
            return redirect('detalle_carta', carta_id=carta_id)
        
        if carta.inventario.stock_real < cantidad:
            messages.error(request, f'Stock insuficiente para {carta.nombre}')
            return redirect('detalle_carta', carta_id=carta_id)
        
        # Obtener o crear carrito CON TODOS LOS CAMPOS REQUERIDOS
        carrito = Pedido.objects.filter(
            cliente=request.user,
            estado='CARRITO'
        ).first()
        
        if not carrito:
            nombre_usuario = f"{request.user.first_name or ''} {request.user.last_name or ''}".strip()
            if not nombre_usuario:
                nombre_usuario = request.user.username
            
            carrito = Pedido.objects.create(
                cliente=request.user,
                estado='CARRITO',
                nombre_completo=nombre_usuario,
                email=request.user.email or '',
                telefono='',
                direccion='',
                ciudad='No especificada',  # VALOR POR DEFECTO REQUERIDO
                provincia='',
                codigo_postal='',
                pais='España',
                subtotal=Decimal('0.00'),
                envio=Decimal('0.00'),
                impuestos=Decimal('0.00'),
                total=Decimal('0.00')
            )
        
        # Verificar si ya existe el item
        item_existente = carrito.items.filter(carta=carta).first()
        
        if item_existente:
            # Actualizar cantidad
            nueva_cantidad = item_existente.cantidad + cantidad
            if nueva_cantidad <= carta.inventario.stock_real:
                item_existente.cantidad = nueva_cantidad
                item_existente.save()
                messages.success(request, f'Cantidad actualizada para {carta.nombre}')
            else:
                messages.error(request, f'Stock insuficiente para agregar más unidades de {carta.nombre}')
        else:
            # Crear nuevo item
            ItemPedido.objects.create(
                pedido=carrito,
                carta=carta,
                inventario=carta.inventario,
                cantidad=cantidad,
                precio_unitario=carta.inventario.precio_actual
            )
            messages.success(request, f'{carta.nombre} añadida al carrito')
        
        # Recalcular totales
        carrito.calcular_totales()
        
        return redirect('ver_carrito')
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('detalle_carta', carta_id=carta_id)

def crear_carrito_usuario(user):
    """Crea un nuevo carrito para un usuario con todos los campos requeridos"""
    nombre_usuario = f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not nombre_usuario:
        nombre_usuario = user.username
    
    return Pedido.objects.create(
        cliente=user,
        estado='CARRITO',
        nombre_completo=nombre_usuario,
        email=user.email or '',
        telefono='',
        direccion='',
        ciudad='No especificada',  # Campo requerido
        provincia='',
        codigo_postal='',
        pais='España',
        subtotal=Decimal('0.00'),
        envio=Decimal('0.00'),
        impuestos=Decimal('0.00'),
        total=Decimal('0.00')
    )


@login_required
def ver_carrito(request):
    """Vista del carrito de compras - Versión simplificada"""
    try:
        # Buscar carrito existente
        carrito = Pedido.objects.filter(
            cliente=request.user,
            estado='CARRITO'
        ).first()
        
        # Si no existe, crear uno nuevo usando la función auxiliar
        if not carrito:
            carrito = crear_carrito_usuario(request.user)
        
        # Calcular totales
        carrito.calcular_totales()
        
        context = {
            'carrito': carrito,
            'items': carrito.items.all().select_related('carta', 'inventario'),
        }
        
        return render(request, 'carrito/ver.html', context)
        
    except Exception as e:
        messages.error(request, f"Error al cargar el carrito: {str(e)}")
        return redirect('lista_cartas')

@login_required
def actualizar_carrito(request, item_id):
    """Actualizar cantidad de un item en el carrito"""
    try:
        item = get_object_or_404(ItemPedido, id=item_id, pedido__cliente=request.user)
        
        if request.method == 'POST':
            cantidad = int(request.POST.get('cantidad', 1))
            
            if cantidad <= 0:
                item.delete()
                messages.success(request, 'Item eliminado del carrito')
            elif cantidad <= item.inventario.stock_real:
                item.cantidad = cantidad
                item.save()
                messages.success(request, 'Cantidad actualizada')
            else:
                messages.error(request, 'Stock insuficiente')
        
        return redirect('ver_carrito')
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('ver_carrito')


@login_required
def eliminar_del_carrito(request, item_id):
    """Eliminar un item del carrito"""
    try:
        item = get_object_or_404(ItemPedido, id=item_id, pedido__cliente=request.user)
        carta_nombre = item.carta.nombre
        pedido = item.pedido
        item.delete()
        messages.success(request, f'{carta_nombre} eliminado del carrito')
        
        # Recalcular totales
        pedido.calcular_totales()
        
        return redirect('ver_carrito')
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('ver_carrito')


@login_required
def vaciar_carrito(request):
    """Vaciar completamente el carrito"""
    try:
        carrito = Pedido.objects.filter(cliente=request.user, estado='CARRITO').first()
        if carrito:
            carrito.items.all().delete()
            carrito.calcular_totales()
            messages.success(request, 'Carrito vaciado')
        return redirect('ver_carrito')
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('ver_carrito')


@login_required
def checkout_view(request):
    """Vista de checkout para completar la compra"""
    try:
        carrito = Pedido.objects.filter(cliente=request.user, estado='CARRITO').first()
        
        if not carrito or carrito.items.count() == 0:
            messages.warning(request, 'Tu carrito está vacío')
            return redirect('lista_cartas')
        
        # Verificar stock
        for item in carrito.items.all():
            if item.cantidad > item.inventario.stock_real:
                messages.error(request, f'Stock insuficiente para {item.carta.nombre}')
                return redirect('ver_carrito')
        
        if request.method == 'POST':
            # Procesar información (usar nombres CORRECTOS de campos)
            carrito.nombre_completo = request.POST.get('nombre_completo')
            carrito.email = request.POST.get('email')
            carrito.telefono = request.POST.get('telefono')
            carrito.direccion = request.POST.get('direccion')
            carrito.ciudad = request.POST.get('ciudad')
            carrito.provincia = request.POST.get('provincia')
            carrito.codigo_postal = request.POST.get('codigo_postal')
            carrito.pais = request.POST.get('pais', 'España')
            carrito.metodo_pago = request.POST.get('metodo_pago')
            carrito.notas = request.POST.get('notas')
            carrito.estado = 'PENDIENTE'  # Cambiar estado a pendiente
            carrito.save()
            
            # Reservar stock
            for item in carrito.items.all():
                item.inventario.reservar(item.cantidad)
            
            messages.success(request, '¡Pedido realizado con éxito!')
            return redirect('mis_pedidos')
        
        context = {
            'carrito': carrito,
        }
        return render(request, 'carrito/checkout.html', context)
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('ver_carrito')

@login_required
def mis_pedidos(request):
    """Historial de pedidos del usuario"""
    try:
        pedidos = Pedido.objects.filter(
            cliente=request.user
        ).exclude(estado='CARRITO').order_by('-fecha_pedido')
        
        context = {
            'pedidos': pedidos,
        }
        return render(request, 'carrito/historial.html', context)
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('lista_cartas')


@login_required
def detalle_pedido(request, pedido_id):
    """Detalle de un pedido específico"""
    try:
        pedido = get_object_or_404(
            Pedido,
            numero_pedido=pedido_id,
            cliente=request.user
        )
        
        context = {
            'pedido': pedido,
        }
        return render(request, 'carrito/detalle_pedido.html', context)
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('mis_pedidos')