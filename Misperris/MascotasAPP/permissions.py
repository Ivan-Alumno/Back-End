SITE_ADMIN_GROUP_NAME = 'Administradores del sitio'


def is_site_admin(user):
    return user.is_authenticated and (
        user.is_superuser
        or user.groups.filter(name=SITE_ADMIN_GROUP_NAME).exists()
    )
