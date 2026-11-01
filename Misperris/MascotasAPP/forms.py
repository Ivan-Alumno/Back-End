from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from MascotasAPP.models import Clientes, Mascotas
from MascotasAPP.validators import validate_email_domain_suffix


class RegistroForm(UserCreationForm):
    correo = forms.EmailField(
        label='Correo electrónico',
        validators=[validate_email_domain_suffix],
    )
    nombre = forms.CharField(label='Nombre', max_length=100)
    apellido_paterno = forms.CharField(label='Apellido paterno', max_length=100)
    apellido_materno = forms.CharField(
        label='Apellido materno',
        max_length=100,
        required=False,
    )
    telefono = forms.CharField(label='Teléfono', max_length=15)
    direccion = forms.CharField(label='Dirección', widget=forms.Textarea(attrs={'rows': 3}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'correo')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password1'].help_text = ''
        self.fields['password2'].label = 'Confirmar contraseña'
        self.fields['password2'].help_text = ''

    def clean_correo(self):
        correo = self.cleaned_data['correo'].strip()
        if User.objects.filter(email__iexact=correo).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        if Clientes.objects.filter(correo__iexact=correo).exists():
            raise forms.ValidationError('Ya existe un cliente con este correo.')
        return correo

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['correo']
        if commit:
            user.save()
            Clientes.objects.create(
                usuario=user,
                nombre=self.cleaned_data['nombre'],
                apellido_paterno=self.cleaned_data['apellido_paterno'],
                apellido_materno=self.cleaned_data['apellido_materno'],
                correo=self.cleaned_data['correo'],
                telefono=self.cleaned_data['telefono'],
                direccion=self.cleaned_data['direccion'],
            )
        return user


class ClienteGestionForm(forms.ModelForm):
    class Meta:
        model = Clientes
        exclude = ('usuario',)
        labels = {
            'nombre': 'Nombre',
            'apellido_paterno': 'Apellido paterno',
            'apellido_materno': 'Apellido materno',
            'correo': 'Correo electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
        }


class MascotaGestionForm(forms.ModelForm):
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
        fields = (
            'nombre',
            'raza',
            'sexo',
            'Edad',
            'descripcion',
            'foto',
            'estado_adopcion',
            'adoptado_por',
        )
        labels = {
            'nombre': 'Nombre',
            'raza': 'Raza',
            'sexo': 'Sexo',
            'Edad': 'Edad (años)',
            'descripcion': 'Descripción',
            'foto': 'Fotografía',
            'estado_adopcion': 'Estado de adopción',
            'adoptado_por': 'Adoptada por',
        }

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.pk and self.instance.adoptado_por_id:
            if cleaned_data.get('adoptado_por') is None:
                cleaned_data['estado_adopcion'] = 'disponible'
        return cleaned_data
