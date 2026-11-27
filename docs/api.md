# API REST – TerriScope

- **Base** : `http://localhost:8000/api/` (depuis le front : URL relatives `/api/...`, relayées par le proxy Vite)
- **Documentation interactive** : Swagger sur http://localhost:8000/api/docs/ (bouton « Try it out »)
- **Schéma OpenAPI** : http://localhost:8000/api/schema/, copie versionnée dans `docs/openapi.yaml`
- **Format** : JSON ; GeoJSON pour les points (`FeatureCollection` / `Feature`), coordonnées `[longitude, latitude]` en WGS 84
- **Compression** : réponses compressées en gzip si le client l'accepte

## Vue d'ensemble

| Méthode et URL | Rôle | Accès |
| --- | --- | --- |
| `GET /api/equipements/?in_bbox=…` | Équipements d'une zone (GeoJSON léger) | Public |
| `GET /api/equipements/{id}/` | Fiche complète d'un équipement | Public |
| `GET /api/domaines/` | Arbre domaine1 > domaine2 > domaine3 | Public |
| `GET /api/villes/?search=…` | Autocomplétion des villes | Public |
| `POST /api/auth/register/` | Inscription, renvoie un token | Public |
| `POST /api/auth/token/` | Connexion, renvoie un token | Public |
| `GET /api/auth/me/` | Utilisateur connecté | Token |
| `GET` `POST /api/implantations/` | Liste et création de ses implantations | Token |
| `GET` `PUT` `PATCH` `DELETE /api/implantations/{id}/` | Lecture, modification, suppression d'une de ses implantations | Token |

## Authentification

Les routes privées attendent le header **`Authorization: Token <clé>`** (le mot `Token`, pas `Bearer`).
Sans token ou avec un token invalide : `401`.

### `POST /api/auth/register/`

```json
{ "username": "alice", "password": "MotDePasse-Solide-42" }
```

`201` → `{ "token": "<clé de 40 caractères>" }`

`400` si le nom est déjà pris ou si le mot de passe est refusé par les validateurs Django
(8 caractères minimum, pas trop courant, pas entièrement numérique, pas trop proche du nom) :

```json
{ "password": ["Ce mot de passe est trop court. Il doit contenir au minimum 8 caractères."] }
```

### `POST /api/auth/token/`

Même corps que l'inscription. `200` → `{ "token": "…" }` ; `400` si les identifiants sont faux.

### `GET /api/auth/me/`

`200` → `{ "id": 4, "username": "alice" }`

## Équipements (public)

### `GET /api/equipements/`

Points d'une zone, pour la carte. **Pas de pagination** : le front découpe déjà la carte en tuiles.

| Paramètre | Obligatoire | Description | Exemple |
| --- | --- | --- | --- |
| `in_bbox` | **oui** | Zone `minLon,minLat,maxLon,maxLat`, **1° × 1° maximum** | `0.66,47.37,0.72,47.41` |
| `domaine1` | non | Codes domaine1, séparés par des virgules | `F,A` |
| `domaine2` | non | Codes domaine2 | `F3` |
| `domaine3` | non | Codes domaine3 | `F307,F303` |
| `ville` | non | Villes, séparées par des virgules (nom exact) | `Tours,Joué-lès-Tours` |

Une liste de valeurs dans un même paramètre est un **OU** (`ville=Tours,Blois` : Tours ou Blois) ;
plusieurs paramètres se combinent en **ET** (`domaine1=F&ville=Tours` : sport-loisirs-culture **à** Tours).

