---
name: journal
description: Note un blocage ou une décision dans le journal de bord de l'équipe, pour préparer le post-mortem.
disable-model-invocation: true
allowed-tools: Bash(date *)
---

Applique la procédure « Journal » de `AGENTS.md`.
Le rôle du développeur est dans `CLAUDE.local.md` ; l'heure s'obtient avec `date +%H:%M`.
Contenu de l'entrée : « $ARGUMENTS », complété par ce qui s'est passé dans cette conversation.
