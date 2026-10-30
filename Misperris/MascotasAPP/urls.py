from django.urls import path
from django.contrib.auth import views as auth_views

from MascotasAPP import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('adoptables/', views.adoptables, name='adoptables'),
    path('cuenta/registro/', views.registro, name='registro'),
    path(
        'cuenta/iniciar-sesion/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login',
    ),
    path(
        'cuenta/cerrar-sesion/',
        auth_views.LogoutView.as_view(),
        name='logout',
    ),
    path(
        'adopcion/solicitar/<int:mascota_id>/',
        views.solicitar_adopcion,
        name='solicitar_adopcion',
    ),
    path('gestion/', views.gestion_inicio, name='gestion_inicio'),
    path('gestion/clientes/', views.gestion_clientes, name='gestion_clientes'),
    path(
        'gestion/clientes/nuevo/',
        views.gestion_cliente_form,
        name='gestion_cliente_nuevo',
    ),
    path(
        'gestion/clientes/<int:cliente_id>/editar/',
        views.gestion_cliente_form,
        name='gestion_cliente_editar',
    ),
    path(
        'gestion/clientes/<int:cliente_id>/eliminar/',
        views.gestion_cliente_eliminar,
        name='gestion_cliente_eliminar',
    ),
    path('gestion/mascotas/', views.gestion_mascotas, name='gestion_mascotas'),
    path(
        'gestion/mascotas/nueva/',
        views.gestion_mascota_form,
        name='gestion_mascota_nueva',
    ),
    path(
        'gestion/mascotas/<int:mascota_id>/editar/',
        views.gestion_mascota_form,
        name='gestion_mascota_editar',
    ),
    path(
        'gestion/mascotas/<int:mascota_id>/eliminar/',
        views.gestion_mascota_eliminar,
        name='gestion_mascota_eliminar',
    ),
    path(
        'gestion/solicitudes/<int:solicitud_id>/<str:accion>/',
        views.gestionar_solicitud,
        name='gestionar_solicitud',
    ),
]