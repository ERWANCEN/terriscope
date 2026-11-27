# Guide d'utilisation – TerriScope

Ce guide décrit le fonctionnement de l'interface web TerriScope (`http://localhost:5173/`) pour explorer les équipements publics de la région Centre-Val de Loire (BPE 2025) et gérer ses implantations privées de prospection.

## 1. Explorer les équipements publics (accès libre)

À l'ouverture de l'application, la carte interactive (Leaflet) affiche les équipements de la BPE 2025 dans la zone visible :

- **Navigation** : déplacer la carte et zoomer pour charger automatiquement les équipements de l'emprise courante (`in_bbox`). Les points proches sont regroupés en clusters pour garder la carte fluide.
- **Filtrage par domaine** : utiliser le panneau de filtres pour sélectionner un grand domaine (`domaine1`), un sous-domaine (`domaine2`) ou un type d'équipement précis (`domaine3`).
- **Filtrage par commune** : rechercher et sélectionner une ou plusieurs villes pour restreindre l'affichage.
- **Fiche détaillée** : cliquer sur un équipement pour afficher ses informations complètes (nom, type, adresse, commune, code postal, SIRET).

## 2. Créer un compte et se connecter

Les données de prospection sont strictement personnelles. Pour y accéder :

1. Ouvrir le bloc **Connexion** dans l'interface.
2. Pour une première visite, cliquer sur **Créer un compte**, saisir un identifiant et un mot de passe (8 caractères minimum, non entièrement numérique), puis valider.
3. Si le compte existe déjà, saisir ses identifiants et cliquer sur **Se connecter**.

Une fois connecté, le jeton d'authentification est conservé dans le navigateur (`localStorage`) et votre nom d'utilisateur s'affiche dans l'interface.

## 3. Gérer ses implantations privées

Une fois connecté, vos projets d'implantation s'affichent sur la carte sous forme d'**épingles violettes**, visuellement distinctes des équipements publics BPE.

### Ajouter une implantation
1. Cliquer sur la carte à l'emplacement souhaité (ou activer le mode ajout selon l'interface).
2. Remplir le formulaire **Nouvelle implantation** :
   - **Titre** *(obligatoire)* : nom court du projet (ex. *Projet boulangerie centre-ville*).
   - **Type de commerce (`domaine3`)** *(optionnel)* : catégorie BPE envisagée.
   - **Commentaire** *(optionnel)* : notes de terrain, loyer, concurrence.
3. Cliquer sur **Ajouter** : le point est enregistré en base PostGIS et apparaît immédiatement sur la carte.

### Modifier ou supprimer une implantation
1. Cliquer sur une **épingle violette** existante.
2. Le formulaire s'ouvre pré-rempli avec les informations du point :
   - Modifier les champs souhaités puis cliquer sur **Enregistrer**.
   - Ou cliquer sur **Supprimer** puis confirmer pour retirer définitivement l'implantation.

## 4. Déconnexion et isolation des comptes

- Cliquer sur **Déconnexion** supprime le jeton local et efface immédiatement les épingles violettes de la carte (les équipements publics BPE restent visibles).
- Chaque compte ne voit et ne peut modifier que ses propres implantations : deux utilisateurs connectés successivement sur le même poste ne voient jamais les points de l'autre.