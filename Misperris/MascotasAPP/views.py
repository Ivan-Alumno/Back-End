import json
from pathlib import Path
from django.shortcuts import render

BASE_DIR = Path(__file__).resolve().parent.parent

def cargar_mascotas_desde_json():
    json_path = BASE_DIR / 'Mascotas' / 'Data' / 'Mascotas.json'

    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
            if isinstance(datos, list):
                return datos

def index(request):
    mascotas = cargar_mascotas_desde_json()
    return render(request, 'index/index.html', {'Mascotas': mascotas})

def galeria(request):
    mascotas = cargar_mascotas_desde_json()
    return render(request, 'mascotas/galeria.html', {'Mascotas': mascotas})