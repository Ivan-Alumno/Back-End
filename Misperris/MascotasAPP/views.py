from django.shortcuts import render
from MascotasAPP.models import Mascotas

def inicio(request):
    mascotas = Mascotas.objects.order_by('-añadido')[:6]
    return render(request, 'inicio/inicio.html', {'mascotas': mascotas})

def galeria(request):
    mascotas = Mascotas.objects.all()
    return render(request, 'mascotas/galeria.html', {'mascotas': mascotas})
