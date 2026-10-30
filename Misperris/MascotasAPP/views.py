from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods

from MascotasAPP.forms import ClienteGestionForm, MascotaGestionForm, RegistroForm
from MascotasAPP.models import Clientes, Mascotas, SolicitudAdopcion
from MascotasAPP.permissions import is_site_admin


def inicio(request):
    mascotas = Mascotas.objects.order_by('-añadido')[:6]
    return render(request, 'inicio/inicio.html', {
        'mascotas': mascotas,
        'cantidad_clientes': Clientes.objects.count(),
        'cantidad_mascotas': Mascotas.objects.count(),
        'hora_actual': timezone.localtime(),
    })


def adoptables(request):
    mascotas = Mascotas.objects.all()
    cliente = Clientes.objects.filter(usuario=request.user).first() if request.user.is_authenticated else None
    solicitudes_pendientes = set()
    if cliente:
        solicitudes_pendientes = set(
            SolicitudAdopcion.objects.filter(
                cliente=cliente,
                estado='pendiente',
            ).values_list('mascota_id', flat=True)
        )
    return render(request, 'mascotas/adoptables.html', {
        'mascotas': mascotas,
        'puede_solicitar': cliente is not None,
        'solicitudes_pendientes': solicitudes_pendientes,
        'es_admin_sitio': is_site_admin(request.user),
    })


def registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    form = RegistroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                user = form.save()
                login(request, user)
        except IntegrityError:
            form.add_error(None, 'No se pudo crear la cuenta. Comprueba que el usuario y el correo no estén registrados.')
        else:
            messages.success(request, 'Tu cuenta fue creada. Ya puedes solicitar adopciones.')
            return redirect('adoptables')
    return render(request, 'registration/register.html', {'form': form})


@login_required
@require_POST
def solicitar_adopcion(request, mascota_id):
    cliente = Clientes.objects.filter(usuario=request.user).first()
    if cliente is None:
        messages.error(request, 'Tu cuenta no tiene un perfil de cliente para solicitar adopciones.')
        return redirect('adoptables')

    try:
        with transaction.atomic():
            mascota = Mascotas.objects.select_for_update().get(pk=mascota_id)
            if mascota.estado_adopcion != 'disponible' or mascota.adoptado_por_id:
                messages.error(request, 'Esta mascota ya no está disponible.')
                return redirect('adoptables')
            solicitud_activa = SolicitudAdopcion.objects.filter(
                cliente=cliente,
                mascota=mascota,
                estado='pendiente',
            ).exists()
            if solicitud_activa:
                messages.info(request, 'Ya tienes una solicitud pendiente para esta mascota.')
                return redirect('adoptables')
            SolicitudAdopcion.objects.create(cliente=cliente, mascota=mascota)
    except Mascotas.DoesNotExist as error:
        raise Http404('No existe esa mascota.') from error

    messages.success(request, 'Tu solicitud fue enviada al administrador.')
    return redirect('adoptables')


def site_admin_required(view_func):
    @login_required(login_url='login')
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not is_site_admin(request.user):
            messages.warning(
                request,
                'No tienes permisos para acceder al área de administración.',
            )
            return redirect('inicio')
        return view_func(request, *args, **kwargs)

    return wrapped


@site_admin_required
def gestion_inicio(request):
    solicitudes = SolicitudAdopcion.objects.select_related(
        'cliente',
        'mascota',
    ).order_by('estado', '-solicitada')
    return render(request, 'gestion/dashboard.html', {
        'solicitudes': solicitudes,
        'solicitudes_pendientes': solicitudes.filter(estado='pendiente'),
        'cantidad_clientes': Clientes.objects.count(),
        'cantidad_mascotas': Mascotas.objects.count(),
        'cantidad_pendientes': solicitudes.filter(estado='pendiente').count(),
    })


@site_admin_required
def gestion_clientes(request):
    clientes = Clientes.objects.order_by('apellido_paterno', 'nombre')
    return render(request, 'gestion/clientes.html', {'clientes': clientes})


