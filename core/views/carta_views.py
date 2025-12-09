from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from ..models import Carta, Categoria, Expansion, Coleccion, ColeccionCarta

def home_view(request):
    """Vista principal/presentación del sitio - VERSIÓN CORREGIDA"""
    try:
        # Cartas destacadas (las más populares) - CORREGIDO
        cartas_destacadas = Carta.objects.filter(
            coleccionable=True
        ).select_related('inventario', 'expansion').order_by('-popularidad')[:6]
        
        # Nuevas llegadas
        nuevas_cartas = Carta.objects.filter(
            coleccionable=True
        ).select_related('inventario', 'expansion').order_by('-fecha_creacion')[:4]
        
        # Ofertas especiales
        cartas_oferta = Carta.objects.filter(
            inventario__en_promocion=True,
            coleccionable=True
        ).select_related('inventario', 'expansion')[:3]
        
        # Estadísticas
        total_cartas = Carta.objects.filter(coleccionable=True).count()
        total_expansiones = Expansion.objects.filter(activa=True).count()
        categorias = Categoria.objects.all()[:6]
        
        # Obtener categorías para el menú
        categorias_menu = Categoria.objects.all()[:10]
        
    except Exception as e:
        # En caso de error
        cartas_destacadas = []
        nuevas_cartas = []
        cartas_oferta = []
        total_cartas = 0
        total_expansiones = 0
        categorias = []
        categorias_menu = []
    
    context = {
        'cartas_destacadas': cartas_destacadas,
        'nuevas_cartas': nuevas_cartas,
        'cartas_oferta': cartas_oferta,
        'total_cartas': total_cartas,
        'total_expansiones': total_expansiones,
        'categorias': categorias,
        'categorias_menu': categorias_menu,  # Añade esto
    }
    return render(request, 'index.html', context)

