from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import ItemPedido, Pedido, Inventario

@receiver(post_save, sender=ItemPedido)
def actualizar_stock_al_confirmar(sender, instance, created, **kwargs):
    """
    Actualiza el stock cuando se confirma un pedido
    """
    if instance.pedido.estado == 'PEND' and instance.pedido.pagado:
        try:
            with transaction.atomic():
                instance.inventario.actualizar_stock(
                    instance.cantidad, 
                    operacion='venta'
                )
                # Incrementar popularidad de la carta
                instance.inventario.popularidad += 10
                instance.inventario.save()
        except Exception as e:
            # Revertir si hay error
            print(f"Error actualizando stock: {e}")

@receiver(post_delete, sender=ItemPedido)
def restaurar_stock_al_eliminar(sender, instance, **kwargs):
    """
    Restaura el stock cuando se elimina un item del pedido
    """
    if instance.pedido.estado in ['PEND', 'PROC']:
        try:
            instance.inventario.liberar_stock(instance.cantidad)
        except Exception as e:
            print(f"Error restaurando stock: {e}")

@receiver(post_save, sender=Pedido)
def actualizar_estado_pedido(sender, instance, created, **kwargs):
    """
    Maneja cambios de estado del pedido
    """
    if not created and instance.estado == 'ENTR':
        # Marcar como completado y liberar stock reservado
        for item in instance.items.all():
            try:
                item.inventario.cantidad_reservada = max(
                    0, 
                    item.inventario.cantidad_reservada - item.cantidad
                )
                item.inventario.save()
            except Exception as e:
                print(f"Error liberando stock reservado: {e}")