@site_admin_required
@require_http_methods(['GET', 'POST'])
def gestion_cliente_form(request, cliente_id=None):
    cliente = get_object_or_404(Clientes, pk=cliente_id) if cliente_id else None
    form = ClienteGestionForm(request.POST or None, instance=cliente)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cliente guardado correctamente.')
        return redirect('gestion_clientes')
    return render(request, 'gestion/record_form.html', {
        'form': form,
        'titulo': 'Editar cliente' if cliente else 'Añadir cliente',
        'volver_url': 'gestion_clientes',
    })


@site_admin_required
@require_POST
def gestion_cliente_eliminar(request, cliente_id):
    cliente = get_object_or_404(Clientes, pk=cliente_id)
    try:
        cliente.delete()
    except ProtectedError:
        messages.error(request, 'No se puede eliminar este cliente porque tiene mascotas adoptadas o solicitudes registradas.')
    else:
        messages.success(request, 'Cliente eliminado correctamente.')
    return redirect('gestion_clientes')


@site_admin_required
def gestion_mascotas(request):
    mascotas = Mascotas.objects.select_related('adoptado_por').order_by('nombre')
    return render(request, 'gestion/mascotas.html', {'mascotas': mascotas})


@site_admin_required
@require_http_methods(['GET', 'POST'])
def gestion_mascota_form(request, mascota_id=None):
    mascota = get_object_or_404(Mascotas, pk=mascota_id) if mascota_id else None
    form = MascotaGestionForm(request.POST or None, request.FILES or None, instance=mascota)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Mascota guardada correctamente.')
        return redirect('gestion_mascotas')
    return render(request, 'gestion/record_form.html', {
        'form': form,
        'titulo': 'Editar mascota' if mascota else 'Añadir mascota',
        'volver_url': 'gestion_mascotas',
    })


@site_admin_required
@require_POST
def gestion_mascota_eliminar(request, mascota_id):
    mascota = get_object_or_404(Mascotas, pk=mascota_id)
    try:
        mascota.delete()
    except ProtectedError:
        messages.error(request, 'No se puede eliminar esta mascota porque tiene solicitudes de adopción.')
    else:
        messages.success(request, 'Mascota eliminada correctamente.')
    return redirect('gestion_mascotas')


@site_admin_required
@require_POST
def gestionar_solicitud(request, solicitud_id, accion):
    if accion not in ('aprobar', 'rechazar'):
        raise Http404('Acción no válida.')

    if accion == 'rechazar':
        with transaction.atomic():
            solicitud = get_object_or_404(
                SolicitudAdopcion.objects.select_for_update(),
                pk=solicitud_id,
            )
            if solicitud.estado != 'pendiente':
                messages.info(request, 'La solicitud ya fue procesada.')
            else:
                solicitud.estado = 'rechazada'
                solicitud.save(update_fields=('estado',))
                messages.success(request, 'Solicitud rechazada.')
        return redirect('gestion_inicio')

    with transaction.atomic():
        solicitud = get_object_or_404(SolicitudAdopcion, pk=solicitud_id)
        mascota = get_object_or_404(
            Mascotas.objects.select_for_update(),
            pk=solicitud.mascota_id,
        )
        solicitud = get_object_or_404(
            SolicitudAdopcion.objects.select_for_update(),
            pk=solicitud_id,
        )
        if solicitud.estado != 'pendiente':
            messages.info(request, 'La solicitud ya fue procesada.')
        elif mascota.estado_adopcion != 'disponible' or mascota.adoptado_por_id:
            solicitud.estado = 'rechazada'
            solicitud.save(update_fields=('estado',))
            messages.error(request, 'La mascota ya no está disponible; la solicitud se marcó como rechazada.')
        else:
            mascota.adoptado_por = solicitud.cliente
            mascota.estado_adopcion = 'adoptado'
            mascota.save(update_fields=('adoptado_por', 'estado_adopcion'))
            solicitud.estado = 'aprobada'
            solicitud.save(update_fields=('estado',))
            SolicitudAdopcion.objects.filter(
                mascota=mascota,
                estado='pendiente',
            ).exclude(pk=solicitud.pk).update(estado='rechazada')
            messages.success(request, 'Solicitud aprobada y mascota asignada al cliente.')
    return redirect('gestion_inicio')
