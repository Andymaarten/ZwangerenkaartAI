---
title: Validatieprotocol
---

# Validatieprotocol ZwangerenkaartAI

**Status: CONCEPT.** Dit protocol wordt vóór de validatierun gecommit. De commit-datum en -hash in deze repository gelden
als preregistratie. Afwijkingen na die commit staan met datum en reden in §12.

Velden tussen `[ ]` worden ingevuld vóór de commit.

---

## 1. Beoogd gebruik en claim

ZwangerenkaartAI zet een verloskundige zwangerenkaart (PDF) om in een overzicht voor de zorgverlener: patiëntgegevens,
medische gegevens en 88 aandachtspunten. Per aandachtspunt toont het alleen letterlijke passages uit de kaart, zonder
oordeel of score. De zorgverlener beoordeelt de passages en beslist. Het systeem draait lokaal in het Spaarne Gasthuis
(MDR klasse I, in-house).

**Claim die deze validatie toetst** (overeenkomst, fase 2: "de validatie is geslaagd als tijdens de test 90% van de
noodzakelijke aandachtspunten in de samenvatting worden genoemd"): van de aandachtspunten die volgens de gouden standaard
van toepassing zijn, noemt het systeem er minstens 90% in het rapport, met minstens één passage. De gouden standaard is
het oordeel van de beoordelende gynaecoloog na inzage van de passages en het zorgplan (E1); samengestelde
aandachtspunten worden gescoord volgens §4.8 en AP079 telt niet mee (§4.7).

De validatie toetst niet of het gebruik van het systeem klinische uitkomsten verbetert.

## 2. Versie

De versie wordt bevroren vóór de run en verandert daarna niet.

| Onderdeel | Waarde |
|---|---|
| Code (git-tag en commit) | `v3-ontwikkelset-20261015` · `bb75928` (laatste ontwikkelrun 15→16 okt; bevestigen na die run) |
| Vragen en aandachtspunten (`questions/`, commit) | `a99f061` · `aandachtspunten.json` versie 5.5 |
| Docker-image (digest) | `andymaarten/zorgplan:v3-ontwikkelset-20261015` · `sha256:02a566777d1fedff41d98fb8c55e625210a9150b30e54b14d05b72d5b5ba5907` |
| Config-hash (code, prompts, aandachtspunten, vragenlijst, drempel, model) | `c31db1d8ba93` bij modelnaam `medgemma`; heet het model op de server anders, dan geldt de hash uit het eerste serverrapport `[ ]` |
| Model | medgemma 27B, kwantisatie Q8_0, via Ollama, op de server van het Spaarne Gasthuis |
| Drempel call 2 | `[ ]`, vastgesteld volgens §2.1. Wordt tijdens de validatie niet aangepast. |
| Git-sync van `questions/` tijdens de run | uit (`GIT_SYNC_QUESTIONS=0` in de `.env` van de server; waarde vastleggen) |

Elke resultaatfile bevat code-commit en config-hash. Kaarten met een andere config-hash tellen niet mee voor de primaire
analyse (het analysescript meldt dit).

### 2.1 Vaststelling van de drempel

De drempel bepaalt welke passages call 2 laat staan (een passage blijft als de kans op *ja* minstens de drempel is).
Hij wordt één keer vastgesteld, vóór de validatierun, en daarna niet meer veranderd.

- **Gegevens:** de laatste run op de ontwikkelset (kaarten 1–40) met de bevroren versie op de server, vergeleken met de
  gouden standaard van de ontwikkelset (samengestelde aandachtspunten volgens methode A, §4.8). De kansen per passage
  worden bij elke run opgeslagen, dus de recall bij elke drempel is uit te rekenen zonder het model opnieuw te draaien
  (`tools/analyse.py`).
- **Regel:** de drempel is de hoogste waarde waarbij de recall op de ontwikkelset minstens [97]% is.
- **Waarom een marge:** de definities en de drempel zijn op de ontwikkelset afgesteld, dus de recall op nieuwe kaarten
  valt naar verwachting lager uit. De marge boven het criterium van 90% (§5) vangt dat op. De prijs is meer onterechte
  passages; het aantal fout-positieven per kaart bij de gekozen drempel wordt gerapporteerd.
- **Vastlegging:** drempel, bijbehorende recall en fout-positieven per kaart op de ontwikkelset, en de config-hash
  (die de drempel bevat) worden in §2 en in `docs/versies.md` ingevuld vóór de validatierun.

## 3. Kaarten

**Populatie.** Zwangeren die vanuit de eerstelijns verloskundige zorg zijn verwezen naar de afdeling Verloskunde en
Gynaecologie van het Spaarne Gasthuis en schriftelijk toestemming gaven voor gebruik van hun gegevens.

**Welke kaart.** Per patiënt wordt de zwangerenkaart gebruikt zoals die bij de verwijzing binnenkwam en in Epic is
vastgelegd (meestal als digitale verwijzing, soms ingescand). Systeem, experts en zorgplan gaan uit van dezelfde kaart
en hetzelfde moment: het zorgplan (ZP) is de eerste zorgplannotitie in Epic na de datum waarop deze kaart is ontvangen,
dus de notitie van het eerste consult na verwijzing. Latere versies van de kaart en latere notities worden niet gebruikt.

**Inclusie:**

- verwezen vanuit de eerste lijn, met schriftelijke toestemming;
- zwangerenkaart ontvangen in Epic in het tweede of derde kwartaal van 2026;
- de kaart is beschikbaar als PDF waaruit tekst kan worden gehaald.

**Exclusie:**

- de kaart is gebruikt in de ontwikkelfase of in eerdere tests (de kaarten 1–40 van de huidige gouden standaard en
  eerdere testkaarten);
- de kaart ontbreekt, of de PDF bevat geen uitleesbare tekst (bijvoorbeeld alleen een gescande afbeelding);
- een tweede kaart van dezelfde zwangerschap (alleen de eerste telt).

Een kaart zonder zorgplannotitie wordt niet uitgesloten: hij telt mee voor de primaire uitkomst, maar niet voor de
analyses waarin ZP voorkomt. Ontbrekende notities tellen niet als "aandachtspunt afwezig". Het aantal kaarten per
reden van exclusie en het aantal kaarten zonder notitie worden gerapporteerd.

**Aantal en selectie.** Minimaal 40 kaarten, aselect geloot uit de kaarten die aan de criteria voldoen. Methode en zaad
van de loting worden vastgelegd. Het verzamelen gebeurt volgens bijlage A (onderaan).
De validatiekaarten krijgen de nummers 41–80, in de volgorde van de loting, los van de ontwikkelset.

## 4. Beoordelingen per aandachtspunt per kaart

Per kaart en per aandachtspunt worden vier beoordelingen vastgelegd (0 = niet van toepassing, 1 = van toepassing):

| Code | Beoordeling | Door | Moment |
|---|---|---|---|
| **ZP** | Zorgplan zoals in de huidige praktijk opgesteld | wetenschappelijk stagiair, los van de experts | vooraf |
| **E0** | Eerste oordeel van de expert, zonder uitvoer van het systeem en zonder zorgplan | één van twee gynaecologen per kaart (de kaarten zijn verdeeld) | vóór inzage, vastgelegd met commit |
| **M** | Systeem: passages getoond (1) of niet (0), plus de interne score | de bevroren versie | validatierun |
| **E1** | Oordeel van de expert na inzage van de passages én het zorgplan: de uiteindelijke gouden standaard | dezelfde gynaecoloog als bij E0 | na de run |

**Werkwijze.**

1. De kaarten worden verdeeld over twee gynaecologen; elke kaart wordt door één van hen beoordeeld. De gynaecoloog
   scoort E0 op basis van de zwangerenkaart, zonder de uitvoer van het systeem of het zorgplan te zien. Het bestand met
   E0 (kaartnummer, AP, 0/1, beoordelaar A of B, geen patiëntgegevens) wordt gecommit **vóórdat** de experts enige
   uitvoer van het systeem of het zorgplan zien. De commit-hash bewijst de volgorde.
2. ZP wordt onafhankelijk van E0 gecodeerd en ook vóór de inzage gecommit.
3. Daarna ziet de gynaecoloog het rapport van het systeem en het zorgplan, en legt E1 vast. Elke wijziging ten
   opzichte van E0 krijgt een aanleiding (systeem, zorgplan, beide, eigen herlezing) en een reden: (a) gemist bij het
   lezen, (b) andere interpretatie van de definitie, (c) passage of zorgplan overtuigend, (d) anders.
4. **Blinde bevestiging van toegevoegde aandachtspunten.** Alle gevallen met E0 = 0 en E1 = 1 worden, gemengd met een
   gelijk aantal willekeurige gevallen met E0 = 1 en E0 = 0, voorgelegd aan de andere gynaecoloog, die de kaart niet
   eerder beoordeelde en niet weet uit welke groep een geval komt.
5. **Codeboek en twijfelgevallen.** Het codeboek is de `betekenis` per aandachtspunt in `aandachtspunten.json` van de
   bevroren versie. Een twijfelgeval krijgt een opmerking in het bestand en wordt besproken met de andere gynaecoloog;
   de beoordelaar van de kaart beslist.
6. **Niet in de kaart.** Een aandachtspunt dat de experts of het zorgplan kennen uit een andere bron dan deze
   zwangerenkaart (bijvoorbeeld informatie uit het consult), krijgt de aantekening "niet in de kaart" en telt niet mee
   voor de vergelijkingen. Het aantal wordt gerapporteerd.
7. **AP079 (kwetsbaarheden)** telt niet mee voor de primaire uitkomst en wordt apart beschreven.
8. **Samengestelde aandachtspunten** (risicofactoren voor pre-eclampsie, diabetes gravidarum en trombose): het
   aandachtspunt is 1 als minstens één factor uit de factorlijst van de bevroren versie in de kaart staat ("methode A",
   vastgelegd 15-10-2026). Of de combinatie van factoren een indicatie geeft, beoordeelt de zorgverlener; dat wordt
   niet gescoord. De gouden standaard van de ontwikkelset is op 15-10-2026 volgens deze regel herscoord (27 regels; de
   reden staat per regel in de kolom `opmerking`).

## 5. Primaire uitkomst

**Recall van het systeem ten opzichte van de gouden standaard (E1)**, op het niveau van aandachtspunt per kaart,
gepoold over alle kaarten:

recall = aantal (E1 = 1 en M = 1) / aantal (E1 = 1)

- 95%-betrouwbaarheidsinterval met een **cluster-bootstrap per kaart**: de aandachtspunten van één kaart zijn geen
  onafhankelijke waarnemingen (zelfde patiënt, zelfde kaart, zelfde beoordelaars). Daarom worden 2000 keer 40 kaarten
  met teruglegging getrokken, telkens wordt de recall berekend, en het 2,5e en 97,5e percentiel vormen het interval
  (vast zaad). Het Wilson-interval, dat de samenhang negeert, wordt daarnaast gerapporteerd.
- **Succescriterium:** de recall tegen E1 is minstens 90% (puntschatting), zoals in de overeenkomst. Bij ~150 positieven
  betekent dat hoogstens 15 missers.
- Het 95%-betrouwbaarheidsinterval wordt altijd gerapporteerd, met de vermelding of de ondergrens ook boven 90% ligt.
  Dat laatste is geen slaagcriterium, maar zegt hoe zeker de uitkomst is.
- **Hernieuwde validatie:** wordt het criterium niet gehaald, dan kan de versie worden aangepast (vastgelegd in
  `docs/versies.md`) en opnieuw gevalideerd met dit protocol, op een nieuwe set kaarten die niet eerder is gebruikt.
- **Bias.** E1 komt tot stand na inzage van de uitvoer van het systeem. Aandachtspunten die de experts pas na inzage
  toevoegen, zijn vooral punten die het systeem toonde; punten die systeem, zorgplan en experts alle drie missen, komen
  niet boven. De recall tegen E1 valt daardoor gunstiger uit dan de werkelijke recall (*incorporation bias*). Daarom
  wordt de recall tegen het blinde oordeel (E0) als eerste secundaire uitkomst gerapporteerd, met hetzelfde interval en
  naast hetzelfde criterium.

## 6. Secundaire uitkomsten

1. **Recall tegen het blinde oordeel (E0):** aantal (E0 = 1 en M = 1) / aantal (E0 = 1), met cluster-bootstrapinterval,
   vergeleken met het criterium van §5. Dit is de controle op de bias van de primaire uitkomst.
2. **Huidige praktijk tegenover de expert:** recall van het zorgplan (aandeel expert-positieven dat in het zorgplan
   staat), precisie van het zorgplan (aandeel zorgplanpunten dat de expert deelt), positive agreement en kappa; ten
   opzichte van E0 en van E1.
3. **Aanvullende signalering:** aantal gevallen met E0 = 0, M = 1 en E1 = 1, per kaart en per 100 kaarten, met
   cluster-bootstrapinterval. Apart: de deelverzameling waarin ook ZP = 0. Met het bevestigingspercentage uit §4.4.
4. **Wijzigingen in omgekeerde richting:** gevallen met E0 = 1 en E1 = 0.
5. **Systeem tegenover zorgplan, gepaard:** recall van M en van ZP ten opzichte van E1 (beide bronnen konden E1
   beïnvloeden) en van E0, met het verschil en een 95%-interval (gepaarde analyse, cluster-bootstrap). Beschrijvend.
6. **Zorgplan en systeem samen:** aandeel E1-positieven dat in ZP of M voorkomt, en het aantal dat beide missen.
7. **PPV en fout-positieven per kaart**, ten opzichte van E1 en van E0.
8. **Per kaart:** aandeel kaarten waarop het systeem alle E1-positieven vond, aandeel met minstens één misser, en
   aandeel waarop het systeem een aandachtspunt toonde dat in het zorgplan ontbrak en in E1 werd bevestigd.
9. **Overig, beschrijvend:** aandachtspunten per rapport;
   ROC-AUC en PR-AUC van de interne score; uitkomsten per categorie; verwerkingsduur per kaart.

## 7. Letterlijkheid

Elke getoonde passage moet letterlijk in de kaarttekst staan. De code controleert dit bij elke passage. Daarnaast
controleert een apart script na de run **alle** getoonde passages tegen de kaarttekst. Verwacht: 100%. Elke afwijking
wordt beschreven.

## 8. Foutenanalyse

Elke misser (E1 = 1 of E0 = 1, en M = 0) wordt beschreven met de stap waarin het misging:

- niet als kandidaat gevonden (zoekwoorden en call 1);
- weggevallen in de harde controle of het Python-filter;
- door call 2 onder de drempel;
- Python-regel gaf een andere waarde;
- tekstextractie uit de PDF;
- discutabel in de referentie.

Per categorie worden ook de fout-positieven samengevat.

Elke combinatie van referentie, zorgplan en systeem wordt ingedeeld volgens deze tabel (E = E1, met E0 ernaast):

| E | ZP | M | Betekenis |
|---|---|---|---|
| 1 | 1 | 1 | beide gevonden |
| 1 | 0 | 1 | systeem vond wat het zorgplan miste |
| 1 | 1 | 0 | zorgplan vond wat het systeem miste |
| 1 | 0 | 0 | beide gemist |
| 0 | 0 | 1 | fout-positief van het systeem |
| 0 | 1 | 0 | zorgplanpunt dat de experts niet uit de kaart halen |
| 0 | 1 | 1 | beide fout-positief |
| 0 | 0 | 0 | terecht negatief |

## 9. Herhaalbaarheid

Het systeem draait met temperatuur 0 en vaste instellingen en hoort bij dezelfde invoer dezelfde uitvoer te geven.
Ter controle worden 10 validatiekaarten een tweede keer verwerkt met dezelfde versie op dezelfde server. Gerapporteerd:
het aantal aandachtspunten met een andere uitkomst (M) tussen de twee runs. Verwacht: nul.

## 10. Vergelijking met de vorige versie

Waar beschikbaar wordt de vorige versie (v1, ja/nee per aandachtspunt) beschrijvend vergeleken. Geen toets.

## 11. Technische fouten

Mislukt de verwerking van een kaart of een aandachtspunt door een technische fout, dan wordt de kaart één keer opnieuw
verwerkt met dezelfde versie. Het aantal herhalingen en blijvende fouten wordt gerapporteerd. Blijvend mislukte
aandachtspunten tellen als M = 0.

## 12. Afwijkingen van het protocol

| Datum | Afwijking | Reden |
|---|---|---|
| | | |

## 13. Publicatie

De gouden standaard (E0, E1, ZP: kaartnummer, AP, 0/1), het analysescript en de geaggregeerde resultaten worden in deze
repository gepubliceerd, ook als het succescriterium niet wordt gehaald. Kaartteksten en passages worden niet
gepubliceerd.

## Ethiek en gegevensverwerking

Bestaande zwangerenkaarten en zorgplannotities worden gebruikt na schriftelijke toestemming van de deelnemers,
onder een onderzoeksnummer en volgens het beleid van het Spaarne Gasthuis. De verwerking door het systeem gebeurt op
de server van het ziekenhuis; er gaan geen gegevens naar buiten. De vergelijking is retrospectief en verandert de zorg
niet: de uitvoer van het systeem wordt niet gebruikt om bestaande zorgplannen aan te passen.

## Niet in dit protocol

- De juistheid en volledigheid van de patiëntgegevens en medische gegevens in het rapport (vorige zwangerschappen,
  echo's, medicatie, allergieën). Die worden apart beoordeeld met een eigen, vooraf vastgelegde methode.
- De tijdsbesteding met en zonder het systeem (aparte prospectieve deelstudie).

## 14. Monitoring na de validatie

Na ingebruikname wordt de werking doorlopend en per kwartaal gecontroleerd, als onderdeel van het markttoezicht
(post-market surveillance) van de MDR.

**Doorlopend, op alle kaarten (automatisch, zonder gouden standaard):** letterlijkheid van de getoonde passages
(verwacht 100%), aandeel technische fouten, en het aantal aandachtspunten en passages per rapport. Een plotselinge
verschuiving is een signaal voor een gewijzigd kaartformaat of een technisch probleem.

**Per kwartaal, op een steekproef:** 10 willekeurige kaarten van zwangeren die toestemming gaven, blind gescoord door
één expert vóór inzage van de uitvoer (~35 positieve aandachtspunten).

- Elke misser wordt geanalyseerd zoals in §8.
- Recall onder 90% in de kwartaalsteekproef: analyse van de oorzaak en herbeoordeling van de versie, zo nodig met een
  aanpassing volgens het wijzigingsbeheer hieronder.
- Jaarlijks, over vier kwartalen samen (~140 positieven): ondergrens van het 95%-interval onder 90% leidt tot
  herbeoordeling en zo nodig hervalidatie.

Een steekproef van 10 kaarten geeft een breed interval: het is een signaal, geen nieuwe validatie.

**Wijzigingsbeheer.** Elke wijziging aan model, prompts, aandachtspunten (`aandachtspunten.json`), drempel of
tekstextractie is een nieuwe versie. Vóór ingebruikname draait de nieuwe versie op een vaste regressieset (de kaarten van
de ontwikkelset met hun gouden standaard). De wijziging gaat alleen live als de recall op die set niet daalt; de
uitkomst wordt vastgelegd in `docs/versies.md`. Automatische synchronisatie van `questions/` naar de productieserver
gebeurt alleen vanuit een versie die deze controle heeft doorlopen.

## 15. Beperkingen

- Eén ziekenhuis; het systeem werkt op platte tekst en de meest gangbare kaartformaten zijn getest.
- De experts die E0 scoren, kennen het project en de aandachtspunten.
- Elke kaart is door één gynaecoloog beoordeeld; de overeenstemming tussen beoordelaars is niet gemeten. De blinde
  bevestiging door de andere gynaecoloog (§4.4) is een gedeeltelijke controle.
- E1, de referentie van de primaire uitkomst, is beïnvloed door het systeem (zie §5); de recall tegen het blinde oordeel
  E0 wordt daarom ernaast gerapporteerd.
- Het zorgplan legt vast wat de zorgverlener heeft opgeschreven, niet wat die heeft gezien.

## Bijlage A. Verzamelen van kaart en zorgplannotitie

Per gelote deelnemer, met het validatienummer (041–080):

1. Sla de zwangerenkaart uit Epic op als PDF met de naam `Kaart_<nummer>` (bijv. `Kaart_041`).
2. Noteer de datum waarop de kaart (digitale verwijzing of scan) in Epic is ontvangen.
3. Zoek de eerste zorgplannotitie na die datum. Noteer de datum en sla de notitie op als `ZPN_<nummer>`.
4. Geen zorgplannotitie gevonden: noteer dat; de kaart doet mee zonder ZP.

De koppellijst tussen validatienummer, toestemmingsformulier en patiënt blijft in het ziekenhuis en komt niet in deze repository.
