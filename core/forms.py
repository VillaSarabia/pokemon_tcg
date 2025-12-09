# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Pedido, Resena, Carta, Expansion, Coleccion, ColeccionCarta


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellidos")
    
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'nombre_completo', 'email', 'telefono', 
            'direccion', 'ciudad', 'provincia',
            'codigo_postal', 'pais', 'metodo_pago', 'notas'
        ]
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+34 123 456 789'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Calle, número, piso, puerta...'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            'provincia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Provincia'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345'
            }),
            'pais': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'País'
            }),
            'metodo_pago': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Instrucciones especiales para la entrega...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer valor por defecto para país
        if not self.instance.pk:
            self.fields['pais'].initial = 'España'


class PagoTarjetaForm(forms.Form):
    numero_tarjeta = forms.CharField(
        max_length=19,
        validators=[RegexValidator(r'^\d{13,19}$', 'Número de tarjeta inválido')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456'
        })
    )
    nombre_titular = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre como aparece en la tarjeta'
        })
    )
    fecha_expiracion = forms.CharField(
        max_length=5,
        validators=[RegexValidator(r'^(0[1-9]|1[0-2])\/([0-9]{2})$', 'Formato MM/YY')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY'
        })
    )
    cvv = forms.CharField(
        max_length=4,
        validators=[RegexValidator(r'^\d{3,4}$', 'CVV inválido')],
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '123'
        })
    )
    recordar_tarjeta = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Recordar tarjeta para futuras compras'
    )


class ResenaForm(forms.ModelForm):
    valoracion = forms.ChoiceField(
        choices=[(1, '1 ★'), (2, '2 ★★'), (3, '3 ★★★'), (4, '4 ★★★★'), (5, '5 ★★★★★')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Valoración'
    )
    
    class Meta:
        model = Resena
        fields = ['valoracion', 'titulo', 'comentario', 'condicion_recibida', 'recomendado']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de tu reseña'
            }),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe tu experiencia con esta carta...',
                'rows': 4
            }),
            'condicion_recibida': forms.Select(attrs={
                'class': 'form-control'
            }),
            'recomendado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'condicion_recibida': 'Condición en la que recibiste la carta',
            'recomendado': '¿Recomendarías esta carta a otros coleccionistas?',
        }


class BusquedaCartaForm(forms.Form):
    """Formulario para buscar cartas"""
    nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre...',
            'style': 'min-width: 250px;'
        }),
        label=''
    )
    
    tipo = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los tipos')] + Carta.TIPOS_POKEMON,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo'
    )
    
    rareza = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas las rarezas')] + Carta.RAREZAS,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Rareza'
    )
    
    expansion = forms.ModelChoiceField(
        queryset=Expansion.objects.filter(activa=True),
        required=False,
        empty_label="Todas las expansiones",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Expansión'
    )
    
    orden = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Ordenar por'),
            ('nombre', 'Nombre A-Z'),
            ('-nombre', 'Nombre Z-A'),
            ('precio', 'Precio más bajo'),
            ('-precio', 'Precio más alto'),
            ('popularidad', 'Más populares'),
            ('-fecha_creacion', 'Más recientes'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Ordenar por'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar dinámicamente las expansiones activas
        self.fields['expansion'].queryset = Expansion.objects.filter(activa=True)


class ContactoForm(forms.Form):
    """Formulario de contacto"""
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        })
    )
    
    asunto = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Asunto del mensaje'
        })
    )
    
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tu mensaje aquí...',
            'rows': 5
        })
    )


class CuponDescuentoForm(forms.Form):
    """Formulario para aplicar cupones de descuento"""
    codigo = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Introduce tu código de descuento'
        })
    )


class ColeccionForm(forms.ModelForm):
    """Formulario para crear/editar colecciones"""
    class Meta:
        model = Coleccion
        fields = ['nombre', 'descripcion', 'publica', 'portada']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la colección'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe tu colección...',
                'rows': 3
            }),
            'publica': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'portada': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'publica': '¿Colección pública?',
            'portada': 'Imagen de portada (opcional)',
        }


class AgregarCartaColeccionForm(forms.ModelForm):
    """Formulario para añadir cartas a una colección"""
    class Meta:
        model = ColeccionCarta
        fields = ['carta', 'cantidad', 'estado', 'notas']
        widgets = {
            'carta': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            }),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Notas sobre esta carta en tu colección...',
                'rows': 2
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo cartas coleccionables
        self.fields['carta'].queryset = Carta.objects.filter(coleccionable=True)


class CambiarContrasenaForm(forms.Form):
    """Formulario para cambiar contraseña"""
    contrasena_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        }),
        label='Contraseña actual'
    )
    
    nueva_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        }),
        label='Nueva contraseña'
    )
    
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        }),
        label='Confirmar nueva contraseña'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        nueva = cleaned_data.get('nueva_contrasena')
        confirmar = cleaned_data.get('confirmar_contrasena')
        
        if nueva and confirmar and nueva != confirmar:
            self.add_error('confirmar_contrasena', 'Las contraseñas no coinciden')
        
        return cleaned_data


class NewsletterForm(forms.Form):
    """Formulario para suscribirse al newsletter"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu correo electrónico'
        }),
        label=''
    )
    
    acepto_politica = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Acepto la política de privacidad'
    )


class FiltroPrecioForm(forms.Form):
    """Formulario para filtrar por rango de precio"""
    precio_min = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo',
            'step': '0.01'
        }),
        label='Precio mínimo (€)'
    )
    
    precio_max = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Máximo',
            'step': '0.01'
        }),
        label='Precio máximo (€)'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        precio_min = cleaned_data.get('precio_min')
        precio_max = cleaned_data.get('precio_max')
        
        if precio_min and precio_max and precio_min > precio_max:
            self.add_error('precio_max', 'El precio máximo debe ser mayor o igual al mínimo')
        
        return cleaned_data


class ActualizarPerfilForm(forms.ModelForm):
    """Formulario para actualizar perfil de usuario"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
        }


class CancelarPedidoForm(forms.Form):
    """Formulario para cancelar un pedido"""
    motivo = forms.ChoiceField(
        choices=[
            ('', 'Selecciona un motivo'),
            ('cambio_opinion', 'Cambié de opinión'),
            ('encontrado_mas_barato', 'Lo encontré más barato en otro sitio'),
            ('problema_envio', 'Problema con el envío'),
            ('demora', 'Demora en la entrega'),
            ('otro', 'Otro motivo'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Motivo de cancelación'
    )
    
    comentario = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Explica brevemente por qué cancelas el pedido...',
            'rows': 3
        }),
        label='Comentario adicional (opcional)'
    )