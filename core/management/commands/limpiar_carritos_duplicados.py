# core/management/commands/limpiar_carritos_duplicados.py
from django.core.management.base import BaseCommand
from django.db.models import Count
from core.models import Pedido, ItemPedido

class Command(BaseCommand):
    help = 'Limpia carritos duplicados para cada usuario'

    def handle(self, *args, **options):
        # Encontrar usuarios con múltiples carritos
        usuarios_con_duplicados = Pedido.objects.filter(
            estado='CARRITO'
        ).values('cliente').annotate(
            total=Count('id')
        ).filter(total__gt=1)
        
        total_consolidados = 0
        total_eliminados = 0
        
        for usuario_data in usuarios_con_duplicados:
            usuario_id = usuario_data['cliente']
            
            # Obtener carritos del usuario
            carritos = Pedido.objects.filter(
                cliente_id=usuario_id,
                estado='CARRITO'
            ).order_by('-fecha_pedido')
            
            if carritos.count() < 2:
                continue
            
            # Tomar el más reciente como principal
            carrito_principal = carritos.first()
            
            # Consolidar items de otros carritos
            for carrito in carritos[1:]:
                items_movidos = 0
                
                # Necesitamos copiar los items para iterar
                items = list(carrito.items.all())
                
                for item in items:
                    # Verificar si ya existe el item en el carrito principal
                    item_existente = carrito_principal.items.filter(
                        carta=item.carta,
                        inventario=item.inventario
                    ).first()
                    
                    if item_existente:
                        # Sumar cantidades
                        item_existente.cantidad += item.cantidad
                        item_existente.calcular_subtotal()
                        item_existente.save()
                        item.delete()  # Eliminar el item duplicado
                    else:
                        # Mover item al carrito principal
                        item.pedido = carrito_principal
                        item.save()
                        items_movidos += 1
                
                # Eliminar carrito duplicado (vacío)
                carrito.delete()
                total_eliminados += 1
                total_consolidados += items_movidos
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Consolidado carrito para usuario {usuario_id}. '
                    f'{items_movidos} items movidos, 1 carrito eliminado.'
                )
            )
        
        # Recalcular totales de todos los carritos restantes
        carritos_restantes = Pedido.objects.filter(estado='CARRITO')
        for carrito in carritos_restantes:
            carrito.calcular_totales()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Proceso completado:\n'
                f'   - Carritos eliminados: {total_eliminados}\n'
                f'   - Items consolidados: {total_consolidados}\n'
                f'   - Carritos restantes: {carritos_restantes.count()}'
            )
        )