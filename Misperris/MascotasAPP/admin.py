from django.contrib import admin
from MascotasAPP.models import Clientes, Mascotas

class MascotasAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'raza', 'sexo', 'Edad', 'descripcion', 'foto')
    search_fields = ('nombre', 'raza', 'sexo', 'Edad', 'descripcion')
    list_filter = ('nombre', 'raza', 'sexo', 'Edad', 'descripcion')

class ClientesAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'correo', 'telefono')
    search_fields = ('nombre', 'apellido', 'correo', 'telefono')
    list_filter = ('nombre', 'apellido', 'correo', 'telefono')

admin.site.register(Mascotas, MascotasAdmin)
admin.site.register(Clientes, ClientesAdmin)