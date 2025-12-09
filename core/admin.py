# core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Avg
from .models import (
    Categoria, Expansion, Carta, Inventario,
    Pedido, ItemPedido, Resena, Coleccion, ColeccionCarta
)


# =========== CATEGORIA ===========
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'get_total_cartas', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'get_total_cartas']
    
    def get_total_cartas(self, obj):
        return obj.cartas.count()
    get_total_cartas.short_description = 'Total Cartas'


# =========== EXPANSION ===========
@admin.register(Expansion)
class ExpansionAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'fecha_lanzamiento', 'get_cartas_count', 'activa', 'get_simbolo']
    list_filter = ['activa', 'fecha_lanzamiento']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['get_cartas_count', 'get_simbolo']
    
    def get_cartas_count(self, obj):
        return obj.cartas.count()
    get_cartas_count.short_description = 'Cartas'
    
    def get_simbolo(self, obj):
        if obj.simbolo:
            return format_html('<img src="{}" width="50" height="50" />', obj.simbolo.url)
        return "-"
    get_simbolo.short_description = 'Símbolo'


# =========== INVENTARIO INLINE ===========
class InventarioInline(admin.StackedInline):
    model = Inventario
    extra = 0
    fields = ['cantidad_disponible', 'cantidad_reservada', 'precio', 'precio_promocional', 'en_promocion']
    readonly_fields = ['stock_real', 'disponible']


# =========== CARTA ===========
@admin.register(Carta)
class CartaAdmin(admin.ModelAdmin):
    list_display = [
        'get_miniatura', 'codigo', 'nombre', 'expansion',
        'get_tipo', 'rareza', 'get_precio_estimado', 'coleccionable'
    ]
    list_filter = ['tipo', 'rareza', 'expansion', 'coleccionable']
    search_fields = ['codigo', 'nombre', 'descripcion', 'expansion__nombre']
    readonly_fields = [
        'fecha_creacion', 'fecha_actualizacion',
        'get_precio_estimado', 'get_preview', 'popularidad'
    ]
    list_per_page = 20
    inlines = [InventarioInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'codigo', 'nombre', 'numero_en_expansion', 'descripcion',
                'expansion', 'categoria', 'coleccionable'
            )
        }),
        ('Atributos', {
            'fields': (
                'tipo', 'tipo_secundario', 'hp',
                'rareza', 'condicion', 'es_holo', 'primera_edicion', 'idioma'
            )
        }),
        ('Estadísticas', {
            'fields': ('popularidad', 'get_precio_estimado')
        }),
        ('Imágenes', {
            'fields': ('imagen_frontal', 'get_preview', 'imagen_trasera')
        }),
    )
    
    def get_miniatura(self, obj):
        if obj.imagen_frontal:
            return format_html(
                '<img src="{}" width="50" height="70" style="object-fit: cover;" />',
                obj.imagen_frontal.url
            )
        return "-"
    get_miniatura.short_description = ''
    
    def get_preview(self, obj):
        if obj.imagen_frontal:
            return format_html(
                '<img src="{}" width="200" height="280" style="object-fit: cover;" />',
                obj.imagen_frontal.url
            )
        return "Sin imagen"
    get_preview.short_description = 'Vista Previa'
    
    def get_tipo(self, obj):
        if obj.tipo_secundario:
            return f"{obj.tipo}/{obj.tipo_secundario}"
        return obj.tipo or "-"
    get_tipo.short_description = 'Tipo'
    
    def get_precio_estimado(self, obj):
        return f"{obj.precio_estimado}€"
    get_precio_estimado.short_description = 'Valor Estimado'
    
    actions = ['aumentar_popularidad']
    
    def aumentar_popularidad(self, request, queryset):
        for carta in queryset:
            carta.aumentar_popularidad(10)
        self.message_user(request, f'Popularidad aumentada para {queryset.count()} cartas')


# =========== INVENTARIO ===========
@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = [
        'get_carta', 'precio_actual', 'stock_real',
        'vendidos_total', 'valoracion_promedio', 'en_promocion'
    ]
    list_filter = ['en_promocion', 'fecha_ingreso']
    search_fields = ['carta__nombre', 'carta__codigo']
    readonly_fields = [
        'stock_real', 'disponible', 'ultima_actualizacion',
        'precio_actual', 'get_carta_link'
    ]
    
    fieldsets = (
        ('Información', {
            'fields': ('carta', 'get_carta_link')
        }),
        ('Stock', {
            'fields': ('cantidad_disponible', 'cantidad_reservada', 'stock_real', 'disponible')
        }),
        ('Precios', {
            'fields': ('precio', 'precio_promocional', 'en_promocion', 'precio_actual')
        }),
        ('Estadísticas', {
            'fields': ('vendidos_total', 'valoracion_promedio')
        }),
    )
    
    def get_carta(self, obj):
        return obj.carta.nombre
    get_carta.short_description = 'Carta'
    get_carta.admin_order_field = 'carta__nombre'
    
    def get_carta_link(self, obj):
        if obj.carta:
            url = reverse('admin:core_carta_change', args=[obj.carta.id])
            return format_html('<a href="{}">Ver detalles de la carta</a>', url)
        return "-"
    get_carta_link.short_description = 'Enlace'
    
    actions = ['activar_promocion', 'desactivar_promocion']
    
    def activar_promocion(self, request, queryset):
        queryset.update(en_promocion=True)
        self.message_user(request, f'{queryset.count()} productos en promoción')
    
    def desactivar_promocion(self, request, queryset):
        queryset.update(en_promocion=False)
        self.message_user(request, f'{queryset.count()} productos fuera de promoción')


