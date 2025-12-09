# populate_database.py
import os
import requests
import json
import django
import sys
from pathlib import Path
from datetime import date, datetime
from io import BytesIO
from PIL import Image
import time

# Configurar Django
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pokemon_tcg.settings')
django.setup()

from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from core.models import (
    Categoria, Expansion, Carta, Inventario, 
    Pedido, ItemPedido, Resena, Coleccion, ColeccionCarta
)

class DatabasePopulator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.images_dir = Path('media/cartas')
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
    def descargar_imagen(self, url, nombre_archivo):
        """Descarga una imagen y la guarda en el sistema de archivos"""
        try:
            # Esperar para no sobrecargar el servidor
            time.sleep(0.5)
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Verificar que sea una imagen
            if 'image' in response.headers.get('content-type', ''):
                return ContentFile(response.content, nombre_archivo)
            else:
                print(f"URL no es una imagen: {url}")
                return None
        except Exception as e:
            print(f"Error descargando imagen {url}: {e}")
            return None
    
    def crear_superusuario(self):
        """Crea un usuario administrador"""
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@pokemontcg.com',
                password='admin123'
            )
            print("Superusuario creado: admin / admin123")
    
    def crear_usuarios_normales(self):
        """Crea algunos usuarios normales"""
        usuarios = [
            {'username': 'ash_ketchum', 'email': 'ash@pokemon.com', 'password': 'pikachu123'},
            {'username': 'misty', 'email': 'misty@pokemon.com', 'password': 'starmie123'},
            {'username': 'brock', 'email': 'brock@pokemon.com', 'password': 'onix123'},
            {'username': 'coleccionista', 'email': 'coleccion@pokemon.com', 'password': 'cartas123'},
        ]
        
        for user_data in usuarios:
            if not User.objects.filter(username=user_data['username']).exists():
                User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password']
                )
        print(f"{len(usuarios)} usuarios creados")
    
    def crear_categorias(self):
        """Crea las categorías principales"""
        categorias = [
            {
                'nombre': 'Pokémon Básico',
                'descripcion': 'Cartas de Pokémon en su etapa básica',
                'icono': 'pokeball'
            },
            {
                'nombre': 'Pokémon Evolucionado',
                'descripcion': 'Cartas de Pokémon evolucionados (Etapa 1 y 2)',
                'icono': 'superball'
            },
            {
                'nombre': 'Pokémon Legendario',
                'descripcion': 'Cartas de Pokémon legendarios y míticos',
                'icono': 'ultraball'
            },
            {
                'nombre': 'Pokémon EX/GX/V',
                'descripcion': 'Cartas especiales EX, GX, V y similares',
                'icono': 'masterball'
            },
            {
                'nombre': 'Cartas de Entrenador',
                'descripcion': 'Cartas de entrenador, objeto y estadio',
                'icono': 'trainer'
            },
            {
                'nombre': 'Cartas de Energía',
                'descripcion': 'Cartas de energía de todos los tipos',
                'icono': 'energy'
            },
            {
                'nombre': 'Cartas Promocionales',
                'descripcion': 'Cartas especiales de promociones y eventos',
                'icono': 'promo'
            },
        ]
        
        for cat_data in categorias:
            Categoria.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults=cat_data
            )
        print(f"{len(categorias)} categorías creadas")
    
    def crear_expansiones(self):
        """Crea expansiones populares de Pokémon TCG"""
        expansiones = [
            {
                'codigo': 'SWSH12',
                'nombre': 'Fusion Strike',
                'fecha_lanzamiento': date(2021, 11, 12),
                'total_cartas': 264,
                'activa': True,
                'descripcion': 'Expansión Fusion Strike de Espada y Escudo'
            },
            {
                'codigo': 'SWSH11',
                'nombre': 'Cielos Crecientes',
                'fecha_lanzamiento': date(2021, 8, 27),
                'total_cartas': 198,
                'activa': True,
                'descripcion': 'Expansión Cielos Crecientes'
            },
            {
                'codigo': 'SWSH10',
                'nombre': 'Choque de Sombras',
                'fecha_lanzamiento': date(2021, 6, 18),
                'total_cartas': 198,
                'activa': True,
                'descripcion': 'Expansión Choque de Sombras'
            },
            {
                'codigo': 'SWSH9',
                'nombre': 'Brillante Destino',
                'fecha_lanzamiento': date(2021, 5, 14),
                'total_cartas': 190,
                'activa': True,
                'descripcion': 'Expansión Brillante Destino'
            },
            {
                'codigo': 'SWSH8',
                'nombre': 'Ensalada de Espadas',
                'fecha_lanzamiento': date(2021, 2, 19),
                'total_cartas': 202,
                'activa': True,
                'descripcion': 'Expansión V del Volcán y Ensalada de Espadas'
            },
            {
                'codigo': 'SWSH7',
                'nombre': 'Relámpagos Ardientes',
                'fecha_lanzamiento': date(2021, 3, 19),
                'total_cartas': 185,
                'activa': True,
                'descripcion': 'Expansión Relámpagos Ardientes'
            },
            {
                'codigo': 'SWSH6',
                'nombre': 'Callejón sin Salida',
                'fecha_lanzamiento': date(2021, 1, 22),
                'total_cartas': 184,
                'activa': True,
                'descripcion': 'Expansión Callejón sin Salida'
            },
            {
                'codigo': 'SWSH5',
                'nombre': 'Destello de Venganza',
                'fecha_lanzamiento': date(2020, 11, 13),
                'total_cartas': 185,
                'activa': True,
                'descripcion': 'Expansión Destello de Venganza'
            },
            {
                'codigo': 'SWSH4',
                'nombre': 'Tinieblas Imponentes',
                'fecha_lanzamiento': date(2020, 11, 6),
                'total_cartas': 189,
                'activa': True,
                'descripcion': 'Expansión Tinieblas Imponentes'
            },
            {
                'codigo': 'SWSH3',
                'nombre': 'Oscuridad Eterna',
                'fecha_lanzamiento': date(2020, 8, 14),
                'total_cartas': 201,
                'activa': True,
                'descripcion': 'Expansión Oscuridad Eterna'
            },
            {
                'codigo': 'SWSH2',
                'nombre': 'Espada y Escudo Rebelde Clash',
                'fecha_lanzamiento': date(2020, 5, 1),
                'total_cartas': 192,
                'activa': True,
                'descripcion': 'Expansión Rebelde Clash'
            },
            {
                'codigo': 'SWSH1',
                'nombre': 'Espada y Escudo',
                'fecha_lanzamiento': date(2020, 2, 7),
                'total_cartas': 202,
                'activa': True,
                'descripcion': 'Primera expansión de Espada y Escudo'
            },
            {
                'codigo': 'XY12',
                'nombre': 'Destinos Ardientes',
                'fecha_lanzamiento': date(2016, 8, 3),
                'total_cartas': 122,
                'activa': False,
                'descripcion': 'Última expansión de XY'
            },
            {
                'codigo': 'SM12',
                'nombre': 'Alianza Perdida',
                'fecha_lanzamiento': date(2019, 10, 4),
                'total_cartas': 236,
                'activa': False,
                'descripcion': 'Expansión de Sol y Luna'
            },
        ]
        
        for exp_data in expansiones:
            Expansion.objects.get_or_create(
                codigo=exp_data['codigo'],
                defaults=exp_data
            )
        print(f"{len(expansiones)} expansiones creadas")
    
    def crear_cartas_pokemon(self):
        """Crea cartas Pokémon reales con imágenes"""
        # Primero obtengamos las expansiones
        expansion_swsh = Expansion.objects.get(codigo='SWSH12')
        expansion_swsh1 = Expansion.objects.get(codigo='SWSH1')
        
        # Obtener categorías
        categoria_basico = Categoria.objects.get(nombre='Pokémon Básico')
        categoria_evolucionado = Categoria.objects.get(nombre='Pokémon Evolucionado')
        categoria_legendario = Categoria.objects.get(nombre='Pokémon Legendario')
        categoria_ex = Categoria.objects.get(nombre='Pokémon EX/GX/V')
        
        # URL de imágenes de ejemplo (puedes reemplazarlas con URLs reales)
        # Usaré imágenes de la PokéAPI y otras fuentes públicas
        imagenes_cartas = [
            # Pikachu
            {
                'url': 'https://assets.pokemon.com/assets/cms2/img/cards/web/SWSH/SWSH_EN_50.png',
                'nombre': 'pikachu_swsh.png'
            },
            # Charizard
            {
                'url': 'https://assets.pokemon.com/assets/cms2/img/cards/web/SWSH/SWSH_EN_20.png',
                'nombre': 'charizard_swsh.png'
            },
            # Blastoise
            {
                'url': 'https://assets.pokemon.com/assets/cms2/img/cards/web/SWSH/SWSH_EN_30.png',
                'nombre': 'blastoise_swsh.png'
            },
            # Venusaur
            {
                'url': 'https://assets.pokemon.com/assets/cms2/img/cards/web/SWSH/SWSH_EN_3.png',
                'nombre': 'venusaur_swsh.png'
            },
            # Mewtwo
            {
                'url': 'https://images.pokemontcg.io/swsh4/79.png',
                'nombre': 'mewtwo_swsh4.png'
            },
            # Lucario
            {
                'url': 'https://images.pokemontcg.io/swsh10/107.png',
                'nombre': 'lucario_swsh10.png'
            },
            # Greninja
            {
                'url': 'https://images.pokemontcg.io/swsh9/88.png',
                'nombre': 'greninja_swsh9.png'
            },
            # Eevee
            {
                'url': 'https://images.pokemontcg.io/swsh1/134.png',
                'nombre': 'eevee_swsh1.png'
            },
            # Gengar
            {
                'url': 'https://images.pokemontcg.io/swsh11/72.png',
                'nombre': 'gengar_swsh11.png'
            },
            # Dragonite
            {
                'url': 'https://images.pokemontcg.io/swsh12/131.png',
                'nombre': 'dragonite_swsh12.png'
            },
        ]
        
        # Descargar imágenes primero
        imagenes_descargadas = {}
        for img in imagenes_cartas:
            content_file = self.descargar_imagen(img['url'], img['nombre'])
            if content_file:
                imagenes_descargadas[img['nombre']] = content_file
                print(f"Imagen descargada: {img['nombre']}")
            else:
                # Crear imagen placeholder si no se puede descargar
                from django.core.files.base import ContentFile
                from PIL import Image, ImageDraw
                img_placeholder = Image.new('RGB', (245, 342), color='gray')
                draw = ImageDraw.Draw(img_placeholder)
                draw.text((50, 150), img['nombre'].replace('.png', ''), fill='white')
                
                buffer = BytesIO()
                img_placeholder.save(buffer, format='PNG')
                imagenes_descargadas[img['nombre']] = ContentFile(buffer.getvalue(), img['nombre'])
        
        # Cartas Pokémon reales
        cartas = [
            # Pikachu
            {
                'codigo': 'SWSH12-050',
                'nombre': 'Pikachu',
                'numero_en_expansion': 50,
                'descripcion': 'Pikachu es un Pokémon de tipo Eléctrico. Cuando se enfada, descarga inmediatamente la energía almacenada en las bolsas de sus mejillas.',
                'tipo': 'Eléctrico',
                'hp': 70,
                'etapa': 'BASICO',
                'ataque_1_nombre': 'Impactrueno',
                'ataque_1_dano': 30,
                'ataque_1_costo': 'Eléctrico',
                'ataque_1_descripcion': 'Lanza una pequeña descarga eléctrica.',
                'debilidad': 'Tierra',
                'resistencia': 'Acero',
                'costo_retirada': 'Incoloro',
                'expansion': expansion_swsh,
                'categoria': categoria_basico,
                'rareza': 'COMUN',
                'es_holo': False,
                'idioma': 'ES',
                'imagen_nombre': 'pikachu_swsh.png'
            },
            # Charizard
            {
                'codigo': 'SWSH12-020',
                'nombre': 'Charizard',
                'numero_en_expansion': 20,
                'descripcion': 'Charizard es un Pokémon de tipo Fuego/Volador. Escupe fuego tan caliente que funde las rocas.',
                'tipo': 'Fuego',
                'tipo_secundario': 'Volador',
                'hp': 170,
                'etapa': 'ETAPA2',
                'ataque_1_nombre': 'Llamarada',
                'ataque_1_dano': 150,
                'ataque_1_costo': 'Fuego, Fuego, Fuego',
                'ataque_1_descripcion': 'Descarga una potente llamarada sobre el rival.',
                'ataque_2_nombre': 'Garra Dragón',
                'ataque_2_dano': 100,
                'ataque_2_costo': 'Fuego, Fuego, Incoloro',
                'ataque_2_descripcion': 'Ataca con sus afiladas garras.',
                'debilidad': 'Agua',
                'resistencia': None,
                'costo_retirada': 'Incoloro, Incoloro',
                'expansion': expansion_swsh,
                'categoria': categoria_evolucionado,
                'rareza': 'RARA_HOLO',
                'es_holo': True,
                'idioma': 'ES',
                'imagen_nombre': 'charizard_swsh.png'
            },
            # Blastoise
            {
                'codigo': 'SWSH12-030',
                'nombre': 'Blastoise',
                'numero_en_expansion': 30,
                'descripcion': 'Blastoise es un Pokémon de tipo Agua. Los cañones de su caparazón lanzan chorros de agua con precisión.',
                'tipo': 'Agua',
                'hp': 160,
                'etapa': 'ETAPA2',
                'ataque_1_nombre': 'Hidrocañón',
                'ataque_1_dano': 140,
                'ataque_1_costo': 'Agua, Agua, Agua',
                'ataque_1_descripcion': 'Dispara un potente chorro de agua.',
                'habilidad_nombre': 'Torrente',
                'habilidad_descripcion': 'Una vez por turno, puedes poner 2 contadores de daño en el Pokémon Activo de tu rival.',
                'debilidad': 'Planta',
                'resistencia': None,
                'costo_retirada': 'Incoloro, Incoloro, Incoloro',
                'expansion': expansion_swsh,
                'categoria': categoria_evolucionado,
                'rareza': 'RARA_HOLO',
                'es_holo': True,
                'idioma': 'ES',
                'imagen_nombre': 'blastoise_swsh.png'
            },
            # Mewtwo
            {
                'codigo': 'SWSH4-079',
                'nombre': 'Mewtwo V',
                'numero_en_expansion': 79,
                'descripcion': 'Mewtwo es un Pokémon legendario creado por manipulación genética. Posee poderes psíquicos devastadores.',
                'tipo': 'Psíquico',
                'hp': 220,
                'etapa': 'BASICO',
                'ataque_1_nombre': 'Psicoataque',
                'ataque_1_dano': 60,
                'ataque_1_costo': 'Psíquico, Incoloro',
                'ataque_1_descripcion': 'Este ataque inflige 30 puntos de daño adicional a uno de los Pokémon del rival.',
                'ataque_2_nombre': 'Hipersupernova',
                'ataque_2_dano': 200,
                'ataque_2_costo': 'Psíquico, Psíquico, Incoloro',
                'ataque_2_descripcion': 'Descarga toda su energía psíquica.',
                'debilidad': 'Siniestro',
                'resistencia': 'Lucha',
                'costo_retirada': 'Incoloro, Incoloro',
                'expansion': Expansion.objects.get(codigo='SWSH4'),
                'categoria': categoria_legendario,
                'rareza': 'V',
                'es_holo': True,
                'primera_edicion': True,
                'idioma': 'ES',
                'imagen_nombre': 'mewtwo_swsh4.png'
            },
            # Eevee
            {
                'codigo': 'SWSH1-134',
                'nombre': 'Eevee',
                'numero_en_expansion': 134,
                'descripcion': 'Eevee es un Pokémon de tipo Normal con un código genético inestable. Puede evolucionar en diversas formas.',
                'tipo': 'Incoloro',
                'hp': 60,
                'etapa': 'BASICO',
                'ataque_1_nombre': 'Ataque Rápido',
                'ataque_1_dano': 10,
                'ataque_1_costo': 'Incoloro',
                'ataque_1_descripcion': 'Ataca antes que el Pokémon rival.',
                'habilidad_nombre': 'Energía de la Amistad',
                'habilidad_descripcion': 'Si Eevee es tu Pokémon Activo y recibes daño de un ataque, puedes buscar en tu baraja una carta de Energía.',
                'debilidad': 'Lucha',
                'resistencia': None,
                'costo_retirada': 'Incoloro',
                'expansion': expansion_swsh1,
                'categoria': categoria_basico,
                'rareza': 'COMUN',
                'es_holo': False,
                'idioma': 'ES',
                'imagen_nombre': 'eevee_swsh1.png'
            },
            # Lucario
            {
                'codigo': 'SWSH10-107',
                'nombre': 'Lucario VSTAR',
                'numero_en_expansion': 107,
                'descripcion': 'Lucario es un Pokémon de tipo Lucha/Acero. Puede percibir las auras de sus oponentes.',
                'tipo': 'Lucha',
                'hp': 280,
                'etapa': 'VSTAR',
                'ataque_1_nombre': 'Aura Sphere',
                'ataque_1_dano': 220,
                'ataque_1_costo': 'Lucha, Lucha, Incoloro',
                'ataque_1_descripcion': 'Este ataque también hace 30 de daño a uno de los Pokémon en Banca del rival.',
                'habilidad_nombre': 'Poder VSTAR',
                'habilidad_descripcion': 'Una vez durante el partido, puedes usar este poder para robar cartas hasta tener 6 cartas en la mano.',
                'debilidad': 'Psíquico',
                'resistencia': None,
                'costo_retirada': 'Incoloro, Incoloro',
                'expansion': Expansion.objects.get(codigo='SWSH10'),
                'categoria': categoria_ex,
                'rareza': 'VASTRO',
                'es_holo': True,
                'primera_edicion': False,
                'idioma': 'ES',
                'imagen_nombre': 'lucario_swsh10.png'
            },
            # Gengar
            {
                'codigo': 'SWSH11-072',
                'nombre': 'Gengar VMAX',
                'numero_en_expansion': 72,
                'descripcion': 'Gengar es un Pokémon de tipo Fantasma/Veneno. Se esconde en las sombras y se alimenta del miedo de la gente.',
                'tipo': 'Fantasma',
                'hp': 330,
                'etapa': 'VMAX',
                'ataque_1_nombre': 'G-Max Swallow',
                'ataque_1_dano': 120,
                'ataque_1_costo': 'Fantasma, Fantasma, Incoloro',
                'ataque_1_descripcion': 'Cura 30 puntos de daño de este Pokémon.',
                'ataque_2_nombre': 'Darkness Bomber',
                'ataque_2_dano': 270,
                'ataque_2_costo': 'Fantasma, Fantasma, Fantasma, Incoloro',
                'ataque_2_descripcion': 'Descarga una explosión de energía oscura.',
                'debilidad': 'Siniestro',
                'resistencia': 'Lucha',
                'costo_retirada': 'Incoloro, Incoloro',
                'expansion': Expansion.objects.get(codigo='SWSH11'),
                'categoria': categoria_ex,
                'rareza': 'VMAX',
                'es_holo': True,
                'primera_edicion': False,
                'idioma': 'ES',
                'imagen_nombre': 'gengar_swsh11.png'
            },
            # Dragonite
            {
                'codigo': 'SWSH12-131',
                'nombre': 'Dragonite V',
                'numero_en_expansion': 131,
                'descripcion': 'Dragonite es un Pokémon de tipo Dragón/Volador. Puede dar la vuelta al mundo en 16 horas.',
                'tipo': 'Dragón',
                'hp': 230,
                'etapa': 'V',
                'ataque_1_nombre': 'Dragon Gale',
                'ataque_1_dano': 160,
                'ataque_1_costo': 'Dragón, Dragón, Incoloro',
                'ataque_1_descripcion': 'Descarta 2 Energías de este Pokémon.',
                'habilidad_nombre': 'Swirling Winds',
                'habilidad_descripcion': 'Una vez durante tu turno, puedes buscar en tu baraja hasta 2 cartas y ponerlas en tu mano.',
                'debilidad': 'Hada',
                'resistencia': None,
                'costo_retirada': 'Incoloro, Incoloro, Incoloro',
                'expansion': expansion_swsh,
                'categoria': categoria_ex,
                'rareza': 'V',
                'es_holo': True,
                'primera_edicion': False,
                'idioma': 'ES',
                'imagen_nombre': 'dragonite_swsh12.png'
            },
            # Greninja
            {
                'codigo': 'SWSH9-088',
                'nombre': 'Greninja',
                'numero_en_expansion': 88,
                'descripcion': 'Greninja es un Pokémon de tipo Agua/Siniestro. Crea estrellas ninja con agua comprimida.',
                'tipo': 'Agua',
                'hp': 140,
                'etapa': 'ETAPA2',
                'ataque_1_nombre': 'Surf',
                'ataque_1_dano': 120,
                'ataque_1_costo': 'Agua, Agua, Incoloro',
                'ataque_1_descripcion': 'Surfea sobre una ola gigante.',
                'ataque_2_nombre': 'Shuriken Flurry',
                'ataque_2_dano': 40,
                'ataque_2_costo': 'Agua',
                'ataque_2_descripcion': 'Este ataque hace 40 de daño a 2 de los Pokémon del rival.',
                'debilidad': 'Planta',
                'resistencia': None,
                'costo_retirada': 'Incoloro',
                'expansion': Expansion.objects.get(codigo='SWSH9'),
                'categoria': categoria_evolucionado,
                'rareza': 'RARA_HOLO',
                'es_holo': True,
                'primera_edicion': False,
                'idioma': 'ES',
                'imagen_nombre': 'greninja_swsh9.png'
            },
            # Venusaur
            {
                'codigo': 'SWSH12-003',
                'nombre': 'Venusaur VMAX',
                'numero_en_expansion': 3,
                'descripcion': 'Venusaur es un Pokémon de tipo Planta/Veneno. La flor en su lomo libera un aroma relajante.',
                'tipo': 'Planta',
                'hp': 330,
                'etapa': 'VMAX',
                'ataque_1_nombre': 'G-Max Vine',
                'ataque_1_dano': 240,
                'ataque_1_costo': 'Planta, Planta, Planta',
                'ataque_1_descripcion': 'Enreda al Pokémon rival con lianas gigantes.',
                'debilidad': 'Fuego',
                'resistencia': 'Agua',
                'costo_retirada': 'Incoloro, Incoloro, Incoloro',
                'expansion': expansion_swsh,
                'categoria': categoria_ex,
                'rareza': 'VMAX',
                'es_holo': True,
                'primera_edicion': True,
                'idioma': 'ES',
                'imagen_nombre': 'venusaur_swsh.png'
            },
        ]
        
        # Crear las cartas
        cartas_creadas = []
        for carta_data in cartas:
            if not Carta.objects.filter(codigo=carta_data['codigo']).exists():
                # Obtener la imagen
                imagen_nombre = carta_data.pop('imagen_nombre')
                imagen_content = imagenes_descargadas.get(imagen_nombre)
                
                if imagen_content:
                    # Crear la carta
                    carta = Carta(**carta_data)
                    carta.imagen_frontal.save(imagen_nombre, imagen_content, save=True)
                    cartas_creadas.append(carta)
                    
                    print(f"Carta creada: {carta.nombre}")
        
        print(f"{len(cartas_creadas)} cartas creadas")
        return cartas_creadas
    
    def crear_inventario(self):
        """Crea inventario para las cartas"""
        cartas = Carta.objects.all()
        
        precios_base = {
            'COMUN': 0.99,
            'INFREC': 1.99,
            'RARA': 4.99,
            'RARA_HOLO': 14.99,
            'V': 24.99,
            'VMAX': 39.99,
            'VASTRO': 34.99,
            'GX': 29.99,
        }
        
        for carta in cartas:
            if not hasattr(carta, 'inventario'):
                # Determinar precio base
                precio_base = precios_base.get(carta.rareza, 9.99)
                
                # Ajustar por condición y edición
                multiplicador = 1.0
                if carta.primera_edicion:
                    multiplicador *= 1.5
                if carta.condicion == 'NM':
                    multiplicador *= 1.2
                elif carta.condicion == 'LP':
                    multiplicador *= 1.0
                elif carta.condicion == 'MP':
                    multiplicador *= 0.7
                elif carta.condicion == 'HP':
                    multiplicador *= 0.4
                elif carta.condicion == 'D':
                    multiplicador *= 0.2
                
                precio_final = round(precio_base * multiplicador, 2)
                costo_adquisicion = round(precio_final * 0.6, 2)  # 60% del precio como costo
                
                Inventario.objects.create(
                    carta=carta,
                    cantidad_disponible=10,
                    cantidad_reservada=0,
                    precio=precio_final,
                    costo_adquisicion=costo_adquisicion,
                    proveedor="Pokémon Center España",
                    ubicacion_almacen=f"A{cartas.count() % 10 + 1:02d}-B{(cartas.count() // 10) % 5 + 1:02d}",
                    vendidos_total=cartas.count() % 20,  # Simular algunas ventas
                    valoracion_promedio=4.0 + (cartas.count() % 10) * 0.1,  # Valoraciones entre 4.0 y 4.9
                    popularidad=50 + cartas.count() * 10
                )
        
        print(f"Inventario creado para {cartas.count()} cartas")
    
    def crear_pedidos(self):
        """Crea pedidos de ejemplo"""
        # Obtener usuarios y cartas
        try:
            ash = User.objects.get(username='ash_ketchum')
            misty = User.objects.get(username='misty')
            brock = User.objects.get(username='brock')
            
            # Obtener algunas cartas
            pikachu = Carta.objects.get(codigo='SWSH12-050')
            charizard = Carta.objects.get(codigo='SWSH12-020')
            blastoise = Carta.objects.get(codigo='SWSH12-030')
            mewtwo = Carta.objects.get(codigo='SWSH4-079')
            eevee = Carta.objects.get(codigo='SWSH1-134')
            
            # Pedido 1: Ash
            pedido1 = Pedido.objects.create(
                cliente=ash,
                estado='ENTR',
                nombre_completo='Ash Ketchum',
                email='ash@pokemon.com',
                telefono='+34 600 111 222',
                direccion_envio='Calle Pokémon 123, Pueblo Paleta',
                ciudad_envio='Paleta',
                provincia_envio='Kanto',
                codigo_postal='28001',
                metodo_pago='TARJ',
                pagado=True,
                fecha_pago=datetime.now(),
                metodo_envio='Correos Express',
                numero_seguimiento='ES123456789',
                fecha_envio=datetime(2024, 1, 15, 10, 30),
                fecha_entrega_estimada=date(2024, 1, 17),
                notas_cliente='¡Mi primer pedido de cartas Pokémon!'
            )
            
            # Items del pedido 1
            ItemPedido.objects.create(
                pedido=pedido1,
                carta=pikachu,
                inventario=pikachu.inventario,
                cantidad=2,
                precio_unitario=pikachu.inventario.precio
            )
            
            ItemPedido.objects.create(
                pedido=pedido1,
                carta=charizard,
                inventario=charizard.inventario,
                cantidad=1,
                precio_unitario=charizard.inventario.precio
            )
            
            pedido1.calcular_totales()
            
            # Pedido 2: Misty
            pedido2 = Pedido.objects.create(
                cliente=misty,
                estado='ENVI',
                nombre_completo='Misty',
                email='misty@pokemon.com',
                telefono='+34 600 333 444',
                direccion_envio='Gimnasio Ciudad Celeste, Isla Canela',
                ciudad_envio='Ciudad Celeste',
                provincia_envio='Kanto',
                codigo_postal='28002',
                metodo_pago='PAYP',
                pagado=True,
                fecha_pago=datetime.now(),
                metodo_envio='DHL',
                numero_seguimiento='ES987654321',
                fecha_envio=datetime.now(),
                fecha_entrega_estimada=date(2024, 1, 25),
                notas_cliente='Cartas para mi colección de Pokémon de agua'
            )
            
            # Items del pedido 2
            ItemPedido.objects.create(
                pedido=pedido2,
                carta=blastoise,
                inventario=blastoise.inventario,
                cantidad=1,
                precio_unitario=blastoise.inventario.precio
            )
            
            pedido2.calcular_totales()
            
            # Pedido 3: Brock (en carrito)
            pedido3 = Pedido.objects.create(
                cliente=brock,
                estado='CARRITO',
                nombre_completo='Brock',
                email='brock@pokemon.com',
                telefono='+34 600 555 666',
                direccion_envio='Gimnasio Ciudad Plateada, Montaña Plateada',
                ciudad_envio='Ciudad Plateada',
                provincia_envio='Kanto',
                codigo_postal='28003'
            )
            
            # Items del pedido 3 (en carrito)
            ItemPedido.objects.create(
                pedido=pedido3,
                carta=mewtwo,
                inventario=mewtwo.inventario,
                cantidad=1,
                precio_unitario=mewtwo.inventario.precio
            )
            
            ItemPedido.objects.create(
                pedido=pedido3,
                carta=eevee,
                inventario=eevee.inventario,
                cantidad=3,
                precio_unitario=eevee.inventario.precio
            )
            
            pedido3.calcular_totales()
            
            print(f"3 pedidos creados")
            
        except Exception as e:
            print(f"Error creando pedidos: {e}")
    
    def crear_resenas(self):
        """Crea reseñas de ejemplo"""
        try:
            ash = User.objects.get(username='ash_ketchum')
            misty = User.objects.get(username='misty')
            brock = User.objects.get(username='brock')
            
            pikachu = Carta.objects.get(codigo='SWSH12-050')
            charizard = Carta.objects.get(codigo='SWSH12-020')
            blastoise = Carta.objects.get(codigo='SWSH12-030')
            
            # Reseña 1: Ash sobre Pikachu
            Resena.objects.create(
                carta=pikachu,
                usuario=ash,
                valoracion=5,
                titulo='¡Mi Pikachu favorito!',
                comentario='La calidad de esta carta es excelente. El holograma brilla mucho y llegó en perfectas condiciones.',
                condicion_recibida='NM',
                recomendado=True,
                aprobada=True,
                util_si=12,
                util_no=1
            )
            
            # Reseña 2: Misty sobre Blastoise
            Resena.objects.create(
                carta=blastoise,
                usuario=misty,
                valoracion=4,
                titulo='Gran carta de agua',
                comentario='El diseño es precioso y los ataques son muy poderosos. Le doy 4 estrellas porque el holograma tiene un pequeño rasguño.',
                condicion_recibida='LP',
                recomendado=True,
                aprobada=True,
                util_si=8,
                util_no=0
            )
            
            # Reseña 3: Brock sobre Charizard
            Resena.objects.create(
                carta=charizard,
                usuario=brock,
                valoracion=5,
                titulo='¡Impresionante!',
                comentario='Esta carta de Charizard es espectacular. El diseño VMAX es increíble y el daño que hace es brutal. Totalmente recomendada.',
                condicion_recibida='NM',
                recomendado=True,
                aprobada=True,
                util_si=15,
                util_no=2
            )
            
            print("3 reseñas creadas")
            
        except Exception as e:
            print(f"Error creando reseñas: {e}")
    
    def crear_colecciones(self):
        """Crea colecciones de ejemplo para usuarios"""
        try:
            ash = User.objects.get(username='ash_ketchum')
            coleccionista = User.objects.get(username='coleccionista')
            
            # Obtener cartas
            cartas_pikachu = Carta.objects.filter(nombre__icontains='Pikachu')
            cartas_charizard = Carta.objects.filter(nombre__icontains='Charizard')
            cartas_legendarias = Carta.objects.filter(
                categoria__nombre='Pokémon Legendario'
            )
            todas_cartas = Carta.objects.all()[:15]  # Limitar para la colección grande
            
            # Colección 1: Ash - Pokémon Iniciales
            coleccion1 = Coleccion.objects.create(
                usuario=ash,
                nombre='Pokémon Iniciales de Kanto',
                descripcion='Mi colección de los Pokémon iniciales de la región Kanto.',
                publica=True,
                total_cartas=0,
                valor_estimado=0
            )
            
            # Añadir cartas a la colección 1
            for carta in [cartas_pikachu.first(), cartas_charizard.first()]:
                if carta:
                    ColeccionCarta.objects.create(
                        coleccion=coleccion1,
                        carta=carta,
                        cantidad=1,
                        notas='Mi favorita de la colección',
                        estado='NM'
                    )
            
            coleccion1.actualizar_estadisticas()
            
            # Colección 2: Coleccionista - Cartas Legendarias
            coleccion2 = Coleccion.objects.create(
                usuario=coleccionista,
                nombre='Pokémon Legendarios',
                descripcion='Colección completa de Pokémon legendarios de todas las generaciones.',
                publica=False,
                total_cartas=0,
                valor_estimado=0
            )
            
            # Añadir cartas legendarias
            for carta in cartas_legendarias:
                ColeccionCarta.objects.create(
                    coleccion=coleccion2,
                    carta=carta,
                    cantidad=1,
                    estado='NM'
                )
            
            coleccion2.actualizar_estadisticas()
            
            # Colección 3: Colección Grande
            coleccion3 = Coleccion.objects.create(
                usuario=coleccionista,
                nombre='Mi Colección Completa',
                descripcion='Todas mis cartas Pokémon organizadas por expansión.',
                publica=True,
                total_cartas=0,
                valor_estimado=0
            )
            
            # Añadir múltiples cartas
            for i, carta in enumerate(todas_cartas):
                ColeccionCarta.objects.create(
                    coleccion=coleccion3,
                    carta=carta,
                    cantidad=1 if i % 3 != 0 else 2,  # Algunas duplicadas
                    notas=f'Carta #{i+1} de la colección',
                    estado='NM' if i % 2 == 0 else 'LP'
                )
            
            coleccion3.actualizar_estadisticas()
            
            print("3 colecciones creadas")
            
        except Exception as e:
            print(f"Error creando colecciones: {e}")
    
    def populate_all(self):
        """Ejecuta todo el proceso de población"""
        print("=" * 50)
        print("COMIENZO DE POBLACIÓN DE BASE DE DATOS")
        print("=" * 50)
        
        # 1. Crear superusuario
        print("\n1. Creando superusuario...")
        self.crear_superusuario()
        
        # 2. Crear usuarios normales
        print("\n2. Creando usuarios normales...")
        self.crear_usuarios_normales()
        
        # 3. Crear categorías
        print("\n3. Creando categorías...")
        self.crear_categorias()
        
        # 4. Crear expansiones
        print("\n4. Creando expansiones...")
        self.crear_expansiones()
        
        # 5. Crear cartas (esto descargará imágenes)
        print("\n5. Creando cartas (esto puede tomar unos segundos)...")
        self.crear_cartas_pokemon()
        
        # 6. Crear inventario
        print("\n6. Creando inventario...")
        self.crear_inventario()
        
        # 7. Crear pedidos
        print("\n7. Creando pedidos...")
        self.crear_pedidos()
        
        # 8. Crear reseñas
        print("\n8. Creando reseñas...")
        self.crear_resenas()
        
        # 9. Crear colecciones
        print("\n9. Creando colecciones...")
        self.crear_colecciones()
        
        print("\n" + "=" * 50)
        print("POBLACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 50)
        
        # Mostrar resumen
        print(f"\nRESUMEN:")
        print(f"- Usuarios: {User.objects.count()}")
        print(f"- Categorías: {Categoria.objects.count()}")
        print(f"- Expansiones: {Expansion.objects.count()}")
        print(f"- Cartas: {Carta.objects.count()}")
        print(f"- Inventario: {Inventario.objects.count()}")
        print(f"- Pedidos: {Pedido.objects.count()}")
        print(f"- Reseñas: {Resena.objects.count()}")
        print(f"- Colecciones: {Coleccion.objects.count()}")
        
        print("\nCredenciales de acceso:")
        print("Superusuario: admin / admin123")
        print("Usuario normal: ash_ketchum / pikachu123")


def main():
    """Función principal"""
    populator = DatabasePopulator()
    populator.populate_all()


if __name__ == '__main__':
    main()