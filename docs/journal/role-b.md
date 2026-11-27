# Journal – Rôle B · Carte et interface Vue

27 novembre 2026. Les horaires correspondent aux commits ou aux captures de test.

## 11:54 – Passer de la carte de démonstration aux données réelles

- **Problème** — La première carte, centrée sur Tours à 11 h 08, affichait un petit jeu GeoJSON fictif. Il fallait désormais parcourir les équipements de toute la région.
- **Cause** — L’API limite chaque requête à une zone de 1° × 1°. Deux vues voisines couvrent souvent les mêmes équipements.
- **Solution** — J’ai découpé la vue en tuiles, mis en cache les tuiles chargées et dédupliqué les points par UUID avant leur regroupement sur la carte. Depuis 12 h 06, un clic sur un point charge sa fiche détaillée.
- **Temps perdu** — Aucun blocage relevé.

## 12:24 – Combiner les filtres de plusieurs domaines

- **Problème** — Il fallait pouvoir afficher à la fois un domaine entier et une activité précise d’un autre domaine, tout en gardant le filtre de ville.
- **Cause** — Django applique ensemble les critères de niveaux différents. Une requête unique aurait exigé qu’un équipement remplisse les deux conditions.
- **Solution** — Pour chaque tuile, le front interroge l’API par niveau sélectionné avec les mêmes villes, puis réunit les résultats par UUID.
- **Temps perdu** — Non mesuré.

## 13:55 – Débordement de la carte pendant l’ajout d’une implantation

- **Problème** — À l’ouverture du formulaire, les tuiles et les groupes de marqueurs recouvraient les filtres. Le débordement persistait après la fermeture.
- **Cause** — Le défaut apparaissait lors de la superposition du formulaire et des couches Leaflet.
- **Solution** — Le formulaire s’affiche dans le cadre de la carte. La capture de 14 h 08 montre de nouveau les filtres entièrement visibles. J’ai aussi vérifié avec deux comptes que le propriétaire retrouve son point après rechargement, peut le modifier puis le supprimer, et que le second compte ne le voit pas.
- **Temps perdu** — Environ 13 minutes entre les deux captures, essais compris.

## 14:19 – Retrouver une ville ou une implantation hors écran

- **Problème** — Après avoir filtré sur Blois depuis Tours, il fallait encore déplacer la carte. Une implantation éloignée était aussi difficile à retrouver.
- **Cause** — Le filtre changeait les équipements affichés sans déplacer la vue.
- **Solution** — La carte cadre les équipements de la ville choisie. Sous les filtres, « Mes implantations » liste les points du compte connecté. Un clic centre la carte sur le marqueur correspondant.
- **Temps perdu** — Aucun blocage relevé.

## 14:44 – Distinguer une adresse trouvée d’une adresse couverte

- **Problème** — La recherche postale ajoutée à 14 h 40 trouvait aussi des adresses à Paris, alors que TerriScope couvre les équipements du Centre-Val de Loire.
- **Cause** — Le géocodage de l’IGN couvre la France entière.
- **Solution** — J’ai utilisé le code INSEE de la commune pour signaler les résultats hors région. Sur ordinateur et mobile, Paris affiche l’avertissement, puis sélectionner Tours ou effacer le repère le retire.
- **Temps perdu** — Aucun blocage relevé.

## 14:55 – Rechercher un équipement par son nom

- **Problème** — Depuis Tours, il fallait pouvoir retrouver un établissement à Chartres, même si plusieurs établissements portaient le même nom.
- **Cause** — La carte charge seulement les tuiles visibles. Le nom seul ne permet pas de distinguer les homonymes.
- **Solution** — Dès trois caractères, une recherche régionale renvoie jusqu’à dix résultats avec adresse et commune. J’ai sélectionné l’établissement de Chartres parmi deux homonymes et vérifié le centrage, la fiche et le maintien du filtre actif sur ordinateur et mobile.
- **Temps perdu** — Aucun blocage relevé.
