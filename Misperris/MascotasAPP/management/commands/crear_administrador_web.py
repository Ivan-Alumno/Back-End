from getpass import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.db import transaction

from MascotasAPP.models import Clientes, Mascotas, SolicitudAdopcion
from MascotasAPP.permissions import SITE_ADMIN_GROUP_NAME
from MascotasAPP.validators import validate_email_domain_suffix


class Command(BaseCommand):
    help = 'Crea o asigna una cuenta al rol de administrador del sitio.'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('email')

    def handle(self, *_args, **options):
        if _args:
            raise CommandError('No se aceptan argumentos adicionales.')
        username = options['username'].strip()
        email = options['email'].strip()
        User = get_user_model()

        try:
            validate_email(email)
            validate_email_domain_suffix(email)
        except ValidationError as error:
            raise CommandError(f'Correo no válido: {error}') from error

        if not username:
            raise CommandError('El nombre de usuario no puede estar vacío.')

        user = User.objects.filter(username=username).first()
        crear_usuario = user is None
        if user is None:
            if User.objects.filter(email__iexact=email).exists():
                raise CommandError('Ya existe una cuenta con ese correo.')
            password = getpass('Contraseña nueva: ')
            confirmation = getpass('Confirma la contraseña: ')
            if password != confirmation:
                raise CommandError('Las contraseñas no coinciden.')
            user = User(username=username, email=email)
            try:
                validate_password(password, user)
            except ValidationError as error:
                raise CommandError(f'La contraseña no cumple los requisitos: {error}') from error
            user.set_password(password)
        elif user.email:
            if user.email.casefold() != email.casefold():
                raise CommandError('El correo no coincide con el usuario existente.')
        else:
            if User.objects.exclude(pk=user.pk).filter(email__iexact=email).exists():
                raise CommandError('Ya existe una cuenta con ese correo.')
            user.email = email

        with transaction.atomic():
            if crear_usuario:
                user.save()
            elif not user.pk:
                raise CommandError('No se pudo encontrar la cuenta de usuario.')
            elif not User.objects.filter(pk=user.pk, email__iexact=email).exists():
                user.save(update_fields=('email',))
            group, _ = Group.objects.get_or_create(name=SITE_ADMIN_GROUP_NAME)
            permissions = Permission.objects.filter(
                content_type__app_label='MascotasAPP',
                codename__in=[
                    f'{action}_{model._meta.model_name}'
                    for model in (Clientes, Mascotas, SolicitudAdopcion)
                    for action in ('add', 'change', 'delete', 'view')
                ],
            )
            group.permissions.set(permissions)
            user.groups.add(group)
        self.stdout.write(self.style.SUCCESS(
            f'La cuenta "{username}" ya tiene el rol {SITE_ADMIN_GROUP_NAME}.'
        ))
