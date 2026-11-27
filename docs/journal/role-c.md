# Journal – Rôle C · Données, Auth, Implantations et Documentation

## 11:15 – Lignes BPE sans coordonnées lors de l'import ETL
- Problème : sur les 97 095 équipements de la région Centre-Val de Loire (code 24) présents dans le Parquet BPE 2025, 3 821 lignes n'ont pas de coordonnées géographiques exploitables et feraient échouer l'insertion dans le champ `PointField` non nul.
- Cause : certains équipements de la source INSEE ne sont pas géolocalisés (valeurs nulles ou invalides sur les colonnes de coordonnées).
- Solution ou décision : filtrage strict des lignes sans coordonnées valides dans la commande `import_bpe`, avec insertion dans l'ordre des clés étrangères (`regions` → `depts`, `domaine1` → `domaine2` → `domaine3`, puis `bpe`). Résultat : 93 274 équipements géolocalisés importés proprement.
- Temps perdu : environ 5 minutes (vérification des compteurs avant/après filtrage).

## 11:50 – Échec des tests API `curl` sous PowerShell Windows
- Problème : les requêtes de test `POST` sur `/api/auth/register/`, `/api/auth/token/` et `/api/implantations/` échouent ou envoient un JSON mal formé depuis le terminal VS Code sous Windows.
- Cause : dans PowerShell, `curl` est un alias de `Invoke-WebRequest` et l'interprétation des guillemets doubles dans les chaînes JSON casse les payloads.
- Solution ou décision : utilisation de `curl.exe` avec passage du corps JSON via `--data-binary "@-"`. Cela a permis de valider tous les endpoints ainsi que l'isolation entre deux comptes (`alice` et `bob`, réponse `404` sur le point de l'autre).
- Temps perdu : environ 10 minutes.

## 12:15 – Retours de revue sur la PR `auth/implantations`
- Problème : deux points relevés en revue de code avant merge : l'inscription acceptait des mots de passe trop faibles et la vue `MeView` générait un avertissement lors de la génération du schéma OpenAPI.
- Cause : absence des validateurs de mot de passe Django dans `RegisterSerializer` et absence d'annotation de schéma explicite sur `MeView`.
- Solution ou décision : ajout de `validate_password` dans `RegisterSerializer` et de `@extend_schema` sur `MeView`, puis vérification avec `python manage.py spectacular --validate` (0 erreur).
- Temps perdu : environ 8 minutes.

## 13:35 – `ImplantationForm.vue` dupliqué puis corrigé sur la mauvaise branche
- Problème : les coéquipiers signalent que `ImplantationForm.vue` est une copie identique de `LoginForm.vue` ; après correction, le commit est fait par erreur sur `docs/readme` au lieu de `front/implantations`.
- Cause : erreur de copier-coller lors de la création du composant, suivie d'un oubli de changement de branche avant le commit correctif.
- Solution ou décision : remplacement par le vrai formulaire (titre, type de commerce, commentaire, édition et suppression), rapatriement du commit sur `front/implantations` via `git cherry-pick`, validation du fichier SFC avec `vue/compiler-sfc`, push du correctif et suppression de la branche locale `docs/readme` avant de la recréer proprement depuis `origin/main`.
- Temps perdu : environ 10 minutes.

## 14:00 – Conteneur `backend` bloqué sur une erreur d'authentification PostgreSQL
- Problème : `docker compose exec backend python manage.py spectacular` échoue car le service `backend` ne démarre plus (`FATAL: password authentication failed for user "terriscope"`).
- Cause : désynchronisation entre le mot de passe du rôle PostgreSQL stocké dans le volume persistant `pgdata` et celui lu par le service `backend`.
- Solution ou décision : génération immédiate de `docs/openapi.yaml` via `docker compose run --rm --no-deps backend` (sans dépendance à la base), puis resynchronisation du mot de passe dans `db` avec `ALTER USER` pour éviter de supprimer le volume et de réimporter les 93 274 lignes BPE.
- Temps perdu : environ 10 minutes.