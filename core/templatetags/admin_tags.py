# core/templatetags/admin_tags.py
from django import template

register = template.Library()

@register.filter(name='get_attribute')
def get_attribute(obj, attr):
    """
    Obtiene un atributo de un objeto.
    Si el atributo es un método, lo llama sin argumentos.
    """
    try:
        # Intenta obtener el atributo
        value = getattr(obj, attr)
        
        # Si es un método, llámalo
        if callable(value):
            value = value()
            
        return value
    except AttributeError:
        return ""