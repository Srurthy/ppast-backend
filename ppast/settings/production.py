from .base_settings import *
DEBUG = False

ALLOWED_HOSTS = [os.environ.get('AH_DOMAINIP'), os.environ.get('AH_DOMAINIP')]

# do we support ssl ?
SECURE_SSL_REDIRECT = False
DOMAIN = os.environ.get('DOMAINHOST')


ROOT_URLCONF = "ppast.urls"


WSGI_APPLICATION = "ppast.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.environ.get('DATABASE_NAME'),
                "USER":os.environ.get('DATABASE_USER'),
                "PASSWORD": os.environ.get('DATABASE_PASSWORD'),
                "HOST": os.environ.get('DATABASE_HOST'),
                "PORT": os.environ.get('DATABASE_PORT'),
            }
}



# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators


CORS_ORIGIN_ALLOW_ALL = False
# TODO: update the domain here
CORS_ORIGIN_WHITELIST = [
        "front end ip address",
]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT =os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER =os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD =os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_FROM = EMAIL_HOST_USER


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

