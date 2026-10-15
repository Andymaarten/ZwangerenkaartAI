---
title: Versies
---

# Versies

Welke versie hoort bij welke resultaten. Elke uitvoer van het systeem bevat de code-commit en de config-hash; die zijn
hieronder terug te vinden.

| Resultaten | Code (tag · commit) | Definities en vragen (commit, niet openbaar) | Docker-image (digest) | Config-hash | Model | Drempel |
|---|---|---|---|---|---|---|
| Ontwikkelset (kaarten 1–40) | `v3-ontwikkelset-20261014` · `eaa82da` | `b54abef` (aandachtspunten v5.2) | `sha256:dde28ca449cb…ffb7` | `b417a8436c68` (modelnaam `medgemma`; op de server: hash uit het eerste rapport) | medgemma 27B Q8_0, Ollama | 0,3 |
| Ontwikkelset, laatste run vóór de validatie (kaarten 1–40) | `v3-ontwikkelset-20261015` · `bb75928` | `a99f061` (aandachtspunten v5.5) | `sha256:02a566777d1fedff41d98fb8c55e625210a9150b30e54b14d05b72d5b5ba5907` | `c31db1d8ba93` (modelnaam `medgemma`) | medgemma 27B Q8_0, Ollama | 0,3 |
| Validatieset (kaarten 41–80) | `[ ]` | `[ ]` | `[ ]` | `[ ]` | medgemma 27B Q8_0, Ollama | `[ ]` |

## Ontwikkelversies

| Datum | Versie | Wat er veranderde | Waarom |
|---|---|---|---|
| 14-10-2026 | `v3-ontwikkelset-20261014` | Citatenmethode met call 1 (letterlijke citaten), harde controle, Python-filter en call 2 (kans uit logprobs, drempel 0,3); rapport met hooguit twee passages per aandachtspunt en een bijlage; vragen met citaatcontrole en controlevraag | Eerste volledige run op de ontwikkelset |
| 15-10-2026 | `v3-ontwikkelset-20261015` | **Poorten**: een aandachtspunt dat volgens een zeker bepaalde waarde niet kan gelden (bijv. bariatrie bij BMI 30–40 terwijl de BMI 22 is), gaat niet naar het model. **Python-factor**: meetbare risicofactoren (nullipariteit, leeftijd ≥ 40, BMI > 30 of > 35) worden door Python als letterlijke passage toegevoegd. **BMI** alleen uit deze zwangerschap, zonder grenswaarden uit protocolteksten. **Call 2** krijgt de door Python vastgestelde waarden als context. Meer schrijfwijzen van G/P herkend; kale labels zonder uitslag tellen niet. Definities v5.3–v5.5 (o.a. bariatrie alleen de operatie, percentielbereik bij dysmaturiteit, laag-risico-antistoffen, nullipariteit uitgeschreven, extra zoekwoorden) | Foutenanalyse van de run van 14 oktober: de meeste fout-positieven kwamen van verkeerd getoetste getallen en periodes; de gemiste aandachtspunten van factoren die het model in G/P-notatie niet herkende |
| 15-10-2026 | gouden standaard | Samengestelde aandachtspunten herscoord volgens **methode A**: 1 als minstens één factor uit de factorlijst in de kaart staat (27 regels, reden per regel in het bestand) | Het systeem toont passages per factor; de zorgverlener weegt de combinatie. Vastgelegd in het [validatieprotocol](validatieprotocol.html) |

## Wijzigingen na de validatie

Elke wijziging aan model, prompts, definities, drempel of tekstextractie is een nieuwe versie. Vóór ingebruikname
draait die op de vaste regressieset (de ontwikkelset met gouden standaard).

| Datum | Versie | Wijziging | Recall regressieset | Besluit |
|---|---|---|---|---|
| | | | | |
