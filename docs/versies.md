---
title: Versies
---

# Versies

Welke versie hoort bij welke resultaten. Elke uitvoer van het systeem bevat de code-commit en de config-hash; die zijn
hieronder terug te vinden.

| Resultaten | Code (tag · commit) | Definities en vragen (commit, niet openbaar) | Docker-image (digest) | Config-hash | Model | Drempel |
|---|---|---|---|---|---|---|
| Ontwikkelset (kaarten 1–40) | `v3-ontwikkelset-20261014` · `eaa82da` | `b54abef` (aandachtspunten v5.2) | `sha256:dde28ca449cb…ffb7` | `b417a8436c68` (modelnaam `medgemma`; op de server: hash uit het eerste rapport) | medgemma 27B Q8_0, Ollama | 0,3 |
| Validatieset (kaarten 41–80) | `[ ]` | `[ ]` | `[ ]` | `[ ]` | medgemma 27B Q8_0, Ollama | `[ ]` |

## Wijzigingen na de validatie

Elke wijziging aan model, prompts, definities, drempel of tekstextractie is een nieuwe versie. Vóór ingebruikname
draait die op de vaste regressieset (de ontwikkelset met gouden standaard).

| Datum | Versie | Wijziging | Recall regressieset | Besluit |
|---|---|---|---|---|
| | | | | |
