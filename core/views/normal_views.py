from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from ..models import Carta, Categoria, Expansion, Coleccion, ColeccionCarta

def home_view(request):
    return render(request, 'base.html')