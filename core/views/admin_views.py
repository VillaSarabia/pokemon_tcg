from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from ..models import (
    Carta, Expansion, Categoria, Pedido, Inventario, 
    Resena, Coleccion, User
)
from django import forms
from django.forms import ModelForm

def staff_required(view_func):
    """Decorator para verificar que el usuario es staff"""
    decorated_view_func = login_required(user_passes_test(
        lambda u: u.is_staff,
        login_url='/login/'
    )(view_func))
    return decorated_view_func

@staff_required
def dashboard_view(request):
    """Dashboard de administración con estadísticas"""
    
    # Estadísticas generales
    total_ventas = Pedido.objects.filter(
        estado='ENTR',
    ).aggregate(total=Sum('total'))['total'] or 0
    
    pedidos_pendientes = Pedido.objects.filter(estado='PAGADO').count()
    stock_bajo = Inventario.objects.filter(cantidad_disponible__lte=5).count()
    
    # Ventas por día (últimos 30 días)
    fecha_inicio = timezone.now() - timedelta(days=30)
    ventas_recientes = Pedido.objects.filter(
        fecha_pedido__gte=fecha_inicio,
        estado='ENTR'
    ).order_by('fecha_pedido')
    
    # Últimos pedidos
    ultimos_pedidos = Pedido.objects.exclude(estado='CARRITO').order_by(
        '-fecha_pedido'
    )[:10]
    
    context = {
        'total_ventas': total_ventas,
        'pedidos_pendientes': pedidos_pendientes,
        'stock_bajo': stock_bajo,
        'ventas_recientes': ventas_recientes,
        'ultimos_pedidos': ultimos_pedidos,
    }
    return render(request, 'dashboard/index.html', context)

@staff_required
def lista_admin(request, model_name):
    """Vista genérica para listar objetos de cualquier modelo"""
    
    # Mapeo de nombres de modelo a clases
    model_map = {
        'carta': Carta,
        'expansion': Expansion,
        'categoria': Categoria,
        'pedido': Pedido,
        'inventario': Inventario,
        'resena': Resena,
        'coleccion': Coleccion,
        'usuario': User,
    }
    
    if model_name not in model_map:
        messages.error(request, f'Modelo {model_name} no encontrado')
        return redirect('admin_dashboard')
    
    model_class = model_map[model_name]
    
    # Filtrar por búsqueda
    query = request.GET.get('q', '')
    objetos = model_class.objects.all()
    
    if query:
        # Búsqueda genérica por campos comunes
        if hasattr(model_class, 'nombre'):
            objetos = objetos.filter(nombre__icontains=query)
        elif hasattr(model_class, 'username'):
            objetos = objetos.filter(username__icontains=query)
        elif hasattr(model_class, 'codigo'):
            objetos = objetos.filter(codigo__icontains=query)
    
    # Paginación
    paginator = Paginator(objetos, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener campos para mostrar en la tabla
    campos = []
    if objetos.exists():
        obj = objetos.first()
        campos = [field.name for field in obj._meta.fields[:5]]  # Primeros 5 campos
    
    context = {
        'model_name': model_name,
        'model_name_display': model_class._meta.verbose_name_plural,
        'page_obj': page_obj,
        'campos': campos,
        'query': query,
    }
    return render(request, 'admin/lista.html', context)

@staff_required
def detalle_admin(request, model_name, obj_id):
    """Vista genérica para ver detalle de un objeto"""
    
    model_map = {
        'carta': Carta,
        'expansion': Expansion,
        'categoria': Categoria,
        'pedido': Pedido,
        'inventario': Inventario,
        'resena': Resena,
        'coleccion': Coleccion,
        'usuario': User,
    }
    
    if model_name not in model_map:
        messages.error(request, f'Modelo {model_name} no encontrado')
        return redirect('admin_dashboard')
    
    model_class = model_map[model_name]
    objeto = get_object_or_404(model_class, id=obj_id)
    
    context = {
        'model_name': model_name,
        'model_name_display': model_class._meta.verbose_name,
        'objeto': objeto,
    }
    return render(request, 'admin/detalle.html', context)

@staff_required
def crear_admin(request, model_name):
    """Vista genérica para crear un objeto usando formularios de Django"""
    
    model_map = {
        'carta': Carta,
        'expansion': Expansion,
        'categoria': Categoria,
        'inventario': Inventario,
        'resena': Resena,
        'coleccion': Coleccion,
    }
    
    if model_name not in model_map:
        messages.error(request, f'Modelo {model_name} no encontrado')
        return redirect('admin_dashboard')
    
    model_class = model_map[model_name]
    
    # Crear formulario dinámico
    class DynamicForm(forms.ModelForm):
        class Meta:
            model = model_class
            fields = '__all__'
            
            # Widgets personalizados
            widgets = {
                'descripcion': forms.Textarea(attrs={'rows': 3}),
                'comentario': forms.Textarea(attrs={'rows': 3}),
                'notas': forms.Textarea(attrs={'rows': 3}),
                'direccion': forms.Textarea(attrs={'rows': 2}),
            }
    
    if request.method == 'POST':
        form = DynamicForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'{model_class._meta.verbose_name} creado exitosamente')
            return redirect('detalle_admin', model_name=model_name, obj_id=obj.id)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario')
    else:
        form = DynamicForm()
    
    context = {
        'model_name': model_name,
        'model_name_display': f'Crear {model_class._meta.verbose_name}',
        'form': form,  # ¡ESTO ES LO QUE FALTABA!
        'action': 'crear',
    }
    
    # Pasar datos adicionales según el modelo
    if model_name == 'carta':
        context['expansions'] = Expansion.objects.all()
        context['categorias'] = Categoria.objects.all()
    elif model_name == 'inventario':
        context['cartas'] = Carta.objects.all()
    
    return render(request, 'admin/formulario.html', context)

