# Journal – Rôle A · Back et Docker

## 10:50 – Image PostGIS introuvable sur Mac Apple Silicon
- Problème : `docker compose up` échoue sur le service `db` avec « no matching manifest for linux/arm64/v8 in the manifest list entries ».
- Cause : l'image `postgis/postgis:18-3.6` n'est publiée qu'en `linux/amd64`, pas pour les puces Apple Silicon (arm64).
- Solution ou décision : ajout de `platform: linux/amd64` au service `db` dans `docker-compose.yaml` (émulation, plus lente mais fonctionnelle). Piège anticipé par le plan d'action (section 8).
- Temps perdu : environ 2 minutes.

## 12:01 – Carte lente au zoom minimum avec les vraies données
- Problème : au zoom 11 sur Tours, le front demande 96 tuiles (20 570 points) : 6,9 s avant l'affichage complet ; une tuile dense (Orléans, 4 921 points) pèse 900 Ko.
- Cause : mesure sur la tuile dense, la base n'est pas en cause (index GiST) : 0,12 s pour créer les objets Django et 0,22 s dans le serializer DRF, soit les 2/3 du temps.
- Solution ou décision : liste carte construite à la main avec `values_list` (format GeoJSON identique, vérifié point par point) et `GZipMiddleware`. Résultat : tuile dense 0,35 s → 0,13 s et 900 → 210 Ko ; zoom 11 : 6,9 s → 1,7 s. Suggestion à B : `ZOOM_MINIMUM` à 12.
- Temps perdu : environ 15 minutes (diagnostic et mesures).