# =========== ITEM PEDIDO INLINE ===========
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ['get_carta_info', 'get_precio', 'get_subtotal_display']
    fields = ['get_carta_info', 'cantidad', 'get_precio', 'get_subtotal_display']
    
    def get_carta_info(self, obj):
        if obj.carta:
            return format_html('<strong>{}</strong>', obj.carta.nombre)
        return "-"
    get_carta_info.short_description = 'Carta'
    
    def get_precio(self, obj):
        return f"{obj.precio_unitario}€"
    get_precio.short_description = 'Precio Unitario'
    
    def get_subtotal_display(self, obj):
        return f"{obj.subtotal}€"
    get_subtotal_display.short_description = 'Subtotal'


# =========== PEDIDO ===========
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_pedido', 'cliente', 'estado', 'fecha_pedido',
        'get_subtotal', 'get_total', 'cantidad_items'
    ]
    list_filter = ['estado', 'fecha_pedido', 'metodo_pago']
    search_fields = ['numero_pedido', 'cliente__username', 'cliente__email', 'nombre_completo']
    readonly_fields = [
        'numero_pedido', 'fecha_pedido', 'fecha_pago', 'fecha_envio', 'fecha_entrega',
        'get_subtotal', 'get_envio', 'get_impuestos', 'get_total',
        'cantidad_items', 'envio_gratis'
    ]
    inlines = [ItemPedidoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'numero_pedido', 'cliente', 'estado',
                'fecha_pedido', 'fecha_pago', 'fecha_envio', 'fecha_entrega'
            )
        }),
        ('Información de Envío', {
            'fields': (
                'nombre_completo', 'email', 'telefono',
                'direccion', 'ciudad', 'provincia', 'codigo_postal', 'pais'
            )
        }),
        ('Pago', {
            'fields': ('metodo_pago', 'descuento')
        }),
        ('Totales', {
            'fields': (
                'get_subtotal', 'get_envio', 'get_impuestos',
                'get_total', 'cantidad_items', 'envio_gratis'
            )
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
    )
    
    def get_subtotal(self, obj):
        return f"{obj.subtotal}€"
    get_subtotal.short_description = 'Subtotal'
    
    def get_envio(self, obj):
        return f"{obj.envio}€"
    get_envio.short_description = 'Envío'
    
    def get_impuestos(self, obj):
        return f"{obj.impuestos}€"
    get_impuestos.short_description = 'Impuestos'
    
    def get_total(self, obj):
        return f"{obj.total}€"
    get_total.short_description = 'Total'
    
    actions = [
        'marcar_como_pagado', 'marcar_como_enviado',
        'marcar_como_entregado', 'marcar_como_cancelado'
    ]
    
    def marcar_como_pagado(self, request, queryset):
        queryset.update(estado='PAGADO')
        self.message_user(request, f'{queryset.count()} pedidos marcados como pagados')
    
    def marcar_como_enviado(self, request, queryset):
        queryset.update(estado='ENVIADO')
        self.message_user(request, f'{queryset.count()} pedidos marcados como enviados')
    
    def marcar_como_entregado(self, request, queryset):
        queryset.update(estado='ENTREGADO')
        self.message_user(request, f'{queryset.count()} pedidos marcados como entregados')
    
    def marcar_como_cancelado(self, request, queryset):
        queryset.update(estado='CANCELADO')
        self.message_user(request, f'{queryset.count()} pedidos marcados como cancelados')


# =========== ITEM PEDIDO ===========
@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'get_pedido', 'get_carta',
        'cantidad', 'get_precio_unitario', 'get_subtotal'
    ]
    list_filter = ['pedido__estado']
    search_fields = ['carta__nombre', 'pedido__numero_pedido']
    readonly_fields = [
        'get_pedido_info', 'get_carta_info',
        'get_precio_unitario_display', 'get_subtotal_display'
    ]
    
    def get_pedido(self, obj):
        return str(obj.pedido.numero_pedido)
    get_pedido.short_description = 'Pedido'
    
    def get_carta(self, obj):
        return obj.carta.nombre
    get_carta.short_description = 'Carta'
    
    def get_precio_unitario(self, obj):
        return f"{obj.precio_unitario}€"
    get_precio_unitario.short_description = 'Precio'
    
    def get_subtotal(self, obj):
        return f"{obj.subtotal}€"
    get_subtotal.short_description = 'Subtotal'
    
    def get_pedido_info(self, obj):
        return f"Pedido #{obj.pedido.numero_pedido}"
    get_pedido_info.short_description = 'Pedido'
    
    def get_carta_info(self, obj):
        if obj.carta:
            url = reverse('admin:core_carta_change', args=[obj.carta.id])
            return format_html('<a href="{}">{}</a>', url, obj.carta.nombre)
        return "-"
    get_carta_info.short_description = 'Carta'
    
    def get_precio_unitario_display(self, obj):
        return f"{obj.precio_unitario}€"
    get_precio_unitario_display.short_description = 'Precio Unitario'
    
    def get_subtotal_display(self, obj):
        return f"{obj.subtotal}€"
    get_subtotal_display.short_description = 'Subtotal'


