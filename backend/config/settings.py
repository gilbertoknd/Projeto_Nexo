import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega arquivo .env da raiz do projeto ou da pasta backend
load_dotenv(BASE_DIR.parent / '.env')
load_dotenv(BASE_DIR / '.env')

# Segurança & Core
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key-contratacao-mvp-2026')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 't')

allowed_hosts_raw = os.environ.get('DJANGO_ALLOWED_HOSTS', '*')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_raw.split(',') if host.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Terceiros
    'rest_framework',
    'corsheaders',
    # App local
    'servicos',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Deve vir no topo
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Banco de Dados (PostgreSQL via Docker Compose)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'contratacao_db'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgrespassword'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# Internacionalização e Fuso Horário (Importante para os jobs das 00:00 e 01:00)
LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'pt-br')
TIME_ZONE = os.environ.get('TIME_ZONE', 'America/Recife')
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS (Permite comunicação com o Next.js)
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'True').lower() in ('true', '1', 't')
cors_origins_raw = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins_raw.split(',') if origin.strip()]

# Configurações do Celery + RabbitMQ
rabbitmq_user = os.environ.get('RABBITMQ_DEFAULT_USER', 'guest')
rabbitmq_pass = os.environ.get('RABBITMQ_DEFAULT_PASS', 'guest')
rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
rabbitmq_port = os.environ.get('RABBITMQ_PORT', '5672')
default_broker_url = f'amqp://{rabbitmq_user}:{rabbitmq_pass}@{rabbitmq_host}:{rabbitmq_port}//'

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', default_broker_url)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = False

# Garante que se o worker cair no meio da task, a mensagem volta pra fila
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
