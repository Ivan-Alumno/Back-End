# Misperris

Aplicación Django para gestionar clientes y mascotas disponibles para adopción.

## Configuración local (Windows / PowerShell)

1. Instala las dependencias:
   python -m pip install -r requirements.txt

2. Inicia MySQL desde XAMPP. La configuración local usa la base `MisperrisDB`,
   el usuario `root` y contraseña vacía. Asegúrate de que la base y
   ese usuario existan en phpMyAdmin.

3. Aplica las
   migraciones:

   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   python manage.py showmigrations
   ```

   `makemigrations` crea archivos versionados a partir de cambios en los modelos.
   `migrate` aplica esos archivos a la base de datos. La migración incluida
   renombra el apellido existente del cliente para conservar sus datos y añade
   campos para apellido materno (opcional) y fecha de registro. Las mascotas
   admiten edad decimal en años con una cifra decimal (por ejemplo, `0.5` para
   seis meses), foto opcional y estado **Disponible/Adoptado**. Al aplicar la
   migración, las edades existentes se conservan salvo el valor `0.05`, que se
   corrige a `0.5` para representar seis meses; las mascotas quedan disponibles.
   Adoptar una mascota no la elimina de la base de datos. La migración 0006
   vincula cada mascota con un cliente adoptante sin alterar las mascotas
   existentes.

4. Crea un superusuario si todavía no existe. Este comando solicita la
   contraseña de forma interactiva y no la guarda en el código:

   ```powershell
   python manage.py createsuperuser
   ```

   Si la cuenta ya existe, no la dupliques; inicia sesión o restablece su clave
   con `python manage.py changepassword Administrador`.

5. Inicia el servidor y entra al panel:
   python manage.py runserver

   Abre `http://127.0.0.1:8000/admin/`.


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