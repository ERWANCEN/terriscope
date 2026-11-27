FROM python:3.13-slim

# Pas de fichiers .pyc, et logs affichés immédiatement
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Bibliothèques système requises par GeoDjango (GDAL, GEOS, PROJ)
RUN apt-get update && apt-get install -y --no-install-recommends \
        binutils libproj-dev gdal-bin \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Seules les dépendances sont copiées : l'image n'est reconstruite que si elles changent
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Le code n'est PAS copié : il est monté par volume depuis l'hôte (exigence du sujet)
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
