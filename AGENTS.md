# TerriScope – instructions pour les assistants de code

Ce fichier est la source unique des consignes pour tous les assistants de l'équipe :
Codex le lit directement, Gemini Code Assist via `.gemini/settings.json` (ou `GEMINI.md`),
et Claude Code via `CLAUDE.md`. Modifie ce fichier-ci, jamais une copie.

## Contexte

TerriScope : projet de classe d'une journée, équipe de 3 développeurs débutants en Django, Docker et Vue.
Application web : carte des équipements BPE 2025 (INSEE) de la région 24 (~97 095 équipements),
filtres par domaine (3 niveaux) et par ville, et implantations commerciales privées par utilisateur.

Le plan d'action détaillé (modèles, ETL, API, front, Docker, planning) est dans `docs/plan-action.md`.
Avant de coder une fonctionnalité, lis la section du plan qui la concerne.

## Stack imposée (ne pas changer sans accord de l'équipe)

- Back : Python 3.13, Django 6.1 + GeoDjango, Django REST Framework 3.18, djangorestframework-gis 1.3,
  django-filter, drf-spectacular, psycopg 3, pandas + pyarrow (ETL)
- Base : PostgreSQL 18 + PostGIS 3.6 (image `postgis/postgis:18-3.6`)
- Front : Vue 3 + Vite en JavaScript (pas de TypeScript), Leaflet 1.9.4 + Leaflet.markercluster
- INTERDIT : tout autre backend (Node/Express, PHP…), c'est 5 points de malus.
  Pas de TypeScript, Pinia, JWT, librairie UI lourde ni tuiles vectorielles.

## Tout tourne dans Docker

Python et Node ne sont pas utilisés directement sur la machine hôte pour ce projet.
Passe toujours par `docker compose`, lancé depuis la racine du dépôt :

- Démarrer : `docker compose up -d --build`
- État et logs : `docker compose ps`, `docker compose logs --tail=50 backend`
- Django : `docker compose exec backend python manage.py <commande>`
  (check, makemigrations, migrate, createsuperuser, `import_bpe --region 24`, spectacular)
- npm : `docker compose exec frontend npm <commande>`
- Une dépendance Python s'ajoute dans `backend/requirements.txt`,
  puis `docker compose build backend && docker compose up -d backend`.
- URLs : front http://localhost:5173, API http://localhost:8000/api/, Swagger http://localhost:8000/api/docs/

## Commandes autorisées, à confirmer, interdites

- Sans demander : `docker compose ps|logs|up|build|restart`, `docker compose exec backend|frontend …`,
  et Git en local (`status`, `diff`, `log`, `branch`, `switch`, `checkout -b`, `add`, `commit`, `fetch`, `pull`).
- Demande toujours avant : `git push`, `git merge`, `git rebase`, `docker compose down`,
  `docker compose exec db …` (accès direct à la base).
- Jamais : lire `.env` ou le contenu de `data/`, `git push --force`, `git reset --hard`,
  `docker compose down -v`, `docker volume rm`, `pip install` ou `npm install` sur l'hôte.

## Arborescence

```text
docker-compose.yaml  .env.example  README.md  AGENTS.md
data/                 parquet BPE (non versionné, ne pas le lire)
docs/                 plan-action.md, modele-donnees.md, api.md, utilisation.md, post-mortem.md, journal/
backend/              Dockerfile, requirements.txt, manage.py
  config/             settings.py, urls.py
  bpe/                référentiel en lecture seule (models, serializers, filters, views)
    management/commands/import_bpe.py
  prospection/        implantations + authentification
frontend/             vite.config.js, package.json
  src/                App.vue, api.js, map/loader.js, components/
```

## Règles métier

- `Point(lon, lat)` : la longitude d'abord. SRID 4326 partout.
- Noms de tables et colonnes = schéma du sujet (`db_table`, `db_column`), voir la section 4 du plan.
- Endpoint carte `/api/equipements/` : GeoJSON, filtre `in_bbox`, filtres multi-valeurs séparés par des
  virgules (`domaine1`, `domaine2`, `domaine3`, `ville`), pas de pagination, `select_related` + `only`.
- Implantations : `get_queryset` filtre sur `request.user`, `perform_create` fixe le propriétaire.
  Le client n'envoie jamais le propriétaire. Un utilisateur ne voit jamais les points d'un autre.
- Auth : `Authorization: Token <clé>` (pas Bearer).
- Secrets dans `.env`, jamais commité. Tenir `.env.example` à jour.

## Règles back-end (`backend/**/*.py`)

- Modèles géographiques : `from django.contrib.gis.db import models`, champs `PointField(srid=4326)`.
- Serializers carte : `GeoFeatureModelSerializer` avec `geo_field = "geom"` et peu de propriétés.
  Fiche détaillée : un serializer séparé avec les libellés des 3 niveaux de domaine.
- Vues : `ViewSet` DRF + router déclaré dans `config/urls.py` (propriétaire : rôle A).
- Filtres dans `filters.py` : `BaseInFilter` pour les listes, `InBBoxFilter` avec `bbox_filter_field = "geom"`.
- `@extend_schema` (drf-spectacular) sur les vues personnalisées pour documenter les paramètres dans Swagger.
- Configuration via `os.environ`. Pas de SQL brut sauf justification en commentaire.
- Après une modification de `models.py` : `makemigrations` puis `migrate`, et commite les migrations.
  Ne modifie jamais une migration déjà fusionnée dans `main`.

