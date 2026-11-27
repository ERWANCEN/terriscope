# TerriScope

Plateforme d'exploration et de prospection commerciale géographique, construite à partir de la
Base permanente des équipements (BPE 2025) de l'INSEE, pour la région Centre-Val de Loire (code 24).

- **Carte publique** des 93 274 équipements géolocalisés de la région, chargés zone par zone,
  filtrables par domaine (3 niveaux) et par ville, avec une fiche détaillée par équipement.
- **Espace privé** : chaque utilisateur connecté place, modifie et supprime ses implantations
  commerciales potentielles, invisibles pour les autres utilisateurs.

Projet « Docker / Full Stack » – Groupe 1.

## Architecture

Trois conteneurs lancés par `docker compose` ; le code reste sur la machine hôte et il est monté par volume.

| Service | Image | Rôle | Port |
| --- | --- | --- | --- |
| `db` | `postgis/postgis:18-3.6` (officielle) | PostgreSQL + PostGIS | non exposé |
| `backend` | image construite par `backend/Dockerfile` (`python:3.13-slim` + GDAL) | API Django REST Framework | 8000 |
| `frontend` | `node:lts-slim` | Serveur de développement Vite (Vue 3) | 5173 |

Le navigateur ne parle qu'à Vite, qui relaie `/api` vers Django (pas de CORS) ; seul Django accède à la base.

## Installation

### Prérequis

- Docker Desktop (ou Docker Engine + Compose v2) et Git. **Aucune installation de Python ou de Node sur la machine hôte.**
- Le fichier parquet BPE 2025 fourni avec le sujet.

### Étapes

```bash
# 1. Récupérer le projet
git clone https://github.com/ERWANCEN/terriscope.git
cd terriscope

# 2. Créer le fichier de configuration (non versionné), puis changer les mots de passe et la clé secrète
cp .env.example .env

# 3. Copier le parquet dans data/ sous le nom bpe25_clean.parquet
#    (ou garder son nom et le préciser à l'import avec --file, voir ci-dessous)

# 4. Construire et démarrer les 3 conteneurs (les migrations sont appliquées au démarrage du backend)
docker compose up -d --build

# 5. Importer les équipements de la région 24 (environ 15 s)
docker compose exec backend python manage.py import_bpe --region 24
#    → « 93274 équipements importés »
```