@staff_required
def editar_admin(request, model_name, obj_id):
    """Vista genérica para editar un objeto usando formularios de Django"""
    
    model_map = {
        'carta': Carta,
        'expansion': Expansion,
        'categoria': Categoria,
        'pedido': Pedido,
        'inventario': Inventario,
        'resena': Resena,
        'coleccion': Coleccion,
        'usuario': User,
    }
    
    if model_name not in model_map:
        messages.error(request, f'Modelo {model_name} no encontrado')
        return redirect('admin_dashboard')
    
    model_class = model_map[model_name]
    objeto = get_object_or_404(model_class, id=obj_id)
    
    # Crear formulario dinámico
    class DynamicForm(forms.ModelForm):
        class Meta:
            model = model_class
            fields = '__all__'
            
            # Widgets personalizados para campos específicos
            widgets = {
                'descripcion': forms.Textarea(attrs={'rows': 3}),
                'comentario': forms.Textarea(attrs={'rows': 3}),
                'notas': forms.Textarea(attrs={'rows': 3}),
                'direccion': forms.Textarea(attrs={'rows': 2}),
            }
    
    if request.method == 'POST':
        form = DynamicForm(request.POST, request.FILES, instance=objeto)
        if form.is_valid():
            form.save()
            messages.success(request, f'{model_class._meta.verbose_name} actualizado exitosamente')
            return redirect('detalle_admin', model_name=model_name, obj_id=obj_id)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario')
    else:
        form = DynamicForm(instance=objeto)
    
    context = {
        'model_name': model_name,
        'model_name_display': f'Editar {model_class._meta.verbose_name}',
        'objeto': objeto,
        'form': form,  # ¡ESTO ES LO QUE FALTABA!
        'action': 'editar',
    }
    
    # Pasar datos adicionales según el modelo
    if model_name == 'carta':
        context['expansions'] = Expansion.objects.all()
        context['categorias'] = Categoria.objects.all()
    elif model_name == 'inventario':
        context['cartas'] = Carta.objects.all()
    elif model_name == 'pedido':
        context['estados'] = Pedido.ESTADOS
        context['metodos_pago'] = Pedido.METODOS_PAGO
    
    return render(request, 'admin/formulario.html', context)

@staff_required
def eliminar_admin(request, model_name, obj_id):
    """Vista genérica para confirmar eliminación"""
    
    model_map = {
        'carta': Carta,
        'expansion': Expansion,
        'categoria': Categoria,
        'pedido': Pedido,
        'inventario': Inventario,
        'resena': Resena,
        'coleccion': Coleccion,
    }
    
    if model_name not in model_map:
        messages.error(request, f'Modelo {model_name} no encontrado')
        return redirect('admin_dashboard')
    
    model_class = model_map[model_name]
    objeto = get_object_or_404(model_class, id=obj_id)
    
    if request.method == 'POST':
        try:
            objeto_nombre = str(objeto)
            objeto.delete()
            messages.success(request, f'{model_class._meta.verbose_name} "{objeto_nombre}" eliminado exitosamente')
            return redirect('lista_admin', model_name=model_name)
        except Exception as e:
            messages.error(request, f'Error al eliminar: {str(e)}')
            return redirect('detalle_admin', model_name=model_name, obj_id=obj_id)
    
    context = {
        'model_name': model_name,
        'model_name_display': model_class._meta.verbose_name,
        'objeto': objeto,
    }
    return render(request, 'admin/confirmar_eliminar.html', context)

@staff_required
def confirmar_pedido(request, pedido_id):
    """Confirmar un pedido pendiente"""
    pedido = get_object_or_404(Pedido, numero_pedido=pedido_id)
    
    if pedido.estado == 'PEND':
        pedido.estado = 'PROC'
        pedido.save()
        messages.success(request, f'Pedido #{pedido.numero_pedido} confirmado y en proceso')
    else:
        messages.warning(request, 'El pedido no está en estado pendiente')
    
    return redirect('detalle_admin', model_name='pedido', obj_id=pedido.id)

@staff_required
def marcar_enviado(request, pedido_id):
    """Marcar un pedido como enviado"""
    pedido = get_object_or_404(Pedido, numero_pedido=pedido_id)
    
    if pedido.estado == 'PROC':
        pedido.estado = 'ENVI'
        pedido.fecha_envio = timezone.now()
        pedido.numero_seguimiento = request.POST.get('numero_seguimiento', '')
        pedido.save()
        messages.success(request, f'Pedido #{pedido.numero_pedido} marcado como enviado')
    else:
        messages.warning(request, 'El pedido no está en proceso')
    
    return redirect('detalle_admin', model_name='pedido', obj_id=pedido.id)

@staff_required
def marcar_completado(request, pedido_id):
    """Marcar un pedido como completado"""
    pedido = get_object_or_404(Pedido, numero_pedido=pedido_id)
    
    if pedido.estado == 'ENVI':
        pedido.estado = 'ENTR'
        pedido.save()
        messages.success(request, f'Pedido #{pedido.numero_pedido} marcado como entregado')
    else:
        messages.warning(request, 'El pedido no está enviado')
    
    return redirect('detalle_admin', model_name='pedido', obj_id=pedido.id)