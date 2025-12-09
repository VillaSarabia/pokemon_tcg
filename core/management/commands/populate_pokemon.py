# management/commands/populate_pokemon.py
from django.core.management.base import BaseCommand
from io import BytesIO
import requests
from PIL import Image, ImageDraw
from django.core.files.base import ContentFile
import time

class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de ejemplo de Pokémon TCG'
    
    def handle(self, *args, **options):
        from pokemon_tcg.populate_database import DatabasePopulator
        
        self.stdout.write(self.style.SUCCESS('Iniciando población de base de datos...'))
        
        populator = DatabasePopulator()
        populator.populate_all()
        
        self.stdout.write(self.style.SUCCESS('Base de datos poblada exitosamente!'))