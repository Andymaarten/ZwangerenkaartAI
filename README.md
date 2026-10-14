# ZwangerenkaartAI

> **English summary.** ZwangerenkaartAI converts a Dutch obstetric record (*zwangerenkaart*, PDF) into an overview for
> the clinician. For each of 88 predefined points of attention it shows only verbatim passages from the record, without
> a verdict or score; the clinician makes every judgement. It runs fully on-premises with an open model (MedGemma 27B),
> and no patient data leaves the hospital. This repository contains the method, validation protocol, reference
> standard, analysis script and aggregated results; the source code is available to reviewers on request. A validation on new records is in progress. Project page:
> <https://andymaarten.github.io/ZwangerenkaartAI/>

ZwangerenkaartAI zet een verloskundige zwangerenkaart (PDF) lokaal om in een overzicht voor de zorgverlener:
patiëntgegevens, medische gegevens en 88 aandachtspunten. Per aandachtspunt toont het alleen de letterlijke passages uit
de kaart, zonder oordeel of score. De zorgverlener beoordeelt en beslist.

**Status:** onderzoeksproject van het Spaarne Gasthuis. De validatie op nieuwe kaarten loopt. Niet bedoeld voor
klinisch gebruik buiten de validatieomgeving.

**Projectpagina:** <https://andymaarten.github.io/ZwangerenkaartAI/>

## Wat het wel en niet doet

| Wel | Niet |
|---|---|
| patiëntgegevens (naam, geboortedatum, enzovoort) | diagnose, risicoscore of advies |
| 88 aandachtspunten, elk met letterlijke quotes uit de kaart | ja/nee per aandachtspunt |
| medische gegevens (vorige zwangerschappen, echo's, voorgeschiedenis, allergieën, medicatie) | de kaart of het oordeel van de zorgverlener vervangen |

## Hoe het werkt

Per aandachtspunt: een Python-regel voor meetbare waarden (BMI, leeftijd, rhesus, Hb, …), anders kandidaat-passages via
zoekwoorden en het taalmodel (call 1), een harde controle dat elk citaat letterlijk in de kaart staat, een Python-filter,
en een tweede modelaanroep die passages verwijdert die niet bijdragen aan het aandachtspunt. Het rapport bevat altijd de
echte kaarttekst. Details: [docs/methode.md](docs/methode.md).

## Resultaten

Zie de [projectpagina](https://andymaarten.github.io/ZwangerenkaartAI/#resultaten). Resultaten staan daar altijd met de
vermelding *ontwikkelset* of *validatieset*, met 95%-betrouwbaarheidsintervallen. De ontwikkelset bestaat uit kaarten die
tijdens de ontwikkeling zijn gebruikt; alleen de validatieset zegt iets over nieuwe kaarten.

## Validatie

Het validatieprotocol staat in [docs/validatieprotocol.md](docs/validatieprotocol.md) en is vóór de validatierun
gecommit (preregistratie). Kort: 40 nieuwe kaarten, twee gynaecologen (elk een deel van de kaarten) die eerst blind scoren, vergelijking met het zorgplan
uit de huidige praktijk, primaire uitkomst de recall ten opzichte van het expertoordeel na inzage, met de recall ten opzichte van het blinde
expertoordeel ernaast. Welke versie bij welke
resultaten hoort: [docs/versies.md](docs/versies.md).

## Zelf narekenen

De gouden standaard (`docs/resultaten/`: kaartnummer, aandachtspunt, 0/1) en het analysescript staan in deze
repository. Met de resultaatbestanden van een run (zonder kaarttekst, op aanvraag beschikbaar voor reviewers):

```bash
python3 tools/analyse.py <map met *_results.json> docs/resultaten/gouden_standaard_ontwikkelset.csv -o analyse.html
```

## Privacy

Alles draait op servers van het Spaarne Gasthuis; er gaan geen patiëntgegevens naar buiten. Deze repository bevat geen
patiëntgegevens: geen kaartteksten, geen passages, alleen kaartnummers en 0/1 in de gouden standaard. Meer: [docs/mdr-en-privacy.md](docs/mdr-en-privacy.md).

## Beperkingen

Eén ziekenhuis (de meest gangbare kaartformaten zijn getest); de gouden standaard is een expertoordeel; zeldzame
aandachtspunten komen weinig voor; definities veranderen mee met richtlijnen.
Zie [docs/beperkingen.md](docs/beperkingen.md).

## Team

Pieter-Kees de Groot (gynaecoloog, projectleider), Andreas Viruly (arts, technisch lead en strategie), Bart Voskamp
(gynaecoloog, implementatie en kennisverspreiding), Wouter Huijbers (arts, technische ontwikkeling), Diederik Feilzer
(klinisch fysicus in opleiding, technische ontwikkeling). Allen Spaarne Gasthuis en MSCK.

## Licentie

Alle rechten voorbehouden; deze repository is openbaar ter inzage. Zie [LICENSE](LICENSE).

## Citeren

Zie [CITATION.cff](CITATION.cff).

## Code

De broncode, de prompts en de definities van de aandachtspunten zijn niet openbaar. Ze zijn op aanvraag beschikbaar
voor reviewers. Welke versie bij welke resultaten hoort, staat in [docs/versies.md](docs/versies.md).
