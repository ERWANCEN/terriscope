# TerriScope

Plateforme d'exploration et de prospection commerciale géographique, construite à partir de la
Base permanente des équipements (BPE 2025) de l'INSEE, pour la région Centre-Val de Loire (code 24).

Projet « Docker / Full Stack » – Groupe 1.

## Stack

Django 6.1 + GeoDjango + Django REST Framework · PostgreSQL 18 + PostGIS 3.6 · Vue 3 + Leaflet · Docker Compose

## Installation

_À compléter (rôle C) : prérequis, `cp .env.example .env`, `docker compose up --build`,
téléchargement du parquet dans `data/`, commande d'import, création d'un compte._

## Documentation

- Modèle de données : `docs/modele-donnees.md`
- API : `docs/api.md` et Swagger sur http://localhost:8000/api/docs/
- Utilisation : `docs/utilisation.md`
- Post-mortem : `docs/post-mortem.md`

## Outils

Développé avec l'assistance de Claude Code, Codex et Gemini Code Assist. Consignes communes aux assistants : `AGENTS.md`.
