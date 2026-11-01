from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils.html import format_html

from MascotasAPP.models import Clientes, Mascotas, SolicitudAdopcion
from MascotasAPP.validators import validate_email_domain_suffix

class ValidatedUserChangeForm(UserChangeForm):
    email = forms.EmailField(
        required=False,
        validators=[validate_email_domain_suffix],
    )

class ValidatedUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        validators=[validate_email_domain_suffix],
    )

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email')

class ExistingMascotasField(forms.ModelMultipleChoiceField):
    def clean(self, value):
        if isinstance(value, (list, tuple)):
            value = [item for item in value if item not in self.empty_values]
        return super().clean(value)

class AvailableMascotasCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        if not self.choices:
            return format_html('<span>--</span>')
        return super().render(name, value, attrs, renderer)

class MascotasAdminForm(forms.ModelForm):
    Edad = forms.DecimalField(
        label='Edad (años)',
        help_text=(
            'Ingresa la edad en años; por ejemplo, 0.5 equivale aproximadamente '
            'a 6 meses. En las listas se muestra en años y meses.'
        ),
        max_digits=5,
        decimal_places=1,
    )

    class Meta:
        model = Mascotas
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.pk and self.instance.adoptado_por_id:
            if cleaned_data.get('adoptado_por') is None:
                cleaned_data['estado_adopcion'] = 'disponible'
        return cleaned_data

class ClientesAdminForm(forms.ModelForm):
    mascotas_disponibles = ExistingMascotasField(
        queryset=Mascotas.objects.none(),
        required=False,
        label='Mascotas disponibles',
        help_text=(
            'Marca las mascotas que adoptará este cliente. '
            'Solo aparecenan mascotas disponibles ya registradas.'
        ),
        widget=AvailableMascotasCheckboxSelectMultiple,
    )

    class Meta:
        model = Clientes
        exclude = ('usuario',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mascotas_disponibles = Mascotas.objects.filter(
            adoptado_por__isnull=True,
            estado_adopcion='disponible',
        ).order_by('nombre', 'raza')
        field = self.fields['mascotas_disponibles']
        field.queryset = mascotas_disponibles

@admin.register(Mascotas)
class MascotasAdmin(admin.ModelAdmin):
    form = MascotasAdminForm
    list_display = (
        'nombre',
        'raza',
        'sexo',
        'edad',
        'estado_adopcion',
        'adoptado_por',
        'añadido',
    )
    list_display_links = ('nombre',)
    list_filter = ('estado_adopcion', 'sexo', 'raza')
    search_fields = ('nombre', 'raza', 'descripcion')
    readonly_fields = ('añadido',)
    list_per_page = 25
    ordering = ('nombre',)
    fieldsets = (
        ('Datos de la mascota', {
            'fields': (
                'nombre',
                'raza',
                'sexo',
                'Edad',
                'estado_adopcion',
                'adoptado_por',
                'descripcion',
                'foto',
            ),
        }),
        ('Registro', {'fields': ('añadido',)}),
    )

    @admin.display(description='Edad', ordering='Edad')
    def edad(self, obj):
        return obj.edad_formateada

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'adoptado_por':
            kwargs['empty_label'] = '---------'
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'adoptado_por':
            widget = field.widget
            widget.can_add_related = False
            widget.can_change_related = False
            widget.can_delete_related = False
        return field

@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    form = ClientesAdminForm
    list_display = (
        'nombre',
        'apellido_paterno',
        'apellido_materno',
        'correo',
        'telefono',
        'mascotas_adoptadas',
    )
    list_display_links = ('nombre', 'apellido_paterno')
    list_filter = ('apellido_paterno', 'apellido_materno')
    search_fields = ('nombre', 'apellido_paterno', 'apellido_materno', 'correo', 'telefono')
    list_per_page = 25
    ordering = ('apellido_paterno', 'apellido_materno', 'nombre')
    fieldsets = (
        ('Datos personales', {
            'fields': (
                'nombre',
                'apellido_paterno',
                'apellido_materno',
                'mascotas_adoptadas_actuales',
            ),
        }),
        ('Contacto', {'fields': ('correo', 'telefono', 'direccion')}),
        ('Adopciones', {'fields': ('mascotas_disponibles',)}),
    )
    readonly_fields = ('mascotas_adoptadas_actuales',)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        cliente = form.instance
        for mascota in form.cleaned_data['mascotas_disponibles']:
            mascota.adoptado_por = cliente
            mascota.estado_adopcion = 'adoptado'
            mascota.save(update_fields=('adoptado_por', 'estado_adopcion'))

    @admin.display(description='Mascotas adoptadas')
    def mascotas_adoptadas(self, obj):
        return ', '.join(
            mascota.nombre for mascota in obj.mascotas_adoptadas.all()
        ) or 'Ninguna'

    @admin.display(description='Mascotas adoptadas')
    def mascotas_adoptadas_actuales(self, obj):
        if not obj.pk:
            return '--'
        return self.mascotas_adoptadas(obj)

class ValidatedUserAdmin(UserAdmin):
    form = ValidatedUserChangeForm
    add_form = ValidatedUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

admin.site.unregister(User)
admin.site.register(User, ValidatedUserAdmin)


@admin.register(SolicitudAdopcion)
class SolicitudAdopcionAdmin(admin.ModelAdmin):
    list_display = ('mascota', 'cliente', 'estado', 'solicitada')
    list_filter = ('estado', 'solicitada')
    search_fields = (
        'mascota__nombre',
        'cliente__nombre',
        'cliente__apellido_paterno',
        'cliente__correo',
    )
    readonly_fields = ('cliente', 'mascota', 'estado', 'solicitada')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False