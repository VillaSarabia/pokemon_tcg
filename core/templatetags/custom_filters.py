# core/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    """Resta arg de value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def add(value, arg):
    """Suma arg a value"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def multiply(value, arg):
    """Multiplica value por arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def divide(value, arg):
    """Divide value entre arg"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def modulo(value, arg):
    """Calcula value modulo arg"""
    try:
        return float(value) % float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def currency(value):
    """Formatea como moneda"""
    try:
        return f"{float(value):.2f}€"
    except (ValueError, TypeError):
        return value