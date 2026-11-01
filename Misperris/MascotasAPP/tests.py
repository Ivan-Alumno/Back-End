from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from MascotasAPP.models import Clientes, Mascotas, SolicitudAdopcion
from MascotasAPP.permissions import SITE_ADMIN_GROUP_NAME


class PublicAdoptionFlowTests(TestCase):
    def setUp(self):
        self.pet = Mascotas.objects.create(
            nombre='Luna',
            raza='Mestiza',
            sexo='H',
            Edad='1.0',
            descripcion='Amigable',
        )

    def test_public_pages_and_authentication_forms_render(self):
        for route_name in ('inicio', 'adoptables', 'login', 'registro'):
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)

        gallery = self.client.get(reverse('adoptables'))
        self.assertContains(gallery, 'Inicia sesión para adoptar')
        self.assertNotContains(gallery, 'Crear cuenta')
        self.assertNotContains(gallery, 'Quienes Somos')
        self.assertNotContains(
            self.client.get(reverse('login')),
            'nav-button-light',
        )

    def test_login_error_is_rendered_below_password_field(self):
        response = self.client.post(reverse('login'), {
            'username': 'adoptante',
            'password': 'incorrecta',
        })

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        password_field_position = content.index('name="password"')
        error_position = content.index('class="form-errors"')
        self.assertGreater(error_position, password_field_position)

    def test_password_rules_are_explained_without_default_help_list(self):
        response = self.client.get(reverse('registro'))

        self.assertContains(response, 'data-password-rule="length"')
        self.assertContains(response, 'data-password-rule="numeric"')
        self.assertContains(response, 'data-password-rule="match"')
        self.assertContains(response, 'password-validation.js')
        self.assertContains(response, 'contraseñas comunes')

    def test_password_confirmation_starts_neutral_instead_of_claiming_match(self):
        response = self.client.get(reverse('registro'))

        self.assertContains(response, 'Confirma tu contraseña')
        self.assertContains(response, 'data-message-mismatch="Las contraseñas no coinciden"')
        self.assertContains(response, 'data-message-match="Las contraseñas coinciden"')
        self.assertNotContains(response, '>Las contraseñas coinciden</li>')

    def test_pet_age_is_formatted_as_years_and_months(self):
        cases = (
            ('0.3', '4 meses'),
            ('0.5', '6 meses'),
            ('1.0', '1 año'),
            ('1.5', '1 año y 6 meses'),
            ('2.0', '2 años'),
        )

        for age, expected in cases:
            with self.subTest(age=age):
                pet = Mascotas(
                    nombre='Luna',
                    raza='Mestiza',
                    sexo='H',
                    Edad=Decimal(age),
                    descripcion='Amigable',
                )
                self.assertEqual(pet.edad_formateada, expected)

    def test_homepage_shows_database_totals_and_banner(self):
        Clientes.objects.create(
            nombre='Ana',
            apellido_paterno='Pérez',
            correo='ana@example.com',
            telefono='56912345678',
            direccion='Calle de prueba 123',
        )

        response = self.client.get(reverse('inicio'))

        self.assertEqual(response.context['cantidad_clientes'], 1)
        self.assertEqual(response.context['cantidad_mascotas'], 1)
        self.assertContains(response, 'images/Perros_portada.png')
        self.assertContains(response, 'home-clock')
        self.assertContains(response, 'Edad:</strong> 1 año')

        gallery = self.client.get(reverse('adoptables'))
        self.assertContains(gallery, 'Edad:</strong> 1 año')

    def test_registration_creates_user_and_linked_client(self):
        response = self.client.post(reverse('registro'), {
            'username': 'adoptante',
            'correo': 'adoptante@example.com',
            'nombre': 'Ana',
            'apellido_paterno': 'Pérez',
            'apellido_materno': 'Lagos',
            'telefono': '56912345678',
            'direccion': 'Calle de prueba 123',
            'password1': 'UnaClaveSegura!482',
            'password2': 'UnaClaveSegura!482',
        })

        self.assertRedirects(response, reverse('adoptables'))
        user = get_user_model().objects.get(username='adoptante')
        self.assertTrue(user.check_password('UnaClaveSegura!482'))
        self.assertEqual(user.perfil_cliente.correo, 'adoptante@example.com')
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_existing_account_can_log_in(self):
        get_user_model().objects.create_user(
            username='adoptante',
            password='UnaClaveSegura!482',
        )

        response = self.client.post(reverse('login'), {
            'username': 'adoptante',
            'password': 'UnaClaveSegura!482',
        })

        self.assertRedirects(response, reverse('inicio'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        login_page = self.client.get(reverse('login'))
        self.assertContains(login_page, 'Perris_Admin')

    def test_registered_customer_can_submit_only_one_pending_request(self):
        user = get_user_model().objects.create_user(
            username='adoptante',
            password='UnaClaveSegura!482',
        )
        Clientes.objects.create(
            usuario=user,
            nombre='Ana',
            apellido_paterno='Pérez',
            correo='ana@example.com',
            telefono='56912345678',
            direccion='Calle de prueba 123',
        )
        self.client.force_login(user)
        url = reverse('solicitar_adopcion', args=(self.pet.pk,))

        first_response = self.client.post(url)
        second_response = self.client.post(url)

        self.assertRedirects(first_response, reverse('adoptables'))
        self.assertRedirects(second_response, reverse('adoptables'))
        self.assertEqual(SolicitudAdopcion.objects.count(), 1)
        self.assertEqual(self.pet.estado_adopcion, 'disponible')

    def test_anonymous_user_cannot_submit_adoption_request(self):
        response = self.client.post(
            reverse('solicitar_adopcion', args=(self.pet.pk,))
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('solicitar_adopcion', args=(self.pet.pk,))}",
        )
        self.assertEqual(SolicitudAdopcion.objects.count(), 0)


class SiteAdministratorTests(TestCase):
    def setUp(self):
        self.pet = Mascotas.objects.create(
            nombre='Luna',
            raza='Mestiza',
            sexo='H',
            Edad='1.0',
            descripcion='Amigable',
        )
        self.user = get_user_model().objects.create_user(
            username='adoptante',
            password='UnaClaveSegura!482',
        )
        self.client_profile = Clientes.objects.create(
            usuario=self.user,
            nombre='Ana',
            apellido_paterno='Pérez',
            correo='ana@example.com',
            telefono='56912345678',
            direccion='Calle de prueba 123',
        )
        self.site_admin = get_user_model().objects.create_user(
            username='gestor',
            password='OtraClaveSegura!482',
        )
        group, _ = Group.objects.get_or_create(name=SITE_ADMIN_GROUP_NAME)
        self.site_admin.groups.add(group)
        self.request = SolicitudAdopcion.objects.create(
            cliente=self.client_profile,
            mascota=self.pet,
        )

    def test_regular_account_cannot_open_private_admin_area(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('gestion_inicio'), follow=True)

        self.assertRedirects(response, reverse('inicio'))
        self.assertContains(
            response,
            'No tienes permisos para acceder al área de administración.',
        )

    def test_regular_account_is_redirected_from_every_management_section(self):
        self.client.force_login(self.user)

        for route_name in ('gestion_clientes', 'gestion_mascotas'):
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertRedirects(response, reverse('inicio'))

    def test_site_administrator_can_open_private_dashboard(self):
        self.client.force_login(self.site_admin)

        response = self.client.get(reverse('gestion_inicio'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Luna')

    def test_site_administrator_can_open_client_and_pet_management(self):
        self.client.force_login(self.site_admin)

        clients_response = self.client.get(reverse('gestion_clientes'))
        pets_response = self.client.get(reverse('gestion_mascotas'))

        self.assertEqual(clients_response.status_code, 200)
        self.assertEqual(pets_response.status_code, 200)
        self.assertContains(clients_response, 'ana@example.com')
        self.assertContains(pets_response, 'Luna')

    def test_site_administrator_can_create_client_and_pet_records(self):
        self.client.force_login(self.site_admin)

        client_response = self.client.post(
            reverse('gestion_cliente_nuevo'),
            {
                'nombre': 'Mario',
                'apellido_paterno': 'Díaz',
                'apellido_materno': '',
                'correo': 'mario@example.com',
                'telefono': '56922222222',
                'direccion': 'Dirección de prueba',
            },
        )
        pet_response = self.client.post(
            reverse('gestion_mascota_nueva'),
            {
                'nombre': 'Nube',
                'raza': 'Mestiza',
                'sexo': 'D',
                'Edad': '0.5',
                'descripcion': 'Tranquila',
                'estado_adopcion': 'disponible',
                'adoptado_por': '',
            },
        )

        self.assertRedirects(client_response, reverse('gestion_clientes'))
        self.assertRedirects(pet_response, reverse('gestion_mascotas'))
        self.assertTrue(Clientes.objects.filter(correo='mario@example.com').exists())
        self.assertTrue(Mascotas.objects.filter(nombre='Nube').exists())

    def test_approving_request_assigns_pet_and_rejects_competing_requests(self):
        other_client = Clientes.objects.create(
            nombre='Luis',
            apellido_paterno='Rojas',
            correo='luis@example.com',
            telefono='56911111111',
            direccion='Otra dirección de prueba',
        )
        competing_request = SolicitudAdopcion.objects.create(
            cliente=other_client,
            mascota=self.pet,
        )
        self.client.force_login(self.site_admin)

        response = self.client.post(reverse(
            'gestionar_solicitud',
            args=(self.request.pk, 'aprobar'),
        ))

        self.assertRedirects(response, reverse('gestion_inicio'))
        self.pet.refresh_from_db()
        self.request.refresh_from_db()
        competing_request.refresh_from_db()
        self.assertEqual(self.pet.adoptado_por, self.client_profile)
        self.assertEqual(self.pet.estado_adopcion, 'adoptado')
        self.assertEqual(self.request.estado, 'aprobada')
        self.assertEqual(competing_request.estado, 'rechazada')

    def test_rejecting_request_keeps_pet_available(self):
        self.client.force_login(self.site_admin)

        self.client.post(reverse(
            'gestionar_solicitud',
            args=(self.request.pk, 'rechazar'),
        ))

        self.pet.refresh_from_db()
        self.request.refresh_from_db()
        self.assertEqual(self.pet.estado_adopcion, 'disponible')
        self.assertEqual(self.request.estado, 'rechazada')

    def test_management_command_assigns_site_admin_role_without_setting_staff(self):
        account = get_user_model().objects.create_user(
            username='nuevo_gestor',
            password='UnaClaveSegura!482',
        )

        call_command(
            'crear_administrador_web',
            'nuevo_gestor',
            'gestor@example.com',
            stdout=StringIO(),
        )

        account.refresh_from_db()
        self.assertFalse(account.is_staff)
        self.assertTrue(account.groups.filter(name=SITE_ADMIN_GROUP_NAME).exists())
        self.assertTrue(
            account.has_perm('MascotasAPP.change_mascotas')
        )
        self.client.force_login(account)
        homepage = self.client.get(reverse('inicio'))
        self.assertContains(homepage, 'Administración')
        self.assertContains(homepage, 'Clientes')
        self.assertContains(homepage, 'Mascotas')

    @patch(
        'MascotasAPP.management.commands.crear_administrador_web.getpass',
        side_effect=('ClaveNuevaSegura!482', 'ClaveNuevaSegura!482'),
    )
    def test_management_command_creates_admin_with_interactive_password(self, getpass_mock):
        call_command(
            'crear_administrador_web',
            'nuevo_administrador',
            'admin@example.com',
            stdout=StringIO(),
        )

        account = get_user_model().objects.get(username='nuevo_administrador')
        self.assertTrue(account.check_password('ClaveNuevaSegura!482'))
        self.assertFalse(account.is_staff)
        self.assertTrue(account.groups.filter(name=SITE_ADMIN_GROUP_NAME).exists())
        self.assertEqual(getpass_mock.call_count, 2)
