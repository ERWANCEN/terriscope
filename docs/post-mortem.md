# Post-mortem – Projet TerriScope (Groupe 1)

**Date :** 27 novembre 2026  
**Équipe :** Rôle A (Infra, Docker, API BPE & performances) · Rôle B (Carte Leaflet, filtres & interface Vue) · Rôle C (ETL BPE, Authentification, Implantations privées & Documentation)

---

## 1. Ce qui a bien fonctionné

- **Découpage net des responsabilités et des fichiers** : la séparation entre le socle Docker/API publique (A), l'interface cartographique (B) et la chaîne données/authentification/implantations/documentation (C) a permis d'avancer en parallèle sur des branches dédiées avec très peu de conflits Git.
- **Environnement Docker reproductible** : une fois l'émulation `linux/amd64` ajoutée sur l'image PostGIS, les trois postes (Windows et macOS Apple Silicon) ont disposé exactement de la même stack (`postgis/postgis:18-3.6`, Django 6.1, Vue 3).
- **Efficacité des revues de Pull Requests** : les relectures croisées entre coéquipiers ont détecté des défauts réels avant ou juste après le merge — notamment l'ajout de `validate_password` et `@extend_schema` côté backend, ainsi qu'une erreur de copier-coller sur `ImplantationForm.vue` côté frontend.
- **Découplage public / privé** : l'isolation de l'application `prospection` vis-à-vis du référentiel `bpe` (seul lien optionnel via `domaine3` en `on_delete=SET_NULL`) garantit qu'un réimport complet des 93 274 équipements ne détruit aucune donnée utilisateur.

---

## 2. Principaux problèmes rencontrés et solutions

| Domaine | Problème constaté | Cause | Solution retenue |
| --- | --- | --- | --- |
| **Docker / macOS (A)** | Échec du démarrage de `db` sur Mac Apple Silicon (`no matching manifest for linux/arm64/v8`). | L'image officielle `postgis/postgis:18-3.6` n'est publiée qu'en `amd64`. | Ajout de `platform: linux/amd64` dans `docker-compose.yml` (~2 min). |
| **Données ETL (C)** | 3 821 lignes sur 97 095 en région Centre-Val de Loire (24) faisaient échouer l'import spatial. | Équipements INSEE sans coordonnées GPS exploitables dans le Parquet. | Filtrage strict des lignes sans coordonnées valides dans `import_bpe` : **93 274 équipements** importés dans l'ordre des clés étrangères (~5 min). |
| **Performances API (A)** | Zoom 11 sur Tours lent (6,9 s pour 20 570 points ; 900 Ko sur une tuile dense d'Orléans). | Sérialisation ORM + DRF représentant les 2/3 du temps de réponse (l'index spatial GiST était déjà rapide). | Construction manuelle du GeoJSON via `values_list` et activation de `GZipMiddleware` : temps divisé par 4 (6,9 s → 1,7 s ; tuile dense 900 → 210 Ko) (~15 min). |
| **Rechargement Django (A)** | API bloquée avec `RuntimeError` sur `prospection` juste après un `git pull`. | Le serveur de développement Django a redémarré en plein milieu de la mise à jour des fichiers (`urls.py` avant `settings.py`). | `docker compose restart backend` (~3 min). |
| **Intégration UI & superposition (B)** | À l'ouverture du formulaire d'implantation, les tuiles et clusters Leaflet recouvraient les filtres, même après fermeture. | Conflit d'empilement visuel lors de la superposition du formulaire et des couches Leaflet. | Affichage du formulaire dans le cadre de la carte et vérification complète du cycle de vie multi-comptes (création, rechargement, édition, suppression, isolation) (~13 min). |
| **Recherche hors région (B)** | Le géocodage IGN renvoyait des adresses hors Centre-Val de Loire (ex. Paris). | L'API de géocodage IGN couvre toute la France. | Vérification du code INSEE de la commune pour afficher un avertissement explicite hors région 24. |
| **Git & PowerShell Windows (C)** | Tests `curl` cassés sous PowerShell ; doublon sur `ImplantationForm.vue` corrigé sur la mauvaise branche (`docs/readme`). | Alias PowerShell `Invoke-WebRequest` sur `curl` ; oubli de changement de branche avant commit. | Usage de `curl.exe --data-binary "@-"` pour valider l'isolation `404` (`alice`/`bob`), et rapatriement du correctif sur `front/implantations` via `git cherry-pick` (~20 min cumulées). |
| **Base PostgreSQL (C)** | `backend` bloqué sur `password authentication failed` en fin de journée. | Désynchronisation du mot de passe entre le volume `pgdata` et `.env`. | Génération de `docs/openapi.yaml` avec `--no-deps` et resynchronisation via `ALTER USER` dans `db` sans perdre les 93 274 lignes (~10 min). |

---

## 3. Ce que nous ferions différemment

- **Planifier un point de synchronisation intermédiaire pour le branchement frontend** : la séparation des fichiers a évité les conflits, mais un jalon dédié plus tôt aurait permis de relier `LoginForm`, `ImplantationForm` et `implantationsLayer` et de régler les ajustements CSS/Leaflet avec moins de pression en fin de journée.
- **Vérifier systématiquement la branche active avant chaque commit** (`git branch --show-current`) et exécuter une validation automatique (compilation Vue SFC / `manage.py check`) avant d'ouvrir une PR.
- **Documenter dès le départ les spécificités OS** (émulation `amd64` sur macOS, `curl.exe` sous PowerShell Windows, redémarrage du conteneur `backend` après un `git pull` touchant `INSTALLED_APPS`).

---

## 4. Retour d'expérience sur les assistants IA

L'équipe a utilisé **Claude Code**, **Codex** et **Gemini Code Assist** encadrés par les règles communes du fichier `AGENTS.md` :

- **Apports principaux** : accélération nette sur le squelette Django/GeoDjango, la commande ETL Parquet, la structure des composants Vue 3, le découpage en tuiles/cache côté carte et la rédaction de la documentation technique (`modele-donnees.md`, `api.md`, `utilisation.md`).
- **Limites constatées** : les assistants ne détectent pas seuls les effets de bord liés à l'environnement local (alias PowerShell, désynchronisation de volume Docker, superposition CSS Leaflet) ni les erreurs humaines de manipulation Git ou de copier-coller.
- **Enseignement clé** : l'IA augmente fortement la vitesse de production, mais la qualité finale repose sur les **revues humaines de PR**, les **mesures réelles** (profilage des tuiles d'Orléans, compteurs ETL) et les **tests bout-en-bout** (isolation entre deux comptes utilisateurs).