# Plan d'action – Projet Docker / Full Stack BPE (Groupe 1, Centre-Val de Loire)

Nov 27, 2026 · @Erwan

## 1. Analyse du sujet

**En une phrase :** une carte web des \~97 000 équipements BPE 2025 de la région Centre-Val de Loire (code région 24), filtrable par domaine et par ville, avec un espace privé où l'utilisateur connecté place ses implantations commerciales potentielles. Le tout tourne sous Docker et doit être livré en une journée par une équipe débutante. La stratégie est donc : **un MVP qui marche de bout en bout avant midi, puis les finitions.**

### Fonctionnalités attendues

| Bloc | Exigence | Priorité |
| --- | --- | --- |
| Carte publique | Afficher les équipements géolocalisés, naviguer, zoomer | MVP |
| Carte publique | Cliquer sur un équipement pour voir sa fiche | MVP |
| Chargement | Ne charger que ce qui est visible, puis seulement les éléments nouveaux au déplacement, en respectant les filtres | MVP (point noté) |
| Filtres | Par domaine, sur 3 niveaux (domaine1 > domaine2 > domaine3), choix multiple | MVP |
| Filtres | Par ville, choix multiple | MVP |
| Implantations | Connexion, puis ajouter, modifier, supprimer ses points (annotation, type BPE envisagé, commentaire), données privées | MVP |
| Import | Parquet filtré sur la région 24, puis normalisé en 6 tables relationnelles | MVP (prérequis à tout) |

### Contraintes imposées

- **Back obligatoire :** Python, Django, GeoDjango, Django REST Framework ou Django Ninja. Utiliser un autre back (Node, PHP…) coûte 5 points.
- **Base :** PostgreSQL + PostGIS, avec l'image Docker officielle `postgis/postgis`.
- **Docker :** une image Python construite par vous (Dockerfile) et le code **monté depuis l'hôte** via un volume (pas copié dans l'image).
- **Versions :** les dernières stables. Toute exception doit être justifiée dans le README (voir section 2).
- **Front :** React, Vue ou Angular, avec MapLibre GL JS ou Leaflet.

### Livrables

- Une application opérationnelle et reproductible en local.
- `Dockerfile` et `docker-compose.yaml`.
- Un dépôt GitHub partagé avec l'utilisateur **rcarlier**. Seule la branche `main` est évaluée.
- Le modèle de données, la documentation de l'API, et la documentation d'installation, d'import et d'utilisation.
- Un post-mortem et un oral de 10 minutes maximum à partir de 15h30.

### Pièges repérés

- **Le parquet est plat.** Les libellés des domaines sont répétés sur chaque ligne. Il faut en extraire les tables `domaine1/2/3` et les insérer **dans l'ordre des clés étrangères** (domaine1, puis domaine2, puis domaine3, puis bpe).
- **Le parquet ne contient pas les libellés des départements et de la région.** Pour la région 24 : 18 Cher, 28 Eure-et-Loir, 36 Indre, 37 Indre-et-Loire, 41 Loir-et-Cher, 45 Loiret. On les écrit en dur dans le script d'import.
- **Le chargement incrémental est la partie « intelligente » du sujet.** Une simple requête par bbox à chaque déplacement ne suffit pas : elle rechargerait des points déjà affichés.
- **97 000 marqueurs d'un coup font planter Leaflet.** Il faut un zoom minimum et du clustering.

## 2. Stack recommandée

**Recommandation : Vue 3 + Leaflet côté front, Django REST Framework + djangorestframework-gis côté back.** Pour une équipe débutante sur une journée, c'est la combinaison qui donne le plus de fonctionnalités « gratuites » avec le moins de code à écrire. Les versions ont été vérifiées le 27/11/2026.

