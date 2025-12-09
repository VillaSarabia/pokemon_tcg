from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Categoria, Expansion, Carta, Inventario
import json
from datetime import datetime

class Command(BaseCommand):
    help = 'Carga datos iniciales para Pokemon TCG'

    def handle(self, *args, **options):
        self.stdout.write('Cargando datos iniciales...')
        
        # Crear usuario admin si no existe
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@pokemontcg.com',
                password='admin123',
                first_name='Admin',
                last_name='Pokemon'
            )
            self.stdout.write(self.style.SUCCESS('Usuario admin creado'))
        
        # Crear categorías
        categorias_data = [
            {'nombre': 'Pokémon Básicos', 'descripcion': 'Pokémon de etapa básica'},
            {'nombre': 'Pokémon Evolucionados', 'descripcion': 'Pokémon de etapa 1 y 2'},
            {'nombre': 'Pokémon EX/GX/V', 'descripcion': 'Pokémon especiales'},
            {'nombre': 'Cartas de Entrenador', 'descripcion': 'Cartas de apoyo'},
            {'nombre': 'Cartas de Energía', 'descripcion': 'Cartas de energía'},
        ]
        
        for cat_data in categorias_data:
            Categoria.objects.get_or_create(**cat_data)
        
        self.stdout.write(self.style.SUCCESS('Categorías creadas'))
        
        # Crear expansiones de ejemplo
        expansiones_data = [
            {
                'codigo': 'SVI',
                'nombre': 'Escarlata y Violeta',
                'fecha_lanzamiento': '2023-03-31',
                'total_cartas': 258,
                'activa': True,
            },
            {
                'codigo': 'CRZ',
                'nombre': 'Corona Zenith',
                'fecha_lanzamiento': '2023-01-20',
                'total_cartas': 159,
                'activa': True,
            },
            {
                'codigo': 'LOR',
                'nombre': 'Lost Origin',
                'fecha_lanzamiento': '2022-09-09',
                'total_cartas': 196,
                'activa': True,
            },
        ]
        
        for exp_data in expansiones_data:
            exp_data['fecha_lanzamiento'] = datetime.strptime(
                exp_data['fecha_lanzamiento'], '%Y-%m-%d'
            ).date()
            Expansion.objects.get_or_create(
                codigo=exp_data['codigo'],
                defaults=exp_data
            )
        
        self.stdout.write(self.style.SUCCESS('Expansiones creadas'))
        
        # Crear algunas cartas de ejemplo (sin imágenes)
        expansion_svi = Expansion.objects.get(codigo='SVI')
        categoria_basicos = Categoria.objects.get(nombre='Pokémon Básicos')
        
        cartas_data = [
            {
                'codigo': 'SVI-001',
                'nombre': 'Pikachu',
                'numero_en_expansion': 1,
                'descripcion': 'Pokémon Ratón. Cuando se enfada, libera inmediatamente la energía almacenada en las bolsas de sus mejillas.',
                'tipo': 'Eléctrico',
                'hp': 70,
                'etapa': 'BASICO',
                'ataque_1_nombre': 'Impactrueno',
                'ataque_1_dano': 30,
                'ataque_1_costo': 'Eléctrico, Incoloro',
                'rareza': 'COMUN',
                'expansion': expansion_svi,
                'categoria': categoria_basicos,
            },
            {
                'codigo': 'SVI-002',
                'nombre': 'Charizard ex',
                'numero_en_expansion': 2,
                'descripcion': 'Pokémon Llama. Escupe fuego tan caliente que funde las rocas. Causa incendios forestales sin querer.',
                'tipo': 'Fuego',
                'hp': 330,
                'etapa': 'EX',
                'ataque_1_nombre': 'Ascuas Ardientes',
                'ataque_1_dano': 180,
                'ataque_1_costo': 'Fuego, Fuego, Fuego, Incoloro',
                'rareza': 'EX',
                'expansion': expansion_svi,
                'categoria': categoria_basicos,
                'es_holo': True,
            },
        ]
        
        for carta_data in cartas_data:
            carta, created = Carta.objects.get_or_create(
                codigo=carta_data['codigo'],
                defaults=carta_data
            )
            
            if created:
                # Crear inventario para la carta
                Inventario.objects.create(
                    carta=carta,
                    cantidad_disponible=10,
                    precio=24.99 if carta_data['codigo'] == 'SVI-002' else 1.99,
                    precio_promocional=19.99 if carta_data['codigo'] == 'SVI-002' else None,
                    en_promocion=carta_data['codigo'] == 'SVI-002',
                )
        
        self.stdout.write(self.style.SUCCESS('Cartas de ejemplo creadas'))
        
        self.stdout.write(self.style.SUCCESS('¡Datos iniciales cargados exitosamente!'))