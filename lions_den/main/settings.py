"""
Django settings for main project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'snpn+vt4z@(nazt0o@r5$x9t2&@ua1wwz$(d_=qzpcqm*4y57_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
	'ticket_system.apps.TicketSystemConfig',
	'zoo_auth.apps.ZooAuthConfig',
	'zoo_editor.apps.ModelEditorConfig',
	'crispy_forms',
	'django.forms',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [BASE_DIR / 'templates'],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

WSGI_APPLICATION = 'main.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': BASE_DIR / 'default.sqlite3',
	}
}
# Add custom databases
for db_file in (BASE_DIR / 'zoo_editor' / 'databases').iterdir():
    zoo_id = db_file.name.split('.')[0]
    DATABASES[zoo_id] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': db_file,
    }

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-GB'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static"
]

# Media
MEDIA_ROOT = BASE_DIR / 'media/'
MEDIA_URL = 'media/'

# Crispy
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Authentication
AUTH_USER_MODEL = 'zoo_auth.ZooUser'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/zoos'

# Email
EMAIL_USE_SSL = True
EMAIL_PORT = 465
EMAIL_HOST = 'mail.zooverse.org'
EMAIL_HOST_USER = 'contact@zooverse.org'
EMAIL_HOST_PASSWORD =  'ZSL@ldn2020'

# Allow additional template definitions
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'