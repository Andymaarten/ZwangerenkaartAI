---
title: Logboek validatie
---

# Logboek validatie ZwangerenkaartAI

Chronologisch overzicht van elke stap, met het bewijs waar die stap is vastgelegd. Tijden in UTC. Dit logboek bevat geen
patiëntgegevens. De technische logbestanden van de runs (per kaart de modelaanroepen en de uitvoer) bevatten
kaarttekst en blijven op de server van het Spaarne Gasthuis; zie onderaan.

## Ontwikkeling

| Datum | Stap | Vastgelegd in |
|---|---|---|
| 14-10-2026 | Eerste bevroren versie voor de ontwikkelset (`v3-ontwikkelset-20261014`) | code-repo, tag; [Versies](../../versies.html) |
| 15-10-2026 | Nieuwe versie `v3-ontwikkelset-20261015` (`bb75928`); gouden standaard ontwikkelset herscoord volgens methode A | code-repo, tag; commit `2acbde5` (deze repo) |
| 15/16-10-2026 | Laatste run op de ontwikkelset met de bevroren versie (config-hash `bcd127a3bc32`) | analyse ontwikkelset (lokaal) |
| 19-10-2026 | Analysescript vastgelegd (`tools/analyse.py`, commit `27e8d7f` in de code-repo) | code-repo |
| 19-10-2026 18:29 | Validatieprotocol vastgesteld en gepubliceerd | GitHub-release `validatieprotocol-2026-10-19` (commit `0a4671f`) |

## Validatie

| Datum en tijd | Stap | Vastgelegd in |
|---|---|---|
| 19-10-2026 18:41 | Validatierun op de server (40 kaarten, config-hash `bcd127a3bc32`); uitkomsten niet ingezien | serverlogs |
| 20-10-2026 | Scoringsregel (alleen 1 of 0) en nummering 042–081 in het protocol | commits `bf84b04`, `9d80ae1` |
| 20-10-2026 11:13 | E0_A, E0_B (blind) en ZP vastgelegd | commit `78f336f` |
| 20-10-2026 11:18 | Melding per e-mail aan het projectteam | e-mail |
| 20-10-2026 12:27 | E0 (consensus, blind) vastgelegd; analysescripts `secundair.py` en `voorleggen.py` openbaar | commit `2e8c165` |
| 20-10-2026 12:41 | Melding per e-mail aan het projectteam | e-mail |
| 20-10-2026 | Voorleglijst gemaakt; consensussessie van beide gynaecologen | lokaal (bevat passages) |
| 20-10-2026 17:31 | E1 (gouden standaard, met aanleiding en reden) vastgelegd | commit `16b1b00` |
| 20-10-2026 | Berekening van de uitkomsten (`analyse.py`, `secundair.py`) | `analyse_E1.html`, `analyse_E0.html`, `secundair.md` |
| [nog invullen] | Validatieverslag gepubliceerd | [commit] |

## Nog uit te voeren

- Herhaalbaarheid: tweede run op 10 validatiekaarten (protocol §9).

## Waar de technische logbestanden staan

Op de server van het Spaarne Gasthuis, in de map van de applicatie:

| Bestand | Inhoud |
|---|---|
| `data/output/antwoorden/<kaart>_results.json` | per aandachtspunt de kandidaat-passages, de uitkomst van elke stap en de versie (code, config-hash, drempel) |
| `data/output/logs/<kaart>_<tijd>_run.log` | verloop van de verwerking |
| `data/output/logs/<kaart>_<tijd>_raw_requests.jsonl` | elke modelaanroep met vraag en antwoord |
| `data/output/logs/<kaart>_<tijd>_v3_log.md` | verslag van de aandachtspunten per kaart |
| `data/output/rapporten/` | de rapporten zoals de zorgverlener ze ziet |
| `validatie/voorleglijst.csv` | de gevallen die in de consensussessie zijn voorgelegd |

Deze bestanden bevatten patiëntgegevens en worden bewaard volgens het beleid van het Spaarne Gasthuis. Ze worden niet
gepubliceerd. Reviewers kunnen op aanvraag inzage krijgen binnen het ziekenhuis.
