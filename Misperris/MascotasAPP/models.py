from django.db import models
from MascotasAPP.choices import sexos_mascotas

# Create your models here.
class Mascotas(models.Model):
    nombre = models.CharField(max_length=100)
    raza = models.CharField(max_length=100)
    sexo = models.CharField(max_length=1, choices=sexos_mascotas)
    Edad = models.IntegerField()
    descripcion = models.TextField()
    foto = models.ImageField(upload_to='Mascotas/')

    def __str__(self):
        return "{}".format(self.nombre)

    class Meta:
        db_table = "db_mascotas"
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"
        ordering = ["nombre", "raza", "sexo", "Edad"]


class Clientes(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()

    def __str__(self):
        return "{} {}".format(self.nombre, self.apellido)

    class Meta:
        db_table = "db_clientes"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nombre", "apellido", "correo", "telefono"]