Exemple : `GET /api/equipements/?in_bbox=0.66,47.37,0.72,47.41&domaine1=F`

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "id": "ff8975a4-cc10-4350-9c29-d98b46361f6d",
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [0.66045, 47.38121] },
      "properties": { "nom": "Carre d O", "domaine3": "F101" }
    }
  ]
}
```

Erreurs `400` :

- `in_bbox` absent : `{"detail": "Le paramètre in_bbox est obligatoire (minLon,minLat,maxLon,maxLat)."}`
- zone trop grande : `{"detail": "Zone trop grande : 1.0° × 1.0° maximum."}`
- `in_bbox` mal formé : `{"detail": "Invalid bbox string supplied for parameter in_bbox"}`

Ordre de grandeur : une tuile dense du centre d'Orléans (environ 5 000 points) répond en 0,13 s et pèse 210 Ko compressée.

### `GET /api/equipements/{id}/`

Fiche complète. `404` si l'identifiant (UUID) n'existe pas.

```json
{
  "id": "b774218b-52b1-45d1-8f3d-2f591e6d077c",
  "nom": "Sarl Sabourin Ondet",
  "adresse": "3 rue Marcel Dassault",
  "codepostal": "37520",
  "ville": "La Riche",
  "siret": "90341280700013",
  "departement": "Indre-et-Loire",
  "domaine1": "Services pour les particuliers",
  "domaine2": "Services automobiles",
  "domaine3": "Réparation automobile et de matériel agricole",
  "domaine3_code": "A301",
  "longitude": 0.66541,
  "latitude": 47.38025
}
```

### `GET /api/domaines/`

Arbre complet pour le panneau de filtres (7 domaine1, 27 domaine2, 235 domaine3), trié par code.

```json
[
  {
    "code": "F",
    "libelle": "Sports, loisirs et culture",
    "enfants": [
      { "code": "F3", "libelle": "Culture", "enfants": [ { "code": "F307", "libelle": "Bibliothèque" } ] }
    ]
  }
]
```

### `GET /api/villes/`

| Paramètre | Description |
| --- | --- |
| `search` | Partie du nom, sans tenir compte de la casse. Renvoie 20 villes au maximum |

Sans `search` : les 1 739 villes de la région, triées. Exemple : `GET /api/villes/?search=orl` → `["Morlac", "Orléans", "Vorly"]`

## Implantations (privé, token obligatoire)

Chaque utilisateur ne voit et ne manipule **que ses propres implantations** : l'implantation d'un autre
utilisateur répond `404` en lecture, modification et suppression, comme si elle n'existait pas.
Le propriétaire est fixé par le serveur ; un champ `proprietaire` envoyé par le client est ignoré.

Format : une `Feature` GeoJSON.

### `POST /api/implantations/`

```json
{
  "type": "Feature",
  "geometry": { "type": "Point", "coordinates": [0.6889, 47.3941] },
  "properties": {
    "titre": "Projet boulangerie centre-ville",
    "domaine3": "B207",
    "commentaire": "Loyer à vérifier"
  }
}
```

`201` → la `Feature` créée, avec `id`, `cree_le` et `modifie_le` dans les propriétés.

| Champ | Obligatoire | Description |
| --- | --- | --- |
| `geometry` | oui | Point `[longitude, latitude]` |
| `properties.titre` | oui | 255 caractères maximum |
| `properties.domaine3` | non | Code domaine3 existant (type de commerce envisagé) ou `null` |
| `properties.commentaire` | non | Texte libre |

`400` si la géométrie manque ou si le code `domaine3` n'existe pas.

### `GET /api/implantations/`

`200` → `FeatureCollection` des implantations de l'utilisateur connecté.

### `GET` · `PUT` · `PATCH` · `DELETE /api/implantations/{id}/`

- `PATCH` modifie seulement les champs envoyés, par exemple `{"properties": {"titre": "Nouveau titre"}}` ;
- `PUT` remplace la `Feature` complète (géométrie et propriétés) ;
- `DELETE` répond `204`.

## Exemple complet avec curl

```bash
# Inscription : récupère un token
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "MotDePasse-Solide-42"}'

# Création d'une implantation
curl -X POST http://localhost:8000/api/implantations/ \
  -H "Authorization: Token <clé>" -H "Content-Type: application/json" \
  -d '{"type": "Feature", "geometry": {"type": "Point", "coordinates": [0.6889, 47.3941]},
       "properties": {"titre": "Projet boulangerie", "domaine3": "B207"}}'

# Liste de ses implantations
curl http://localhost:8000/api/implantations/ -H "Authorization: Token <clé>"
```

Sous Windows PowerShell, utiliser `curl.exe` (et non l'alias `curl`) pour que les guillemets du JSON soient conservés.
