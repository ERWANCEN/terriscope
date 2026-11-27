---
name: verifier
description: Vérifie que TerriScope fonctionne de bout en bout (conteneurs, Django, import, API, front) et affiche un bilan OK/KO.
disable-model-invocation: true
allowed-tools: Bash(docker compose ps *) Bash(docker compose logs *) Bash(docker compose exec backend *) Bash(docker compose exec frontend *)
---

Applique la procédure « Vérification » de `AGENTS.md`, sans modifier aucun fichier.
Si « $ARGUMENTS » est fourni (par exemple `api` ou `front`), ne lance que les contrôles correspondants.
