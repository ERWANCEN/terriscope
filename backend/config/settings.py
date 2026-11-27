"""
Réglages Django de TerriScope.

Toutes les valeurs sensibles ou propres à la machine sont lues dans l'environnement
(fichier .env chargé par docker compose). Voir .env.example pour la liste des variables.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# --- Sécurité (valeurs lues dans .env) ---

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"

# "backend" est indispensable : c'est le nom d'hôte utilisé par le proxy Vite
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,backend").split(",")


# --- Applications ---

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",            # GeoDjango : champs géographiques (PointField…)
    "rest_framework",                # Django REST Framework
    "rest_framework_gis",            # sérialisation GeoJSON et filtre bbox
    "rest_framework.authtoken",      # authentification par token
    "django_filters",                # filtres déclaratifs (?domaine1=…&ville=…)
    "drf_spectacular",               # documentation OpenAPI / Swagger
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --- Base de données PostgreSQL + PostGIS ---

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ.get("POSTGRES_HOST", "db"),   # nom du service docker compose
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Mots de passe ---

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --- Langue et fuseau horaire ---

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True


# --- Fichiers statiques (admin, Swagger) ---

STATIC_URL = "static/"


# --- E-mails : affichés dans la console en développement ---

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}


# --- Django REST Framework ---

REST_FRAMEWORK = {
    # Header attendu : "Authorization: Token <clé>" (pas Bearer).
    # La session sert seulement à tester l'API depuis le navigateur (API navigable, Swagger).
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Lecture publique par défaut ; chaque vue privée (implantations) exige la connexion.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "TerriScope API",
    "DESCRIPTION": "Équipements BPE 2025 de la région Centre-Val de Loire et implantations privées.",
    "VERSION": "1.0.0",
}
