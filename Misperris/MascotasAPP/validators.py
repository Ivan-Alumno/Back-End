from django.core.exceptions import ValidationError

COMMON_EMAIL_SUFFIXES = {
    'ai',
    'app',
    'biz',
    'cl',
    'com',
    'dev',
    'edu',
    'gov',
    'info',
    'int',
    'io',
    'mil',
    'net',
    'org',
}

def validate_email_domain_suffix(value):
    domain = value.rsplit('@', 1)[-1]
    suffix = domain.rsplit('.', 1)[-1].lower()
    if not suffix.isalpha() or (
        len(suffix) != 2 and suffix not in COMMON_EMAIL_SUFFIXES
    ):
        raise ValidationError(
            'Usa un dominio con una extensión reconocida, como .com o .cl.',
            code='invalid_email_suffix',
        )