| Composant | Choix | Version | Pourquoi ce choix |
| --- | --- | --- | --- |
| Framework front | **Vue 3 + Vite** (JavaScript, sans TypeScript) | dernière, via `npm create vue@latest` | Les templates ressemblent à du HTML, la réactivité (`ref`) est simple, il y a peu de code répétitif. Angular est trop lourd pour une journée (TypeScript, RxJS). Avec React, le StrictMode monte les composants deux fois en dev, ce qui casse souvent l'initialisation d'une carte Leaflet. |
| Carte | **Leaflet** + **Leaflet.markercluster** | 1.9.4 (dernière stable) | L'API est la plus simple, les tuiles OpenStreetMap s'ajoutent en une ligne et les tutoriels sont nombreux. Leaflet 2.0 est encore en bêta ([bêta 4 du 12/11/2026](https://leafletjs.com/)) : on reste donc sur 1.9.4. MapLibre est plus performant mais demande de configurer un style JSON. |
| API | **Django REST Framework** | 3.18 (ajoute le support de Django 6.1) | `ModelViewSet` donne un CRUD complet en une dizaine de lignes, et l'API navigable aide à déboguer. |
| Géo API | **djangorestframework-gis** | [1.3.0 (01/09/2026)](https://pypi.org/project/djangorestframework-gis) | Fournit `GeoFeatureModelSerializer`, qui sort du GeoJSON directement lisible par Leaflet, et `InBBoxFilter`, qui gère le filtre par bbox sans rien coder. C'est l'argument décisif face à Django Ninja. |
| Doc API | **drf-spectacular** (Swagger / OpenAPI) | dernière | Le livrable « Documentation des API » est généré automatiquement sur `/api/docs/`. |
| Filtres | **django-filter** | dernière | Filtres `?domaine3=...&ville=...` déclaratifs. |
| Framework back | **Django + GeoDjango** | [6.1.x](https://www.djangoproject.com/download/) (6.1.3) | Dernière version stable, sortie le 05/08/2026. |
| Python | **3.13** (`python:3.13-slim`) | 3.13 | Django 6.1 supporte Python 3.12 à 3.14, mais djangorestframework-gis 1.3 n'est officiellement testé que jusqu'à 3.13. C'est donc la plus récente version supportée par **toutes** nos dépendances. Justifiez-le dans le README. |
| Driver PostgreSQL | **psycopg 3** (`psycopg[binary]`) | dernière | La version binaire évite de compiler `libpq`. |
| ETL | **pandas + pyarrow** | dernières | `pyarrow` lit le parquet en ne gardant que la région 24 dès la lecture, ce qui économise la mémoire. |
| Base | **PostgreSQL 18 + PostGIS 3.6**, image `postgis/postgis:18-3.6` | 18 / 3.6.4 | C'est la version [recommandée par l'image officielle](https://github.com/postgis/docker-postgis). PostgreSQL 19 n'y est disponible qu'en bêta. |
| Conteneur front | `node:lts-slim` | LTS | Node ne sert qu'à faire tourner Vite : ce n'est pas un back, donc pas de malus. |
| Authentification | **TokenAuthentication** de DRF + proxy Vite | inclus | Pas de CSRF ni de CORS à gérer : Vite redirige `/api` vers Django, donc tout est sur la même origine. |

**Ce qu'on évite volontairement :** TypeScript, Pinia, un state manager, une librairie UI lourde, JWT, Nginx et les tuiles vectorielles. Chacun de ces outils coûte du temps de prise en main pour un gain nul à l'oral. Si vous voulez un minimum de style, un CSS simple ou [Pico CSS](https://picocss.com/) (une seule balise `<link>`) suffit.

## 3. Architecture et arborescence

**Trois conteneurs, et le code reste sur votre machine.** Le navigateur ne parle qu'au serveur Vite, qui relaie `/api` vers Django. Seul Django accède à PostGIS.

&#91;embedded content: architecture Docker · 3 conteneurs, 3 volumes\]

Les flèches pleines représentent les requêtes, les flèches en pointillés les dossiers montés en volume. Modifier un fichier sur l'hôte recharge immédiatement Django ou Vite, sans reconstruire d'image.

```text
terriscope/
├── docker-compose.yaml
├── .env.example          # copié en .env (non versionné)
├── .gitignore  .gitattributes
├── README.md             # installation, import, utilisation
├── data/                 # bpe25.parquet (non versionné)
├── docs/
│   ├── modele-donnees.md # diagramme Mermaid erDiagram
│   ├── api.md  openapi.yaml
│   ├── utilisation.md
│   └── post-mortem.md
├── backend/
│   ├── Dockerfile  requirements.txt  manage.py
│   ├── config/           # settings.py, urls.py
│   ├── bpe/              # référentiel : models, serializers, filters, views
│   │   └── management/commands/import_bpe.py
│   └── prospection/      # implantations + authentification
└── frontend/
    ├── vite.config.js  package.json
    └── src/
        ├── App.vue  api.js
        ├── map/loader.js
        └── components/   # MapView, FiltresPanel, FicheEquipement, ImplantationForm
```

## 4. Modèle de données

**Le modèle comporte deux applications Django.** `bpe` contient le référentiel en lecture seule, soit les 6 tables du schéma du sujet. `prospection` contient les implantations des utilisateurs, stockées à part comme le demande l'énoncé. Les noms de tables et de colonnes (`db_table`, `db_column`) reprennent ceux du schéma du sujet pour que le correcteur s'y retrouve.

```python
# backend/bpe/models.py
from django.contrib.gis.db import models

class Region(models.Model):
    id_region = models.CharField(max_length=3, primary_key=True)
    libelle = models.CharField(max_length=255)
    class Meta:
        db_table = "regions"

class Departement(models.Model):
    id_dept = models.CharField(max_length=3, primary_key=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, db_column="id_region")
    libelle = models.CharField(max_length=255)
    class Meta:
        db_table = "depts"

class Domaine1(models.Model):
    code = models.CharField(max_length=1, primary_key=True)
    libelle = models.CharField(max_length=255)
    class Meta:
        db_table = "domaine1"

class Domaine2(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    domaine1 = models.ForeignKey(Domaine1, on_delete=models.PROTECT,
                                 db_column="domaine1_code", related_name="enfants")
    libelle = models.CharField(max_length=255)
    class Meta:
        db_table = "domaine2"

class Domaine3(models.Model):
    code = models.CharField(max_length=4, primary_key=True)
    domaine2 = models.ForeignKey(Domaine2, on_delete=models.PROTECT,
                                 db_column="domaine2_code", related_name="enfants")
    libelle = models.CharField(max_length=255)
    class Meta:
        db_table = "domaine3"

class Equipement(models.Model):
    id = models.UUIDField(primary_key=True)            # colonne _id du parquet
    domaine3 = models.ForeignKey(Domaine3, on_delete=models.PROTECT, db_column="domaine3_code")
    departement = models.ForeignKey(Departement, on_delete=models.PROTECT, db_column="id_dept")
    nom = models.CharField(max_length=255, blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    codepostal = models.CharField(max_length=5, blank=True)
    ville = models.CharField(max_length=255, db_index=True)
    siret = models.CharField(max_length=14, blank=True)
    geom = models.PointField(srid=4326)                # index spatial GiST créé automatiquement
    class Meta:
        db_table = "bpe"
```

```python
# backend/prospection/models.py
from django.conf import settings
from django.contrib.gis.db import models

class Implantation(models.Model):
    proprietaire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                     related_name="implantations")
    titre = models.CharField(max_length=255)
    domaine3 = models.ForeignKey("bpe.Domaine3", on_delete=models.SET_NULL,
                                 null=True, blank=True)   # type de commerce envisagé
    commentaire = models.TextField(blank=True)
    geom = models.PointField(srid=4326)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
```

**Choix à justifier à l'oral :**

- Le schéma du sujet montre à la fois `id_dept` et `dept` dans `bpe`. On les fusionne en **une seule clé étrangère** (`id_dept` vers `depts`) pour éviter la redondance.
- La seule liaison entre `Implantation` et le référentiel est la classification `Domaine3` (type de commerce envisagé). Elle n'a aucun lien avec les équipements, ce qui respecte la consigne « stockées indépendamment ».
- Les index utiles sont tous créés automatiquement : GiST sur `geom`, B-tree sur les clés étrangères, plus `db_index` sur `ville`.
- **Livrable :** un diagramme `erDiagram` en Mermaid dans `docs/modele-donnees.md`, que GitHub affiche nativement.

## 5. ETL : import du parquet BPE

**L'import est une commande Django rejouable, `python manage.py import_bpe --region 24`.** Elle doit produire environ **97 095 lignes** dans `bpe`, le chiffre de l'annexe du sujet, et sert de test de validation. Elle s'exécute en moins d'une minute.

1. **Télécharger** [bpe25.parquet.zip](https://data.atontour.info/bpe25.parquet.zip) et le dézipper dans `./data/`. Ce dossier est monté sur `/data` dans le conteneur et ignoré par Git (`data/*.parquet` dans `.gitignore`).
2. **Inspecter avant de coder (10 min, à ne pas sauter).** Dans `docker compose exec backend python`, lancez `import pyarrow.parquet as pq; print(pq.read_schema("/data/bpe25.parquet"))`. Vérifiez le nom exact des colonnes et surtout le **type de `region`** (chaîne `"24"` ou entier `24`), car le filtre en dépend.
3. **Extraire.** Lisez la classification complète des domaines, toutes régions confondues, pour que le choix du « type de commerce envisagé » couvre toute la classification. Lisez ensuite les équipements filtrés **dès la lecture** grâce à `filters=`.
4. **Nettoyer.** Supprimez les lignes sans `lon`/`lat`, remplacez les valeurs vides par `""`, forcez `codepostal` et `siret` en texte, et renommez `_id` et `SIRET` (pandas renomme les colonnes qui commencent par `_` dans `itertuples`).
5. **Charger dans l'ordre des clés étrangères :** regions, depts, domaine1, domaine2, domaine3, puis bpe, avec `bulk_create(batch_size=5000)`.

```python
# backend/bpe/management/commands/import_bpe.py
import pyarrow.parquet as pq
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction
from bpe.models import Region, Departement, Domaine1, Domaine2, Domaine3, Equipement

REGIONS = {"24": "Centre-Val de Loire"}
DEPTS = {"18": "Cher", "28": "Eure-et-Loir", "36": "Indre",
         "37": "Indre-et-Loire", "41": "Loir-et-Cher", "45": "Loiret"}
DOM_COLS = ["domaine1_code", "domaine1_libelle", "domaine2_code",
            "domaine2_libelle", "domaine3_code", "domaine3_libelle"]

class Command(BaseCommand):
    help = "Importe les équipements BPE 2025 d'une région"

    def add_arguments(self, parser):
        parser.add_argument("--file", default="/data/bpe25.parquet")
        parser.add_argument("--region", default="24")  # adapter le type après l'étape 2

    @transaction.atomic
    def handle(self, *args, file, region, **kw):
        # 1. Extraction
        dom = pq.read_table(file, columns=DOM_COLS).to_pandas().drop_duplicates()
        df = pq.read_table(file, filters=[("region", "=", region)]).to_pandas()

        # 2. Nettoyage
        df = df.dropna(subset=["lon", "lat"]).fillna("")
        df = df.rename(columns={"_id": "uuid", "SIRET": "siret"})

        # 3. Chargement (référentiels idempotents, équipements purgés puis rechargés)
        Region.objects.bulk_create([Region(id_region=k, libelle=v) for k, v in REGIONS.items()],
                                   ignore_conflicts=True)
        Departement.objects.bulk_create([Departement(id_dept=k, libelle=v, region_id="24")
                                         for k, v in DEPTS.items()], ignore_conflicts=True)
        d1 = dom.drop_duplicates("domaine1_code")
        Domaine1.objects.bulk_create([Domaine1(code=r.domaine1_code, libelle=r.domaine1_libelle)
                                      for r in d1.itertuples()], ignore_conflicts=True)
        # ... même logique pour Domaine2 (domaine1_id=...) puis Domaine3 (domaine2_id=...)

        Equipement.objects.all().delete()
        Equipement.objects.bulk_create(
            (Equipement(id=r.uuid, nom=r.nom, adresse=r.adresse,
                        codepostal=str(r.codepostal)[:5], ville=r.ville,
                        siret=str(r.siret)[:14], departement_id=str(r.dept),
                        domaine3_id=r.domaine3_code,
                        geom=Point(float(r.lon), float(r.lat), srid=4326))
             for r in df.itertuples()),
            batch_size=5000,
        )
        self.stdout.write(self.style.SUCCESS(f"{Equipement.objects.count()} équipements importés"))
```

**Pourquoi ce n'est pas un simple `DROP` et réimport :** si on supprimait les domaines, le `SET_NULL` effacerait le type envisagé de toutes les implantations des utilisateurs. Les référentiels sont donc insérés avec `ignore_conflicts`, et seuls les équipements sont purgés.

**Attention à l'ordre de `Point(lon, lat)` :** c'est la longitude d'abord. Si vos points apparaissent en Somalie, c'est que l'ordre est inversé.

## 6. API REST

**Huit endpoints suffisent.** Toute la documentation est générée par drf-spectacular sur `/api/docs/` (Swagger) et `/api/schema/` (fichier OpenAPI à joindre au dépôt).

| Méthode et URL | Rôle | Accès | Outil DRF |
| --- | --- | --- | --- |
| `GET /api/equipements/?in_bbox=minLon,minLat,maxLon,maxLat&domaine1=&domaine2=&domaine3=&ville=` | Points d'une zone, au format GeoJSON, avec des propriétés légères (`id`, `nom`, `domaine3`) | Public | `ReadOnlyModelViewSet` + `GeoFeatureModelSerializer` + `InBBoxFilter` + django-filter |
| `GET /api/equipements/{id}/` | Fiche complète : adresse, SIRET, libellés des 3 niveaux de domaine | Public | même ViewSet, avec un serializer de détail |
| `GET /api/domaines/` | Arbre domaine1 > domaine2 > domaine3 pour le filtre | Public | `ListAPIView` + serializers imbriqués + `prefetch_related` |
| `GET /api/villes/?search=tou` | Autocomplétion des villes, sur les valeurs distinctes de `bpe.ville` | Public | `APIView` + `values_list("ville", flat=True).distinct()` |
| `POST /api/auth/token/` | Login : renvoie un token | Public | `obtain_auth_token` (fourni par DRF) |
| `POST /api/auth/register/` | Inscription (optionnel, sinon on crée les comptes avec `createsuperuser`) | Public | `CreateAPIView` |
| `GET /api/auth/me/` | Utilisateur connecté | Token | `APIView` |
| `GET` `POST` `PUT` `PATCH` `DELETE /api/implantations/` | CRUD des implantations de l'utilisateur connecté uniquement | Token | `ModelViewSet` + `GeoFeatureModelSerializer` |

**Les filtres multi-valeurs s'écrivent avec une virgule :** `?domaine3=F307,F303&ville=Tours,Orléans`. Avec django-filter, on utilise `BaseInFilter` (`CharInFilter(field_name="ville", lookup_expr="in")`). Les filtres sur domaine1 et domaine2 passent par les relations : `domaine3__domaine2__domaine1__in`.

**L'isolation des données privées tient en trois lignes**, et c'est un point de sécurité que le correcteur testera :

```python
class ImplantationViewSet(viewsets.ModelViewSet):
    serializer_class = ImplantationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):                      # l'utilisateur ne voit QUE ses points
        return Implantation.objects.filter(proprietaire=self.request.user)

    def perform_create(self, serializer):        # le propriétaire n'est jamais envoyé par le client
        serializer.save(proprietaire=self.request.user)
```

**Performance du endpoint carte :**

- `select_related("domaine3")` et `.only("id", "nom", "geom", "domaine3_id")` pour ne charger que l'essentiel.
- Pas de pagination sur ce endpoint (`pagination_class = None`), car le front découpe déjà les requêtes en petites zones.
- Un garde-fou côté serveur : la bbox est refusée (erreur 400) si elle dépasse environ 1° × 1°.

## 7. Front Vue + Leaflet

**Le chargement optimisé repose sur une grille fixe de tuiles.** On découpe la carte en carrés de taille fixe : ce sont les tuiles « slippy map » du niveau de zoom 12, d'environ 10 km de côté en France. À chaque déplacement, le front calcule les tuiles visibles et ne demande que celles qu'il n'a pas encore chargées pour les filtres actifs. Changer un filtre vide le cache et recharge la vue. C'est exactement ce que demande le sujet : on ne charge que ce qui est visible, et seulement ce qui manque. C'est aussi simple à expliquer à l'oral.

```js
// frontend/src/map/loader.js
import L from 'leaflet'
const Z = 12          // grille fixe (~10 km)
const MIN_ZOOM = 11   // en dessous : message « Zoomez pour voir les équipements »

const tileBbox = (x, y, z) => {
  const n = 2 ** z, lon = v => v / n * 360 - 180
  const lat = v => Math.atan(Math.sinh(Math.PI * (1 - 2 * v / n))) * 180 / Math.PI
  return [lon(x), lat(y + 1), lon(x + 1), lat(y)]   // minLon,minLat,maxLon,maxLat
}

export function createLoader(map, cluster, getQueryString, onSelect) {
  const loadedTiles = new Set(), seenIds = new Set()
  let generation = 0                                // ignore les réponses d'anciens filtres

  async function load() {
    if (map.getZoom() < MIN_ZOOM) return
    const gen = generation, qs = getQueryString(), b = map.getBounds()
    const a = map.project(b.getNorthWest(), Z).divideBy(256).floor()
    const c = map.project(b.getSouthEast(), Z).divideBy(256).floor()
    const jobs = []
    for (let x = a.x; x <= c.x; x++) for (let y = a.y; y <= c.y; y++) {
      const key = `${x}/${y}`
      if (loadedTiles.has(key)) continue             // déjà chargée : rien à faire
      loadedTiles.add(key)
      jobs.push(fetch(`/api/equipements/?in_bbox=${tileBbox(x, y, Z)}&${qs}`)
        .then(r => r.json()).catch(() => { loadedTiles.delete(key); return { features: [] } }))
    }
    const results = await Promise.all(jobs)
    if (gen !== generation) return
    const markers = results.flatMap(fc => fc.features)
      .filter(f => !seenIds.has(f.id) && seenIds.add(f.id))
      .map(f => L.circleMarker([f.geometry.coordinates[1], f.geometry.coordinates[0]], { radius: 6 })
                 .on('click', () => onSelect(f.id)))
    cluster.addLayers(markers)                       // ajout en lot : beaucoup plus rapide
  }

  function reset() { generation++; loadedTiles.clear(); seenIds.clear(); cluster.clearLayers(); load() }
  map.on('moveend', load)
  return { load, reset }
}
```

**Composants Vue (5 composants et un module API, pas plus) :**

| Fichier | Rôle |
| --- | --- |
| `App.vue` | Mise en page : panneau latéral, carte, barre de connexion |
| `MapView.vue` | Crée la carte dans `onMounted`, avec les tuiles OSM, le groupe de clusters, le loader et une couche « Mes implantations » d'une autre couleur |
| `FiltresPanel.vue` | Arbre à 3 niveaux de cases à cocher (cocher un parent coche ses enfants), et des villes en autocomplétion (`<input list>` + `<datalist>`) affichées en étiquettes |
| `FicheEquipement.vue` | Affiche le détail renvoyé par `GET /api/equipements/{id}/` dans le panneau latéral |
| `ImplantationForm.vue` | Mode « Ajouter » : on clique sur la carte, puis on remplit le titre, le type (liste des domaine3) et le commentaire. Cliquer sur l'un de ses points permet de le modifier ou de le supprimer. |
| `api.js` | Petite surcouche de `fetch` qui ajoute `Authorization: Token …` (le token est stocké dans `localStorage`) |

**Pièges Leaflet classiques (qui coûtent une heure chacun si on ne les connaît pas) :**

- **Carte grise ou invisible :** le conteneur doit avoir une hauteur CSS explicite (`height: 100vh`), et il faut `import 'leaflet/dist/leaflet.css'`.
- **Icônes de marqueur cassées avec Vite :** utilisez `L.circleMarker` plutôt que `L.marker`, ce qui évite le problème.
- **Ne pas rendre l'objet carte réactif :** stockez-le dans une simple variable, ou avec `markRaw(map)`, jamais dans un `ref()`, car le proxy de Vue casse Leaflet.
- **Envoyer les filtres au niveau le plus haut coché** (`domaine1=F` plutôt que la liste de tous ses codes domaine3), sinon l'URL devient très longue.

## 8. Docker

**Trois services, un seul `docker compose up --build`.** `db` utilise l'image postgis officielle. `backend` utilise votre image Python, construite avec un Dockerfile, et le code est monté en volume. `frontend` utilise l'image `node` avec le code également monté. C'est le premier chantier de la matinée, car toute l'équipe en dépend.

```dockerfile
# backend/Dockerfile
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# Bibliothèques système requises par GeoDjango (GDAL, GEOS, PROJ)
RUN apt-get update && apt-get install -y --no-install-recommends \
        binutils libproj-dev gdal-bin \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Le code n'est PAS copié : il est monté par volume (exigence du sujet)
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

```text
# backend/requirements.txt
Django~=6.1
djangorestframework~=3.18
djangorestframework-gis~=1.3
drf-spectacular
django-filter
psycopg[binary]
pandas
pyarrow
```

```yaml
# docker-compose.yaml
services:
  db:
    image: postgis/postgis:18-3.6
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql        # chemin modifié à partir de PostgreSQL 18
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      retries: 10

  backend:
    build: ./backend
    env_file: .env
    volumes:
      - ./backend:/app                     # code en dehors du conteneur
      - ./data:/data                       # parquet
    ports: ["8000:8000"]
    depends_on:
      db:
        condition: service_healthy
    command: sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"

  frontend:
    image: node:lts-slim
    working_dir: /app
    volumes:
      - ./frontend:/app
      - /app/node_modules                  # garde les modules Linux dans le conteneur
    ports: ["5173:5173"]
    command: sh -c "npm install && npm run dev -- --host 0.0.0.0"
    depends_on: [backend]

volumes:
  pgdata:
```

```js
// frontend/vite.config.js (extrait) : le proxy supprime CORS et CSRF
server: {
  proxy: { '/api': { target: 'http://backend:8000', changeOrigin: true } },
  watch: { usePolling: true },   // indispensable sous Windows et macOS avec des volumes
}
```

**Réglages Django à ne pas oublier :**

- `ENGINE: "django.contrib.gis.db.backends.postgis"` et `HOST: "db"`, avec les valeurs lues depuis l'environnement (`os.environ`).
- `"django.contrib.gis"`, `"rest_framework"`, `"rest_framework_gis"`, `"rest_framework.authtoken"`, `"django_filters"` et `"drf_spectacular"` dans `INSTALLED_APPS`.
- `ALLOWED_HOSTS` doit contenir `backend` et `localhost`, sinon le proxy Vite reçoit une erreur 400.
- On versionne `.env.example`, et on ajoute `.env` au `.gitignore`.

**Pièges Docker pour débutants :**

- **Port 5432 déjà pris** par un PostgreSQL installé en local : n'exposez pas le port de `db`, ce n'est pas nécessaire. Si vous voulez y accéder avec DBeaver ou pgAdmin, utilisez `"5433:5432"`.
- **Fins de ligne CRLF sous Windows** dans les scripts `.sh` : ajoutez `* text=auto eol=lf` dans `.gitattributes` dès le premier commit.
- **Mac Apple Silicon :** si `postgis/postgis` refuse de se lancer, ajoutez `platform: linux/amd64` au service `db` (émulation, plus lent mais fonctionnel). À tester dès 9h30.
- **Repartir de zéro :** `docker compose down -v` supprime aussi le volume de la base, et il faudra relancer l'import.
- **Lancer une commande Django :** `docker compose exec backend python manage.py <commande>`. Mettez ces commandes dans le README.

## 9. Planning de la journée et répartition des rôles

**Trois rôles qui travaillent en parallèle dès 9h30, avec deux jalons non négociables : le MVP de bout en bout à 12h00 et le gel des fonctionnalités à 14h30.** Les horaires supposent un démarrage à 9h00 : décalez tout le planning si vous commencez plus tard.

&#91;embedded content: planning de la journée · 3 rôles, 2 jalons\]

Le front (B) avance sur des données factices jusqu'à ce que l'API (A) et l'import (C) soient prêts vers 11h00. Personne n'attend personne.

| Rôle | Responsable de | Fichiers dont il est seul propriétaire |
| --- | --- | --- |
| **A · Back et Docker** | Docker, settings, modèles, API carte, doc Swagger, performance | `docker-compose.yaml`, `Dockerfile`, `settings.py`, `urls.py` |
| **B · Front carte** | Vue, Leaflet, chargement par tuiles, filtres, fiche équipement, démo à l'oral | `package.json`, `vite.config.js`, `MapView.vue`, `loader.js` |
| **C · Données, auth, doc** | ETL, authentification, API et formulaire des implantations, README, post-mortem | `import_bpe.py`, `prospection/`, `README.md`, `docs/` |

**Synchronisations rapides de 5 minutes, debout :** à 10h30, 12h00, 14h00 et 14h30. Chacun dit ce qui marche, ce qui bloque et s'il a besoin de quelqu'un. Un blocage de plus de 30 minutes déclenche le plan B (section 11).

## 10. Workflow Git

**Une branche courte par personne et par tâche, fusionnée dans `main` au moins toutes les 1h30.** Seule `main` est notée, et attendre 14h pour fusionner garantit des conflits ingérables.

1. **9h00 :** la personne A crée le dépôt et ajoute immédiatement **rcarlier** comme collaborateur. Elle pousse le squelette (arborescence, `.gitignore`, `.gitattributes`, `.env.example`, `README.md` vide), puis les deux autres clonent.
2. **Nommage des branches :** `back/docker`, `back/api-carte`, `data/etl`, `front/carte`, `front/filtres`, `auth/implantations`.
3. **Cycle :** `git pull origin main`, travail, commits fréquents, `git pull origin main` encore, résolution des conflits en local, push, puis pull request sur GitHub fusionnée par l'auteur. Pas besoin de relecture formelle : un coup d'œil du voisin suffit.
4. **Fichiers à risque de conflit :** `settings.py`, `urls.py`, `package.json` et `docker-compose.yaml` n'ont **qu'un seul responsable** (la personne A pour le back, la personne B pour le front). Les autres lui demandent les modifications.
5. **À ne jamais committer :** `.env`, `data/*.parquet`, `node_modules/`, `__pycache__/`.
6. **Messages de commit lisibles** pour le post-mortem, sur le modèle `feat(api): filtre bbox sur les équipements` ou `fix(etl): ordre lon/lat`.

```gitignore
.env
data/*.parquet
data/*.zip
node_modules/
__pycache__/
*.pyc
frontend/dist/
```

## 11. Risques et plans B

**La règle de la journée : si un problème bloque plus de 30 minutes, on passe au plan B et on le note pour le post-mortem.** À l'oral, une fonctionnalité simplifiée qui marche vaut mieux qu'une fonctionnalité ambitieuse qui plante.

| Risque | Signe d'alerte | Plan B |
| --- | --- | --- |
| Docker ne démarre pas sur un poste | Pas de `docker compose up` fonctionnel à 10h00 | Ce membre travaille en binôme sur le poste d'un autre. On ne débogue pas Docker Desktop pendant 2 heures. |
| GeoDjango ne trouve pas GDAL | `ImproperlyConfigured: Could not find the GDAL library` | Vérifier que `gdal-bin` est dans le Dockerfile, puis `docker compose build --no-cache backend`. |
| Le filtre région de l'ETL ne renvoie rien | `0 équipements importés` | Le type de `region` est faux (`"24"` au lieu de `24`) : relire `read_schema`. En dernier recours, filtrer après lecture avec pandas : `df[df.region.astype(str) == "24"]`. |
| Le chargement par tuiles n'est pas prêt à 12h00 | Pas de points sur la carte | Version simple : une requête bbox à chaque `moveend` avec un zoom minimum. On améliore avec les tuiles l'après-midi. |
| L'arbre de filtres à 3 niveaux prend trop de temps | Toujours en cours à 13h45 | Trois `<select multiple>` en cascade (domaine1, puis domaine2, puis domaine3) : c'est fonctionnellement équivalent. |
| L'authentification bloque | Erreurs 401 ou 403 en boucle | Vérifier le header `Authorization: Token <clé>` (le mot `Token`, pas `Bearer`) et la présence de `rest_framework.authtoken` dans `INSTALLED_APPS` avec `migrate` relancé. |
| Conflits Git à 14h30 | Fusion impossible | Fusionner toutes les 1h30, et un seul responsable par fichier partagé (section 10). |
| Démo qui plante pendant l'oral | Wi-Fi, conteneur arrêté | Enregistrer une **vidéo de 2 minutes** de la démo à 15h00. Lancer `docker compose up` à 15h20, pas pendant l'oral. |

**À couper en premier si vous êtes en retard** (dans cet ordre) : l'inscription (on crée les comptes en ligne de commande), le style, l'autocomplétion des villes (remplacée par une liste déroulante), puis le dédoublonnage par `seenIds`.

**Ce qu'on ne coupe jamais :** le chargement limité à la zone visible, l'isolation des implantations par utilisateur, le README d'installation et la branche `main` à jour.

## 12. Livrables, post-mortem et oral

**Le test final se fait à 14h45 :** un membre clone `main` dans un dossier vierge, suit le README **mot à mot**, et doit voir la carte fonctionner. Tout ce qui manque dans le README apparaît à ce moment-là.

### Checklist des livrables

- [ ] Dépôt GitHub partagé avec **rcarlier** (à faire dès 9h00)
- [ ] `backend/Dockerfile` et `docker-compose.yaml` à la racine
- [ ] Application fonctionnelle après `git clone` + `docker compose up --build` + import
- [ ] `README.md` : prérequis, installation, téléchargement du parquet, commande d'import, création d'un compte, URL de l'application et de la doc API, justification des versions
- [ ] `docs/modele-donnees.md` : diagramme Mermaid `erDiagram` et explication des choix
- [ ] `docs/api.md` : lien vers `/api/docs/`, exemples de requêtes `curl` pour la bbox et les filtres, et `docs/openapi.yaml` exporté avec `python manage.py spectacular --file docs/openapi.yaml`
- [ ] `docs/utilisation.md` : guide utilisateur en 5 étapes avec captures d'écran
- [ ] `docs/post-mortem.md`
- [ ] Branche `main` à jour avant 15h00, sans `.env` ni parquet committé

### Modèle de post-mortem (à remplir de 14h45 à 15h15)

```markdown
# Post-mortem – Groupe 1
## Objectif et résultat : ce qui est livré / ce qui ne l'est pas
## Ce qui a bien marché (3 points)
## Ce qui a mal marché : problème → cause → temps perdu → solution
## Décisions techniques et leurs alternatives (Vue vs React, DRF vs Ninja, tuiles vs bbox...)
## Ce qu'on ferait différemment
## Pistes d'amélioration (tuiles vectorielles MVT, cache HTTP, tests, déploiement)
```

**Astuce :** chacun note ses blocages au fil de l'eau dans un fichier partagé (heure, problème, solution). Le post-mortem s'écrit alors en 20 minutes.

### Déroulé de l'oral (10 minutes maximum, les 3 membres parlent)

| Durée | Contenu | Qui |
| --- | --- | --- |
| 1 min | Le besoin, la région Centre-Val de Loire, \~97 000 équipements | A |
| 1 min 30 | Architecture Docker et choix de stack, avec le schéma de la section 3 | A |
| 1 min 30 | ETL : du parquet plat aux 6 tables, avec le schéma de la base | C |
| 3 min | **Démo en direct :** zoom, filtres, puis l'onglet Réseau qui montre que seules les nouvelles tuiles sont chargées, puis login, ajout et modification d'une implantation, puis un second compte qui ne la voit pas | B |
| 1 min 30 | Le chargement optimisé expliqué (grille de tuiles + cache), et la doc API Swagger | B |
| 1 min 30 | Post-mortem : 2 succès, 2 difficultés, ce qu'on améliorerait | C |

**Montrer l'onglet Réseau du navigateur pendant la démo** est la preuve la plus convaincante que la contrainte de chargement est respectée : on y voit qu'aucune requête n'est envoyée quand on revient sur une zone déjà vue.
