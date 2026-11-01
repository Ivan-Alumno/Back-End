from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models

from MascotasAPP.choices import estados_adopcion, sexos_mascotas
from MascotasAPP.validators import validate_email_domain_suffix


# Create your models here.
class Mascotas(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre de la mascota")
    raza = models.CharField(max_length=100, verbose_name="Raza de la mascota", blank=False, null=False)
    sexo = models.CharField(max_length=1, choices=sexos_mascotas, verbose_name="Sexo de la mascota")
    Edad = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        verbose_name="Edad (años)",
        help_text="Usa decimales para indicar meses; por ejemplo, 0.5 equivale a 6 meses.",
    )

    descripcion = models.TextField(verbose_name="Descripción de la mascota")
    añadido=models.DateTimeField(auto_now_add=True, verbose_name="Fecha de añadido")
    
    foto = models.ImageField(
        upload_to='Mascotas/',
        verbose_name="Foto de la mascota",
        blank=True,
    )
    
    estado_adopcion = models.CharField(
        max_length=10,
        choices=estados_adopcion,
        default='disponible',
        verbose_name="Estado de adopción",
    )
    
    adoptado_por = models.ForeignKey(
        'MascotasAPP.Clientes',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='mascotas_adoptadas',
        verbose_name="Adoptada por",
    )

    @property
    def edad_en_anos(self):
        return format(self.Edad.normalize(), 'f')

    @property
    def edad_formateada(self):
        total_meses = int(
            (Decimal(str(self.Edad)) * Decimal('12')).quantize(
                Decimal('1'),
                rounding=ROUND_HALF_UP,
            )
        )
        años, meses = divmod(total_meses, 12)

        partes = []
        if años:
            partes.append(f"{años} {'año' if años == 1 else 'años'}")
        if meses or not años:
            partes.append(f"{meses} {'mes' if meses == 1 else 'meses'}")
        return ' y '.join(partes)

    def clean(self):
        super().clean()
        if self.adoptado_por_id:
            self.estado_adopcion = 'adoptado'
        elif self.estado_adopcion == 'adoptado':
            raise ValidationError({
                'adoptado_por': 'Selecciona el cliente que adoptó esta mascota.',
            })

    def save(self, *args, **kwargs):
        if self.adoptado_por_id:
            self.estado_adopcion = 'adoptado'
        elif self.estado_adopcion == 'adoptado':
            raise ValidationError({
                'adoptado_por': 'Selecciona el cliente que adoptó esta mascota.',
            })
        super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.nombre)

    class Meta:
        db_table = "db_mascotas"
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"
        ordering = ["nombre", "raza", "sexo", "Edad", "añadido"]


class Clientes(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='perfil_cliente',
        verbose_name="Cuenta de usuario",
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre del cliente")
    apellido_paterno = models.CharField(max_length=100, verbose_name="Apellido paterno del cliente")
    apellido_materno = models.CharField(max_length=100, blank=True, verbose_name="Apellido materno del cliente")
    correo = models.EmailField(
        validators=[validate_email_domain_suffix],
        verbose_name="Correo electrónico",
    )
    
    telefono = models.CharField(max_length=15, verbose_name="Número de teléfono")
    direccion = models.TextField(verbose_name="Dirección del cliente")

    def __str__(self):
        return "{} {} {}".format(self.nombre, self.apellido_paterno, self.apellido_materno)

    class Meta:
        db_table = "db_clientes"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nombre", "apellido_paterno", "apellido_materno", "correo", "telefono"]


class SolicitudAdopcion(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    )

    cliente = models.ForeignKey(
        Clientes,
        on_delete=models.PROTECT,
        related_name='solicitudes_adopcion',
        verbose_name="Solicitante",
    )
    mascota = models.ForeignKey(
        Mascotas,
        on_delete=models.PROTECT,
        related_name='solicitudes_adopcion',
        verbose_name="Mascota solicitada",
    )
    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default='pendiente',
        verbose_name="Estado",
    )
    solicitada = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de solicitud",
    )

    class Meta:
        db_table = "db_solicitudes_adopcion"
        verbose_name = "Solicitud de adopción"
        verbose_name_plural = "Solicitudes de adopción"
        ordering = ('-solicitada',)

    def __str__(self):
        return f"{self.cliente} - {self.mascota} ({self.get_estado_display()})"