def lista_cartas(request):
    """Lista completa de cartas con filtros - VERSIÓN MEJORADA"""
    try:
        # Obtener cartas con inventario
        cartas = Carta.objects.filter(
            coleccionable=True
        ).select_related('expansion', 'inventario', 'categoria')
        
        # Aplicar filtros
        tipo = request.GET.get('tipo')
        rareza = request.GET.get('rareza')
        expansion_id = request.GET.get('expansion')
        categoria_id = request.GET.get('categoria')  # Nuevo filtro de categoría
        query = request.GET.get('q', '')
        
        if query:
            cartas = cartas.filter(
                Q(nombre__icontains=query) |
                Q(descripcion__icontains=query) |
                Q(codigo__icontains=query)
            )
        
        if tipo and tipo != 'all':
            cartas = cartas.filter(Q(tipo=tipo) | Q(tipo_secundario=tipo))
        
        if rareza and rareza != 'all':
            cartas = cartas.filter(rareza=rareza)
        
        if expansion_id and expansion_id != 'all':
            cartas = cartas.filter(expansion_id=expansion_id)
        
        if categoria_id and categoria_id != 'all':  # Nuevo filtro
            cartas = cartas.filter(categoria_id=categoria_id)
        
        # Ordenamiento
        orden = request.GET.get('orden', 'nombre')
        
        if orden == 'precio_asc':
            cartas = cartas.order_by('inventario__precio')
        elif orden == 'precio_desc':
            cartas = cartas.order_by('-inventario__precio')
        elif orden == 'nombre':
            cartas = cartas.order_by('nombre')
        elif orden == 'nuevo':
            cartas = cartas.order_by('-fecha_creacion')
        elif orden == 'popularidad':
            cartas = cartas.order_by('-popularidad')
        else:
            cartas = cartas.order_by('nombre')
        
        # Paginación
        from django.core.paginator import Paginator
        paginator = Paginator(cartas, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Obtener opciones de filtro
        tipos = Carta.TIPOS_POKEMON
        rarezas = Carta.RAREZAS
        expansiones = Expansion.objects.filter(activa=True)
        categorias = Categoria.objects.all()  # Obtener todas las categorías
        
        context = {
            'cartas': page_obj,
            'tipos': tipos,
            'rarezas': rarezas,
            'expansiones': expansiones,
            'categorias': categorias,  # Añadir al contexto
            'filtros_activos': {
                'tipo': tipo,
                'rareza': rareza,
                'expansion': expansion_id,
                'categoria': categoria_id,  # Añadir al estado de filtros
                'query': query,
                'orden': orden,
            }
        }
        return render(request, 'cartas/lista.html', context)
        
    except Exception as e:
        # En caso de error, mostrar cartas básicas
        cartas = Carta.objects.filter(coleccionable=True)[:12]
        context = {
            'cartas': cartas,
            'tipos': Carta.TIPOS_POKEMON,
            'rarezas': Carta.RAREZAS,
            'expansiones': Expansion.objects.filter(activa=True),
            'categorias': Categoria.objects.all(),  # Añadir también aquí
            'error': str(e)
        }
        return render(request, 'cartas/lista.html', context)

def detalle_carta(request, carta_id):
    """Vista detallada de una carta"""
    carta = get_object_or_404(
        Carta.objects.select_related('expansion', 'inventario', 'categoria'),
        id=carta_id
    )
    
    # Incrementar popularidad
    if hasattr(carta, 'inventario'):
        carta.inventario.save()
    
    # Cartas relacionadas
    cartas_relacionadas = Carta.objects.filter(
        Q(expansion=carta.expansion) | Q(tipo=carta.tipo) | Q(rareza=carta.rareza)
    ).exclude(id=carta.id)[:4]
    
    # Reseñas aprobadas
    reseñas = carta.resenas.filter(aprobada=True)[:5]
    
    context = {
        'carta': carta,
        'cartas_relacionadas': cartas_relacionadas,
        'resenas': reseñas,
    }
    return render(request, 'cartas/detalle.html', context)

def filtrar_cartas(request):
    """Vista para filtrar cartas (AJAX o normal) - VERSIÓN CORREGIDA"""
    # Obtener parámetros de filtro
    tipo = request.GET.get('tipo', '')
    rareza = request.GET.get('rareza', '')
    expansion_id = request.GET.get('expansion', '')
    categoria_id = request.GET.get('categoria', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    orden = request.GET.get('orden', 'nombre')
    query = request.GET.get('q', '')
    
    # Inicializar queryset
    cartas = Carta.objects.filter(
        coleccionable=True
    ).select_related('expansion', 'inventario', 'categoria')
    
    # Aplicar filtros
    if query:
        cartas = cartas.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(codigo__icontains=query)
        )
    
    if tipo and tipo != 'all':
        cartas = cartas.filter(Q(tipo=tipo) | Q(tipo_secundario=tipo))
    
    if rareza and rareza != 'all':
        cartas = cartas.filter(rareza=rareza)
    
    if expansion_id and expansion_id != 'all':
        cartas = cartas.filter(expansion_id=expansion_id)
    
    if categoria_id and categoria_id != 'all':
        cartas = cartas.filter(categoria_id=categoria_id)
    
    # Filtrar por precio si existe
    if precio_min:
        try:
            precio_min_val = float(precio_min)
            cartas = cartas.filter(inventario__precio__gte=precio_min_val)
        except ValueError:
            pass
    
    if precio_max:
        try:
            precio_max_val = float(precio_max)
            cartas = cartas.filter(inventario__precio__lte=precio_max_val)
        except ValueError:
            pass
    
    # Ordenamiento
    orden_map = {
        'nombre': 'nombre',
        'precio_asc': 'inventario__precio',
        'precio_desc': '-inventario__precio',
        'nuevo': '-fecha_creacion',
        'popularidad': '-popularidad',
        'rareza': 'rareza',
    }
    
    order_field = orden_map.get(orden, 'nombre')
    cartas = cartas.order_by(order_field)
    
    # Verificar si es una solicitud AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Preparar datos para respuesta JSON
        data = []
        for carta in cartas[:20]:  # Limitar a 20 resultados para AJAX
            data.append({
                'id': carta.id,
                'nombre': carta.nombre,
                'precio': str(carta.inventario.precio_actual) if carta.inventario else '0.00',
                'imagen': carta.imagen_frontal.url if carta.imagen_frontal else '',
                'tipo': carta.tipo or '',
                'rareza': carta.rareza,
                'expansion': carta.expansion.nombre if carta.expansion else '',
                'url': f'/cartas/{carta.id}/',  # Simplificado
            })
        
        return JsonResponse({'cartas': data})
    
    # Si NO es AJAX, renderizar template HTML
    # Paginación para vista normal
    from django.core.paginator import Paginator
    paginator = Paginator(cartas, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener opciones de filtro
    tipos = Carta.TIPOS_POKEMON
    rarezas = Carta.RAREZAS
    expansiones = Expansion.objects.filter(activa=True)
    
    # CORRECCIÓN: Usar 'cartas' en lugar de 'carta' para el related_name
    from django.db.models import Count
    categorias = Categoria.objects.annotate(
        num_cartas=Count('cartas')  # CAMBIO: 'cartas' en plural
    )
    
    context = {
        'cartas': page_obj,
        'tipos': tipos,
        'rarezas': rarezas,
        'expansiones': expansiones,
        'categorias': categorias,
        'filtros_activos': {
            'tipo': tipo,
            'rareza': rareza,
            'expansion': expansion_id,
            'categoria': categoria_id,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'orden': orden,
            'query': query,
        },
        'resultados_count': cartas.count(),
    }
    
    # Renderizar el template de búsqueda
    return render(request, 'cartas/buscar.html', context)

@login_required
def wishlist_view(request):
    """Vista de la wishlist del usuario"""
    try:
        wishlist, created = Coleccion.objects.get_or_create(
            usuario=request.user,
            nombre='Wishlist',
            defaults={'descripcion': 'Mis cartas deseadas', 'publica': False}
        )
        cartas_wishlist = wishlist.cartas.all().select_related('carta__inventario')
    except:
        cartas_wishlist = []
    
    context = {
        'wishlist': cartas_wishlist,
    }
    return render(request, 'cartas/wishlist.html', context)

@login_required
def agregar_wishlist(request, carta_id):
    """Agregar carta a wishlist"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        carta = get_object_or_404(Carta, id=carta_id)
        
        try:
            wishlist, created = Coleccion.objects.get_or_create(
                usuario=request.user,
                nombre='Wishlist',
                defaults={'descripcion': 'Mis cartas deseadas', 'publica': False}
            )
            
            # Verificar si ya está en la wishlist
            if not wishlist.cartas.filter(carta=carta).exists():
                ColeccionCarta.objects.create(
                    coleccion=wishlist,
                    carta=carta,
                    cantidad=1
                )
                wishlist.actualizar_estadisticas()
                return JsonResponse({'success': True, 'message': 'Carta añadida a wishlist'})
            else:
                return JsonResponse({'success': False, 'message': 'La carta ya está en tu wishlist'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'error': 'Solicitud no válida'}, status=400)

@login_required
def eliminar_wishlist(request, carta_id):
    """Eliminar carta de wishlist"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        carta = get_object_or_404(Carta, id=carta_id)
        
        try:
            wishlist = Coleccion.objects.get(
                usuario=request.user,
                nombre='Wishlist'
            )
            item = wishlist.cartas.filter(carta=carta).first()
            if item:
                item.delete()
                wishlist.actualizar_estadisticas()
                return JsonResponse({'success': True, 'message': 'Carta eliminada de wishlist'})
            else:
                return JsonResponse({'success': False, 'message': 'Carta no encontrada en wishlist'})
        except Coleccion.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No tienes wishlist'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'error': 'Solicitud no válida'}, status=400)

# core/views/carta_views.py - Agrega esta función:
def buscar_cartas(request):
    """Vista para buscar cartas"""
    query = request.GET.get('q', '')
    
    if query:
        cartas = Carta.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(tipo__icontains=query)
        ).select_related('inventario', 'expansion')
    else:
        cartas = Carta.objects.none()
    
    context = {
        'cartas': cartas,
        'query': query,
        'resultados_count': cartas.count(),
    }
    return render(request, 'cartas/buscar.html', context)

# En carta_views.py, añade esta función al final:

def buscar_cartas(request):
    """Vista para buscar cartas con filtros avanzados"""
    query = request.GET.get('q', '').strip()
    
    # Inicializar queryset
    cartas = Carta.objects.filter(coleccionable=True).select_related('inventario', 'expansion', 'categoria')
    
    # Búsqueda por texto
    if query:
        cartas = cartas.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(codigo__icontains=query) |
            Q(expansion__nombre__icontains=query)
        )
    
    # Aplicar filtros adicionales si existen
    tipo = request.GET.get('tipo')
    rareza = request.GET.get('rareza')
    expansion_id = request.GET.get('expansion')
    categoria_id = request.GET.get('categoria')
    
    if tipo and tipo != 'all':
        cartas = cartas.filter(Q(tipo=tipo) | Q(tipo_secundario=tipo))
    
    if rareza and rareza != 'all':
        cartas = cartas.filter(rareza=rareza)
    
    if expansion_id and expansion_id != 'all':
        cartas = cartas.filter(expansion_id=expansion_id)
    
    if categoria_id and categoria_id != 'all':
        cartas = cartas.filter(categoria_id=categoria_id)
    
    # Ordenamiento
    orden = request.GET.get('orden', 'nombre')
    orden_map = {
        'nombre': 'nombre',
        'precio_asc': 'inventario__precio',
        'precio_desc': '-inventario__precio',
        'nuevo': '-fecha_creacion',
        'popularidad': '-popularidad',
        'rareza': 'rareza',
    }
    
    order_field = orden_map.get(orden, 'nombre')
    cartas = cartas.order_by(order_field)
    
    # Obtener datos para los filtros
    categorias = Categoria.objects.all()
    tipos = Carta.TIPOS_POKEMON
    rarezas = Carta.RAREZAS
    expansiones = Expansion.objects.filter(activa=True)
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(cartas, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'cartas': page_obj,
        'query': query,
        'categorias': categorias,
        'tipos': tipos,
        'rarezas': rarezas,
        'expansiones': expansiones,
        'filtros_activos': {
            'tipo': tipo,
            'rareza': rareza,
            'expansion': expansion_id,
            'categoria': categoria_id,
            'orden': orden,
            'query': query,
        },
        'resultados_count': cartas.count(),
    }
    
    return render(request, 'cartas/buscar.html', context)