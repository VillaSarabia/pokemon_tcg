# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from decimal import Decimal
from django.utils import timezone


class Categoria(models.Model):
    """Modelo para categorías de cartas Pokémon"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    icono = models.CharField(max_length=50, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    @property
    def total_cartas(self):
        """Total de cartas en esta categoría"""
        return self.cartas.count()


class Expansion(models.Model):
    """Modelo para las expansiones/sets de cartas Pokémon"""
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=200)
    fecha_lanzamiento = models.DateField()
    total_cartas = models.PositiveIntegerField()
    simbolo = models.ImageField(upload_to='expansiones/simbolos/', blank=True, null=True)
    activa = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Expansión"
        verbose_name_plural = "Expansiones"
        ordering = ['-fecha_lanzamiento']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def cartas_count(self):
        """Número real de cartas en esta expansión"""
        return self.cartas.count()


class Carta(models.Model):
    """Modelo principal para las cartas Pokémon"""
    
    # Tipos Pokémon
    TIPOS_POKEMON = [
        ('Normal', 'Normal'),
        ('Fuego', 'Fuego'),
        ('Agua', 'Agua'),
        ('Planta', 'Planta'),
        ('Eléctrico', 'Eléctrico'),
        ('Hielo', 'Hielo'),
        ('Lucha', 'Lucha'),
        ('Veneno', 'Veneno'),
        ('Tierra', 'Tierra'),
        ('Volador', 'Volador'),
        ('Psíquico', 'Psíquico'),
        ('Bicho', 'Bicho'),
        ('Roca', 'Roca'),
        ('Fantasma', 'Fantasma'),
        ('Dragón', 'Dragón'),
        ('Siniestro', 'Siniestro'),
        ('Acero', 'Acero'),
        ('Hada', 'Hada'),
        ('Incoloro', 'Incoloro'),
    ]
    
    # Rarezas
    RAREZAS = [
        ('COMUN', 'Común'),
        ('INFREC', 'Infrecuente'),
        ('RARA', 'Rara'),
        ('RARA_HOLO', 'Rara Holo'),
        ('RARA_LUM', 'Rara Luminosa'),
        ('ULTRA', 'Rara Ultra'),
        ('SECRETA', 'Rara Secreta'),
        ('EX', 'Rara Holo EX'),
        ('GX', 'Rara GX'),
        ('V', 'Rara Holo V'),
        ('VMAX', 'Rara Holo VMAX'),
        ('PROMO', 'Promo'),
    ]
    
    # Condiciones
    CONDICIONES = [
        ('NM', 'Casi Perfecta (Near Mint)'),
        ('LP', 'Levemente Jugada (Lightly Played)'),
        ('MP', 'Moderadamente Jugada (Moderately Played)'),
        ('HP', 'Altamente Jugada (Heavily Played)'),
        ('D', 'Dañada (Damaged)'),
    ]
    
    # Campos básicos
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    numero_en_expansion = models.PositiveIntegerField()
    descripcion = models.TextField()
    
    # Atributos
    tipo = models.CharField(max_length=20, choices=TIPOS_POKEMON, blank=True, null=True)
    tipo_secundario = models.CharField(max_length=20, choices=TIPOS_POKEMON, blank=True, null=True)
    hp = models.PositiveIntegerField(blank=True, null=True)
    
    # Relaciones
    expansion = models.ForeignKey(Expansion, on_delete=models.PROTECT, related_name='cartas')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='cartas')
    
    # Detalles
    rareza = models.CharField(max_length=20, choices=RAREZAS)
    condicion = models.CharField(max_length=2, choices=CONDICIONES, default='NM')
    es_holo = models.BooleanField(default=False)
    primera_edicion = models.BooleanField(default=False)
    idioma = models.CharField(max_length=20, default='Español')
    
    # Imágenes
    imagen_frontal = models.ImageField(upload_to='cartas/frontal/')
    imagen_trasera = models.ImageField(upload_to='cartas/trasera/', blank=True, null=True)
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    coleccionable = models.BooleanField(default=True)
    popularidad = models.IntegerField(default=0)  # Para ordenamiento
    
    class Meta:
        verbose_name = "Carta"
        verbose_name_plural = "Cartas"
        ordering = ['expansion', 'numero_en_expansion']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['tipo']),
            models.Index(fields=['rareza']),
            models.Index(fields=['popularidad']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def tipos_completos(self):
        """Devuelve todos los tipos de la carta"""
        tipos = []
        if self.tipo:
            tipos.append(self.tipo)
        if self.tipo_secundario:
            tipos.append(self.tipo_secundario)
        return tipos
    
    @property
    def precio_estimado(self):
        """Calcula precio estimado"""
        precios_base = {
            'COMUN': 0.3, 'INFREC': 0.8, 'RARA': 2.0,
            'RARA_HOLO': 10.0, 'RARA_LUM': 15.0, 'ULTRA': 30.0,
            'SECRETA': 40.0, 'EX': 20.0, 'GX': 25.0,
            'V': 20.0, 'VMAX': 35.0, 'PROMO': 5.0,
        }
        
        multiplicadores = {
            'NM': 1.0, 'LP': 0.75, 'MP': 0.5, 'HP': 0.3, 'D': 0.1
        }
        
        base = precios_base.get(self.rareza, 1.0)
        multiplicador = multiplicadores.get(self.condicion, 1.0)
        
        if self.es_holo:
            multiplicador *= 1.3
        if self.primera_edicion:
            multiplicador *= 2.0
        
        return round(base * multiplicador, 2)
    
    def aumentar_popularidad(self, cantidad=1):
        """Aumenta la popularidad de la carta"""
        self.popularidad += cantidad
        self.save(update_fields=['popularidad'])


class Inventario(models.Model):
    """Gestión de stock de cartas"""
    carta = models.OneToOneField(Carta, on_delete=models.CASCADE, related_name='inventario')
    cantidad_disponible = models.PositiveIntegerField(default=0)
    cantidad_reservada = models.PositiveIntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_promocional = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    en_promocion = models.BooleanField(default=False)
    
    # Métricas
    vendidos_total = models.PositiveIntegerField(default=0)
    valoracion_promedio = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    # Fechas
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"
        ordering = ['-fecha_ingreso']
    
    def __str__(self):
        return f"Inventario de {self.carta.nombre}"
    
    @property
    def precio_actual(self):
        """Precio actual (promocional si está en promoción)"""
        return self.precio_promocional if self.en_promocion and self.precio_promocional else self.precio
    
    @property
    def stock_real(self):
        """Stock disponible real"""
        return self.cantidad_disponible - self.cantidad_reservada
    
    @property
    def disponible(self):
        """¿Hay stock disponible?"""
        return self.stock_real > 0
    
    def reservar(self, cantidad):
        """Reserva stock"""
        if cantidad > self.stock_real:
            raise ValueError(f"Stock insuficiente. Disponible: {self.stock_real}")
        self.cantidad_reservada += cantidad
        self.save()
    
    def liberar(self, cantidad):
        """Libera stock reservado"""
        if cantidad > self.cantidad_reservada:
            cantidad = self.cantidad_reservada
        self.cantidad_reservada -= cantidad
        self.save()
    
    def vender(self, cantidad):
        """Registra una venta"""
        if cantidad > self.stock_real:
            raise ValueError(f"Stock insuficiente. Disponible: {self.stock_real}")
        self.cantidad_disponible -= cantidad
        self.vendidos_total += cantidad
        self.save()


class Pedido(models.Model):
    """Pedidos de clientes"""
    
    ESTADOS = [
        ('CARRITO', 'En Carrito'),
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    METODOS_PAGO = [
        ('TARJETA', 'Tarjeta'),
        ('PAYPAL', 'PayPal'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('EFECTIVO', 'Efectivo'),
    ]
    
    # Identificación
    numero_pedido = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    
    # Estado y fechas
    estado = models.CharField(max_length=20, choices=ESTADOS, default='CARRITO')
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_pago = models.DateTimeField(blank=True, null=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    
    # Información de envío
    nombre_completo = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100, blank=True, default='')
    provincia = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    pais = models.CharField(max_length=100, default='España')
    
    # Información de pago
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, blank=True, null=True)
    
    # Totales
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    envio = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Información adicional
    notas = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_pedido']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_pedido']),
            models.Index(fields=['cliente']),
        ]
    
    def __str__(self):
        return f"Pedido #{self.numero_pedido}"
    
    def calcular_totales(self):
        """Calcula todos los totales del pedido"""
        # Calcular subtotal
        subtotal = Decimal('0.00')
        for item in self.items.all():
            item.calcular_subtotal()
            subtotal += item.subtotal
        
        # Calcular envío
        envio = Decimal('0.00') if subtotal >= Decimal('100.00') else Decimal('4.95')
        
        # Calcular impuestos
        impuestos = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))
        
        # Calcular total
        total = (subtotal + envio + impuestos - self.descuento).quantize(Decimal('0.01'))
        
        # Actualizar campos
        self.subtotal = subtotal
        self.envio = envio
        self.impuestos = impuestos
        self.total = total
        
        # Guardar sin llamar a save() completo
        Pedido.objects.filter(id=self.id).update(
            subtotal=subtotal,
            envio=envio,
            impuestos=impuestos,
            total=total
        )
    
    @property
    def cantidad_items(self):
        return sum(item.cantidad for item in self.items.all())
    
    @property
    def envio_gratis(self):
        return self.envio == 0
    
    def procesar_pago(self):
        """Procesa el pago del pedido"""
        if self.estado == 'CARRITO':
            self.estado = 'PAGADO'
            self.fecha_pago = timezone.now()
            self.save()
            
            # Reservar stock
            for item in self.items.all():
                item.inventario.reservar(item.cantidad)


class ItemPedido(models.Model):
    """Items individuales en un pedido"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    carta = models.ForeignKey(Carta, on_delete=models.PROTECT, related_name='items_pedido')
    inventario = models.ForeignKey(Inventario, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Ítem de Pedido"
        verbose_name_plural = "Ítems de Pedido"
        unique_together = ['pedido', 'carta']
    
    def __str__(self):
        return f"{self.cantidad}x {self.carta.nombre}"
    
    def save(self, *args, **kwargs):
        # Calcular subtotal antes de guardar
        self.calcular_subtotal()
        super().save(*args, **kwargs)
    
    def calcular_subtotal(self):
        """Calcula el subtotal del item"""
        if self.precio_unitario and self.cantidad:
            self.subtotal = self.precio_unitario * self.cantidad
        else:
            self.subtotal = Decimal('0.00')


class Resena(models.Model):
    """Reseñas de cartas"""
    carta = models.ForeignKey(Carta, on_delete=models.CASCADE, related_name='resenas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resenas')
    valoracion = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    titulo = models.CharField(max_length=200)
    comentario = models.TextField()
    condicion_recibida = models.CharField(max_length=2, choices=Carta.CONDICIONES, blank=True, null=True)
    recomendado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    aprobada = models.BooleanField(default=False)
    votos_positivos = models.PositiveIntegerField(default=0)
    votos_negativos = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ['-fecha_creacion']
        unique_together = ['carta', 'usuario']
    
    def __str__(self):
        return f"Reseña de {self.usuario.username} para {self.carta.nombre}"
    
    @property
    def utilidad(self):
        return self.votos_positivos - self.votos_negativos
    
    def votar_positivo(self):
        self.votos_positivos += 1
        self.save()
    
    def votar_negativo(self):
        self.votos_negativos += 1
        self.save()


class Coleccion(models.Model):
    """Colecciones personales de cartas"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='colecciones')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    publica = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    portada = models.ImageField(upload_to='colecciones/portadas/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Colección"
        verbose_name_plural = "Colecciones"
        ordering = ['-fecha_creacion']
        unique_together = ['usuario', 'nombre']
    
    def __str__(self):
        return self.nombre
    
    @property
    def total_cartas(self):
        return sum(item.cantidad for item in self.cartas.all())
    
    @property
    def valor_estimado(self):
        total = Decimal('0.00')
        for item in self.cartas.all():
            total += item.carta.precio_estimado * item.cantidad
        return total


class ColeccionCarta(models.Model):
    """Cartas dentro de una colección"""
    coleccion = models.ForeignKey(Coleccion, on_delete=models.CASCADE, related_name='cartas')
    carta = models.ForeignKey(Carta, on_delete=models.CASCADE, related_name='en_colecciones')
    cantidad = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=2, choices=Carta.CONDICIONES, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Carta en Colección"
        verbose_name_plural = "Cartas en Colecciones"
        unique_together = ['coleccion', 'carta']
    
    def __str__(self):
        return f"{self.carta.nombre} en {self.coleccion.nombre}"