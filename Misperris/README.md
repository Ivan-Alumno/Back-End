# Misperris

Aplicación Django para gestionar clientes y mascotas disponibles para adopción.

## Configuración local (Windows / PowerShell)

1. Instalación de las dependencias:
   `python -m pip install -r dependencias.txt`

2. Inicia MySQL desde XAMPP. 
   La configuración local usa la base `MisperrisDB`,
   el usuario `root` y la contraseña vacía.

3. Aplicar las migraciones:
   `python manage.py makemigrations`
   `python manage.py migrate`
   `python manage.py showmigrations`

   La migración 0007 vincula opcionalmente una cuenta con un cliente y crea la
   tabla de solicitudes de adopción. No borra los clientes ni las mascotas
   existentes.

4. Crea un superusuario si todavía no existe. Este comando solicita la
   contraseña de forma interactiva y no la guarda en el código:

   `python manage.py createsuperuser`

   Si existe inicia sesión o restablece su clave con
   `python manage.py changepassword Administrador`.

5. Inicia el servidor y entra al panel:
   python manage.py runserver

   Abre `http://127.0.0.1:8000/gestion/` para el panel privado del sitio. El
   Admin estándar de Django conserva la ruta definida en `Database/urls.py`.

## Cuentas, adopciones y administración privada

El encabezado permite iniciar sesión o registrarse. El registro solicita nombre,
apellidos, correo, teléfono, dirección, nombre de usuario y contraseña; crea una
cuenta de Django y su ficha de cliente vinculada. Las contraseñas usan la
validación integrada de Django y nunca se guardan en texto plano.
La portada muestra un banner con la imagen local del proyecto, la hora del
servidor y los conteos de clientes y mascotas registrados.

Una persona registrada puede enviar una solicitud desde la galería para una
mascota disponible. La solicitud queda pendiente y no cambia por sí sola el
estado de la mascota. Un administrador del sitio puede aprobarla (asigna la
mascota al cliente y marca como rechazadas otras solicitudes pendientes para
esa mascota) o rechazarla.

El panel privado está en `/gestion/` y permite gestionar solicitudes, clientes
y mascotas. Solo los superusuarios y miembros del grupo **Administradores del
sitio** pueden entrar. Si una persona autenticada sin permisos intenta abrir
una sección de gestión, recibe un aviso y vuelve al inicio. Para crear una
cuenta de ese rol desde PowerShell:

```powershell
python manage.py migrate
python manage.py crear_administrador_web nombre_usuario correo@example.com
```

El comando solicita la contraseña de manera interactiva, valida su seguridad y
asigna permisos de gestión de clientes, mascotas y solicitudes. No se debe
guardar una contraseña en el código. Los administradores creados con este
comando no necesitan ser superusuarios ni acceder al Admin estándar de Django.
En esta evaluación cerrada, la página de inicio de sesión muestra las
credenciales de la cuenta de evaluación para que el profesor pueda acceder.


## Administración y permisos

Los modelos `Mascotas` y `Clientes` están registrados en Django Admin con
búsqueda, filtros, paginación y formularios agrupados.

Los usuarios anónimos no pueden entrar al panel.
Las mascotas se agregan y modifican ahora desde Admin, incluyendo su fotografía.

En Admin se puede asignar un cliente desde la ficha de la mascota o seleccionar
mascotas ya registradas desde la ficha del cliente. En Clientes, las mascotas ya
adoptadas aparecen junto a los datos del cliente y las disponibles se muestran
aparte como casillas de selección; si no hay mascotas disponibles, se muestra
`--`. Desde Clientes no se pueden crear mascotas ni introducir sus datos. Al
marcar una disponible, queda como **Adoptado** automáticamente; el Admin muestra
el vínculo en ambas fichas y no permite eliminar a un cliente que tenga mascotas
adoptadas.
En la ficha de una mascota, el cliente adoptante se elige con un desplegable
que incluye `---------` para dejarla sin adoptante y disponible al guardar.
Desde ese campo solo se puede consultar la ficha del cliente; no se muestran
acciones para crear, editar o eliminar clientes.
Los formularios de clientes y usuarios del Admin aceptan extensiones de correo
comunes (como `.com` y `.cl`) y códigos de país de dos letras. Esta comprobación
valida el formato, no confirma que el buzón exista o reciba mensajes.