## Règles front-end (`frontend/src/**`)

- Composants en `<script setup>` (Composition API), JavaScript uniquement.
- La carte Leaflet se crée dans `onMounted` et se détruit dans `onUnmounted` (`map.remove()`).
- L'objet carte et les couches Leaflet ne vont jamais dans `ref()` / `reactive()` : variable simple ou `markRaw()`.
- Le chargement des équipements passe uniquement par `src/map/loader.js` (grille de tuiles z12 + cache).
  Ne jamais charger toute la région d'un coup.
- Marqueurs `L.circleMarker`, ajoutés en lot avec `cluster.addLayers(...)`.
- Conteneur de carte avec une hauteur CSS explicite, `leaflet/dist/leaflet.css` importé.
- Tous les appels HTTP passent par `src/api.js`, avec des URL relatives `/api/...` (proxy Vite).
- Pas de nouvelle dépendance npm sans accord du rôle B. CSS simple, pas de framework UI.

## Rôles et fichiers à propriétaire unique

Le développeur indique son rôle : dans `CLAUDE.local.md` avec Claude Code, ou en début de session
avec Codex ou Gemini (« Je suis le rôle B »). Si tu ne le connais pas, demande-le avant de modifier un fichier.
Ne modifie pas un fichier ci-dessous qui n'appartient pas à son rôle :
écris la modification proposée pour qu'il la transmette au propriétaire.

| Rôle | Fichiers dont il est seul propriétaire |
| --- | --- |
| A · Back et Docker | `docker-compose.yaml`, `backend/Dockerfile`, `backend/requirements.txt`, `backend/config/settings.py`, `backend/config/urls.py` |
| B · Front carte | `frontend/package.json`, `frontend/vite.config.js`, `frontend/src/components/MapView.vue`, `frontend/src/map/loader.js` |
| C · Données, auth, doc | `backend/bpe/management/commands/import_bpe.py`, `backend/prospection/`, `README.md`, `docs/`, `AGENTS.md` |

## Façon de travailler

- Une fonctionnalité à la fois. Vérifie qu'elle marche (commande, curl, navigateur) avant la suivante.
- Pour une tâche qui touche plus de 3 fichiers, propose d'abord un plan court et attends la validation.
- Code simple et lisible plutôt que générique. Commentaires et messages en français.
- Explique en 2 ou 3 phrases ce que fait le code produit : l'équipe doit pouvoir le présenter à l'oral.
- Git : branches `back/…`, `front/…`, `data/…`, `auth/…`. Commits au format
  `feat(api): …`, `fix(etl): …`, `docs: …`. Jamais de commit direct sur `main`.
- Si un problème résiste plus de 30 minutes, dis-le et propose le plan B (section 11 du plan).

## Procédures

Le développeur peut demander une procédure par son nom (« lance la procédure Vérification »).

### Vérification

Ne modifie aucun fichier. Lance ces contrôles dans l'ordre et continue même si l'un échoue :

1. `docker compose ps` : db, backend et frontend « running », db « healthy ».
2. `docker compose exec backend python manage.py check`
3. `docker compose exec backend python manage.py showmigrations --plan` : aucune migration non appliquée.
4. Nombre d'équipements, environ 97 095 attendus :
   `docker compose exec backend python manage.py shell -c "from bpe.models import Equipement; print(Equipement.objects.count())"`
5. API carte sur Tours (attendu : `FeatureCollection` et plus de 0 points) :
   `docker compose exec backend python -c "import urllib.request,json; d=json.load(urllib.request.urlopen('http://localhost:8000/api/equipements/?in_bbox=0.66,47.37,0.72,47.41')); print(d.get('type'), len(d.get('features', [])))"`
6. Sans token, `/api/implantations/` doit répondre 401 ou 403 :
   `docker compose exec backend python -c "import urllib.request as u, urllib.error as e
try: print(u.urlopen('http://localhost:8000/api/implantations/').status)
except e.HTTPError as x: print(x.code)"`
7. `docker compose exec frontend npm run build`

Termine par un tableau contrôle | OK/KO | détail, avec pour chaque KO la cause probable et la correction
(appuie-toi sur la section 11 de `docs/plan-action.md`).

### Journal

Pour préparer le post-mortem, ajoute à `docs/journal/role-<a|b|c>.md` (un fichier par rôle, crée-le si besoin) :

```markdown
## <HH:MM> – <titre court>
- Problème : …
- Cause : …
- Solution ou décision : …
- Temps perdu : … (estimation)
```

Reste factuel et court, ne modifie aucun autre fichier, ne commite pas.

### Prêt à fusionner

1. Si la branche courante est `main`, arrête-toi et propose de créer une branche.
2. Vérifie que le diff ne contient ni `.env`, ni fichier de `data/`, ni `node_modules/`, ni secret.
3. Signale toute modification d'un fichier à propriétaire unique qui n'est pas au rôle du développeur.
4. Si un `models.py` a changé, vérifie que les migrations sont dans le diff.
5. Lance `manage.py check` (back) et/ou `npm run build` (front) selon le diff.
6. `git fetch origin` puis `git pull origin main`. En cas de conflit, explique-le simplement et propose
   une résolution sans rien valider seul.
7. Propose un message de commit au bon format, commite après accord, puis demande avant
   `git push -u origin <branche>` et donne un titre et une description de pull request à copier.
