from django.db import models
from django.utils import timezone
from MascotasAPP.Choices import sexos

# Create your models here.
class Mascota(models.Model):
    nombre = models.CharField(max_length=100)
    raza = models.CharField(max_length=100)
    descripcion = models.TextField()
    foto = models.ImageField(upload_to='Mascotas/')

    def __str__(self):
        return self.nombre
