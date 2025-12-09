from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import uuid
from ..models import Pedido
from ..forms import PagoTarjetaForm
import json
from django.http import HttpResponseRedirect, JsonResponse

@login_required
def pago_efectivo(request):
    """Formulario de pago en efectivo"""
    carrito = Pedido.objects.filter(cliente=request.user, estado='CARRITO').first()
    
    if not carrito or carrito.items.count() == 0:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('lista_cartas')
    
    if request.method == 'POST':
        # Confirmar pago en efectivo
        carrito.estado = 'PEND'
        carrito.metodo_pago = 'EFEC'
        carrito.fecha_pago = timezone.now()
        carrito.save()
        
        messages.success(request, '¡Pedido confirmado! Deberás pagar en efectivo al recibir tu pedido.')
        return redirect('detalle_pedido', pedido_id=carrito.numero_pedido)
    
    context = {
        'carrito': carrito,
    }
    return render(request, 'pagos/efectivo.html', context)

@login_required
def pago_tarjeta(request):
    """Formulario de pago con tarjeta"""
    carrito = Pedido.objects.filter(cliente=request.user, estado='CARRITO').first()
    
    if not carrito or carrito.items.count() == 0:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('lista_cartas')
    
    form = PagoTarjetaForm()
    
    if request.method == 'POST':
        form = PagoTarjetaForm(request.POST)
        if form.is_valid():
            # Aquí iría la integración con pasarela de pago real
            # Por ahora simulamos el pago exitoso
            carrito.estado = 'PEND'
            carrito.metodo_pago = 'TARJ'
            carrito.fecha_pago = timezone.now()
            carrito.transaccion_id = f"TARJ_{uuid.uuid4().hex[:16].upper()}"
            carrito.save()
            
            messages.success(request, '¡Pago con tarjeta procesado exitosamente!')
            return redirect('detalle_pedido', pedido_id=carrito.numero_pedido)
    
    context = {
        'carrito': carrito,
        'form': form,
    }
    return render(request, 'pagos/tarjeta.html', context)

@login_required
def pago_paypal(request):
    """Simulación de pago con PayPal"""
    carrito = Pedido.objects.filter(cliente=request.user, estado='CARRITO').first()
    
    if not carrito or carrito.items.count() == 0:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('lista_cartas')
    
    if request.method == 'POST':
        # Simular procesamiento de PayPal
        carrito.estado = 'PEND'
        carrito.metodo_pago = 'PAYP'
        carrito.fecha_pago = timezone.now()
        carrito.transaccion_id = f"PAYP_{uuid.uuid4().hex[:16].upper()}"
        carrito.save()
        
        messages.success(request, '¡Pago con PayPal procesado exitosamente!')
        return redirect('detalle_pedido', pedido_id=carrito.numero_pedido)
    
    context = {
        'carrito': carrito,
    }
    return render(request, 'pagos/paypal.html', context)

@login_required
def pago_transferencia(request):
    """Información para pago por transferencia bancaria"""
    carrito = Pedido.objects.filter(cliente=request.user, estado='CARRITO').first()
    
    if not carrito or carrito.items.count() == 0:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('lista_cartas')
    
    if request.method == 'POST':
        # Confirmar que se realizará transferencia
        carrito.estado = 'PEND'
        carrito.metodo_pago = 'TRANS'
        # No marcamos como pagado hasta confirmar la transferencia
        carrito.save()
        
        messages.success(request, '¡Pedido confirmado! Por favor realiza la transferencia bancaria.')
        return redirect('detalle_pedido', pedido_id=carrito.numero_pedido)
    
    # Datos bancarios (en producción deberían estar en settings)
    datos_bancarios = {
        'titular': 'Pokemon TCG S.L.',
        'iban': 'ES12 3456 7890 1234 5678 9012',
        'bic': 'ABCDESMMXXX',
        'concepto': f'PEDIDO-{carrito.numero_pedido}',
        'importe': carrito.total,
    }
    
    context = {
        'carrito': carrito,
        'datos_bancarios': datos_bancarios,
    }
    return render(request, 'pagos/transferencia.html', context)

@login_required
def procesar_pago(request, metodo):
    """Endpoint para procesar pagos (simulación)"""
    carrito = Pedido.objects.filter(cliente=request.user, estado='CARRITO').first()
    
    if not carrito:
        return JsonResponse({'success': False, 'message': 'Carrito no encontrado'})
    
    # Simular procesamiento de pago
    carrito.estado = 'PEND'
    carrito.metodo_pago = metodo
    
    
    
    
    carrito.fecha_pago = timezone.now()
    carrito.transaccion_id = f"{metodo}_{uuid.uuid4().hex[:16].upper()}"
    carrito.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Pago procesado exitosamente',
        'pedido_id': str(carrito.numero_pedido)
    })