Avec un autre nom de fichier : `docker compose exec backend python manage.py import_bpe --region 24 --file /data/<nom>.parquet`
(le dossier `data/` de l'hôte est monté sous `/data` dans le conteneur). L'import peut être relancé sans créer de doublon.

### Variables d'environnement (`.env`)

| Variable | Rôle | Exemple |
| --- | --- | --- |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Base créée au premier démarrage de `db` | `terriscope` |
| `POSTGRES_HOST`, `POSTGRES_PORT` | Accès du backend à la base | `db`, `5432` |
| `DJANGO_SECRET_KEY` | Clé secrète Django | longue chaîne aléatoire |
| `DJANGO_DEBUG` | `1` en développement | `1` |
| `DJANGO_ALLOWED_HOSTS` | Doit contenir `backend` (proxy Vite) et `localhost` | `localhost,127.0.0.1,backend` |

Le mot de passe de la base est fixé au **premier** démarrage de `db` et conservé dans le volume `pgdata` :
le modifier ensuite dans `.env` ne suffit pas (voir « Dépannage »).

## Utilisation

| URL | Contenu |
| --- | --- |
| http://localhost:5173 | Application (carte, filtres, fiche, connexion, implantations) |
| http://localhost:8000/api/docs/ | Documentation Swagger de l'API, testable en ligne |
| http://localhost:8000/admin/ | Administration Django (compte créé avec `createsuperuser`) |

Les comptes utilisateurs se créent depuis l'application (« Créer un compte ») ou avec `POST /api/auth/register/`.
Le parcours détaillé est dans [docs/utilisation.md](docs/utilisation.md).

### Commandes utiles

```bash
docker compose ps                                        # état des conteneurs
docker compose logs --tail=50 backend                    # logs de l'API
docker compose exec backend python manage.py check       # contrôle de la configuration Django
docker compose exec backend python manage.py createsuperuser
docker compose exec -T backend python manage.py spectacular > docs/openapi.yaml    # regénérer le schéma OpenAPI
docker compose exec frontend npm run build               # build de production du front
docker compose down                                      # arrêter (les données sont conservées)
```

## Données

- Source : parquet BPE 2025, filtré sur la région 24 dès la lecture (pyarrow), puis normalisé en 6 tables
  (`regions`, `depts`, `domaine1`, `domaine2`, `domaine3`, `bpe`) ; voir [docs/modele-donnees.md](docs/modele-donnees.md).
- **97 095 lignes pour la région 24, 93 274 importées** : les 3 821 équipements sans coordonnées sont écartés,
  car ils ne peuvent pas être placés sur une carte.
- Les libellés de la région et des 6 départements, absents du parquet, sont écrits dans la commande d'import.

## Versions

Dernières versions stables au 27/11/2026, avec les exceptions justifiées ci-dessous.

| Composant | Version |
| --- | --- |
| Python | 3.13 |
| Django + GeoDjango | 6.1.3 |
| Django REST Framework | 3.18.3 |
| djangorestframework-gis | 1.3.0 |
| drf-spectacular / django-filter | 0.30.0 / 26.2 |
| psycopg 3 / pandas / pyarrow | 3.3.9 / 3.1.1 / 26.0.1 |
| PostgreSQL / PostGIS | 18.6 / 3.6.4 |
| Node (image `node:lts-slim`) | 26 LTS |
| Vue / Vite | 3.5 / 7.3 |
| Leaflet / Leaflet.markercluster | 1.9.4 / 1.5.3 |

**Exceptions justifiées :**

- **Python 3.13 et non 3.14** : Django 6.1 supporte 3.14, mais djangorestframework-gis 1.3 n'est officiellement
  testé que jusqu'à 3.13. C'est la version la plus récente supportée par **toutes** les dépendances.
- **Leaflet 1.9.4 et non 2.0** : Leaflet 2.0 est encore en bêta.
- **PostgreSQL 18 et non 19** : PostgreSQL 19 n'est disponible qu'en bêta dans l'image officielle `postgis/postgis`.
- **`platform: linux/amd64` pour `db`** : l'image `postgis/postgis` n'est publiée qu'en amd64 ; sur Mac Apple Silicon,
  Docker l'émule (plus lent, mais fonctionnel). Sans effet sur un PC Intel ou AMD.

## Dépannage

| Symptôme | Cause et solution |
| --- | --- |
| `no matching manifest for linux/arm64` | Mac Apple Silicon : déjà géré par `platform: linux/amd64` dans `docker-compose.yaml` |
| L'API ne répond plus après un `git pull` | Le serveur Django s'est rechargé pendant la mise à jour des fichiers : `docker compose restart backend` |
| `password authentication failed for user …` | Le mot de passe de `.env` ne correspond plus à celui enregistré dans le volume `pgdata` : remettre l'ancien mot de passe dans `.env`, ou repartir de zéro avec `docker compose down -v` (supprime la base : il faut relancer l'import) |
| `0 équipements importés` ou `FileNotFoundError` | Vérifier le nom du parquet dans `data/` et l'option `--file` |
| Erreur `401` sur `/api/implantations/` | Header attendu : `Authorization: Token <clé>` (le mot `Token`, pas `Bearer`) |
| Le port 8000 ou 5173 est déjà pris | Arrêter l'application qui l'utilise, ou changer le port à gauche dans `docker-compose.yaml` (`"8001:8000"`) |

## Documentation

- Modèle de données : [docs/modele-donnees.md](docs/modele-donnees.md)
- API : [docs/api.md](docs/api.md), Swagger sur http://localhost:8000/api/docs/ et schéma [docs/openapi.yaml](docs/openapi.yaml)
- Utilisation : [docs/utilisation.md](docs/utilisation.md)
- Post-mortem : [docs/post-mortem.md](docs/post-mortem.md)
- Journaux de bord de l'équipe : [docs/journal/](docs/journal/)

## Outils

Développé avec l'assistance de Claude Code, Codex et Gemini Code Assist. Consignes communes aux assistants : `AGENTS.md`.