# =========== RESENA ===========
@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = [
        'get_carta', 'get_usuario', 'valoracion',
        'fecha_creacion', 'aprobada', 'recomendado', 'utilidad'
    ]
    list_filter = ['valoracion', 'aprobada', 'recomendado', 'fecha_creacion']
    search_fields = ['carta__nombre', 'usuario__username', 'titulo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'utilidad']
    
    def get_carta(self, obj):
        return obj.carta.nombre
    get_carta.short_description = 'Carta'
    
    def get_usuario(self, obj):
        return obj.usuario.username
    get_usuario.short_description = 'Usuario'
    
    actions = ['aprobar_resenas', 'rechazar_resenas']
    
    def aprobar_resenas(self, request, queryset):
        queryset.update(aprobada=True)
        self.message_user(request, f'{queryset.count()} reseñas aprobadas')
    
    def rechazar_resenas(self, request, queryset):
        queryset.update(aprobada=False)
        self.message_user(request, f'{queryset.count()} reseñas rechazadas')


# =========== COLECCION CARTA INLINE ===========
class ColeccionCartaInline(admin.TabularInline):
    model = ColeccionCarta
    extra = 0
    readonly_fields = ['get_valor_estimado']
    fields = ['carta', 'cantidad', 'estado', 'notas', 'get_valor_estimado']
    
    def get_valor_estimado(self, obj):
        return f"{obj.carta.precio_estimado}€"
    get_valor_estimado.short_description = 'Valor Unitario'


# =========== COLECCION ===========
@admin.register(Coleccion)
class ColeccionAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'get_usuario', 'publica',
        'get_total_cartas', 'get_valor_estimado', 'fecha_creacion'
    ]
    list_filter = ['publica', 'fecha_creacion', 'usuario']
    search_fields = ['nombre', 'usuario__username', 'descripcion']
    readonly_fields = [
        'fecha_creacion', 'fecha_actualizacion',
        'get_total_cartas', 'get_valor_estimado'
    ]
    inlines = [ColeccionCartaInline]
    
    def get_usuario(self, obj):
        return obj.usuario.username
    get_usuario.short_description = 'Usuario'
    
    def get_total_cartas(self, obj):
        return obj.total_cartas
    get_total_cartas.short_description = 'Total Cartas'
    
    def get_valor_estimado(self, obj):
        return f"{obj.valor_estimado:.2f}€"
    get_valor_estimado.short_description = 'Valor Estimado'


# =========== COLECCION CARTA ===========
@admin.register(ColeccionCarta)
class ColeccionCartaAdmin(admin.ModelAdmin):
    list_display = [
        'get_coleccion', 'get_carta', 'cantidad',
        'estado', 'fecha_agregado'
    ]
    list_filter = ['estado', 'fecha_agregado']
    search_fields = ['coleccion__nombre', 'carta__nombre']
    readonly_fields = ['fecha_agregado', 'get_coleccion_link', 'get_carta_link']
    
    def get_coleccion(self, obj):
        return obj.coleccion.nombre
    get_coleccion.short_description = 'Colección'
    
    def get_carta(self, obj):
        return obj.carta.nombre
    get_carta.short_description = 'Carta'
    
    def get_coleccion_link(self, obj):
        if obj.coleccion:
            url = reverse('admin:core_coleccion_change', args=[obj.coleccion.id])
            return format_html('<a href="{}">{}</a>', url, obj.coleccion.nombre)
        return "-"
    get_coleccion_link.short_description = 'Ver Colección'
    
    def get_carta_link(self, obj):
        if obj.carta:
            url = reverse('admin:core_carta_change', args=[obj.carta.id])
            return format_html('<a href="{}">{}</a>', url, obj.carta.nombre)
        return "-"
    get_carta_link.short_description = 'Ver Carta'


# Personalización del sitio admin
admin.site.site_header = "🏆 Pokémon TCG Store - Administración"
admin.site.site_title = "Pokémon TCG Admin"
admin.site.index_title = "📊 Panel de Control"