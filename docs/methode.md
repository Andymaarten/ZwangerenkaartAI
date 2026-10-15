---
title: Methode
---

# Methode

Deze pagina beschrijft hoe ZwangerenkaartAI van een zwangerenkaart tot een rapport komt, en waarom het zo is opgezet.
De broncode, de prompts en de definities van de aandachtspunten zijn niet openbaar; ze zijn op aanvraag beschikbaar
voor reviewers.

## Overzicht

```
PDF ─▶ tekst (met tabelherstel)
        ├─▶ patiëntgegevens en medische gegevens
        └─▶ 88 aandachtspunten
              ├─ Python-regel (meetbare waarden)
              ├─ focuspassages (zoekwoorden)
              ├─ call 1: citaten + korte argumentatie
              ├─ harde controle + Python-filter
              └─ call 2: passages zonder bijdrage eruit
        ─▶ rapport
```

Alles draait lokaal: het taalmodel (MedGemma 27B) op een server van het ziekenhuis, de software in een Docker-container
ernaast. Het model krijgt bij elke aanroep alleen de kaart en de vraag; er is geen gespreksgeheugen tussen aanroepen.

## Van PDF naar tekst

De tekst wordt met PyMuPDF uit de PDF gehaald. Tabellen in de kaart komen daarbij vaak uit elkaar (het label op de ene
regel, de waarde op de volgende). Een tabelherstel zet label en waarde weer op één regel, zodat een passage als
"BMI 30,7" leesbaar blijft. We hebben vijf andere methoden voor PDF-extractie vergeleken; die gaven meer structuur,
maar verminkten soms waarden of lieten een positief aandachtspunt wegvallen. Daarom blijft het bij platte tekst met
tabelherstel.

## Patiëntgegevens en medische gegevens

Voor elk onderdeel van het rapport (naam, geboortedatum, vorige zwangerschappen, echo's, voorgeschiedenis,
allergieën, medicatie) staat een vaste vraag in de vragenlijst. Zoveel mogelijk zit in die vragen; Python
controleert alleen of het antwoord in de kaart staat.

1. **Vraag.** Het model krijgt de hele kaart en de vraag. Bij een tabel (bijvoorbeeld medicatie of vorige
   zwangerschappen) geeft het per rij ook een citaat uit de kaart.
2. **Citaatcontrole.** Het citaat van elke rij wordt teruggezocht in de kaart. Staat het er niet in, dan valt de rij weg
   en meldt het rapport hoeveel rijen zijn weggelaten. Zo komt een verzonnen rij niet in het rapport. Lege en dubbele
   rijen vallen weg, en bij de huidige zwangerschap ook rijen met een datum van vóór deze zwangerschap.
3. **Controlevraag.** Bij een deel van de tabellen stelt het systeem per rij nog een ja/nee-vraag, bijvoorbeeld "is dit
   een geneesmiddel dat de patiënte in deze zwangerschap gebruikt?". Net als bij call 2 van de aandachtspunten wordt de
   kans op *ja* uit de logprobs gelezen, met dezelfde lage drempel: alleen rijen die duidelijk niet passen, vallen weg.

## Aandachtspunten

Een aandachtspunt is een klinisch relevant onderwerp uit de zwangerenkaart, bijvoorbeeld "sectio in de anamnese" of
"BMI ≥ 30". Alles wat per aandachtspunt verschilt (definitie, zoekwoorden, rekenregel) staat in een apart
definitiebestand, niet in de code. De definities zijn
opgesteld door de gynaecologen van het team, op basis van landelijke richtlijnen en de protocollen van het Spaarne
Gasthuis.

Per aandachtspunt:

1. **Python-laag en poorten.** Eerst leest Python vaste waarden uit de kaart: BMI, leeftijd op de à terme datum,
   pariteit (G/P-notatie), rhesus D en c, HIV, HBsAg, Hb, ferritine, trombocyten en het interval sinds de vorige
   bevalling. Labwaarden en BMI tellen alleen uit de huidige zwangerschap; grenswaarden uit protocolteksten
   ("BMI > 35") tellen niet als meting. Geven meerdere metingen verschillende uitkomsten, of is een waarde niet zeker
   te bepalen, dan gebruikt Python hem niet. Daarna per aandachtspunt, volgens regels in het definitiebestand:
   - **AP gevuld met een gevonden waarde.** Hangt het aandachtspunt van één meetbare waarde af (bijvoorbeeld
     maternale leeftijd > 40 jaar), dan beslist Python. Er komt geen taalmodel aan te pas; de passage is de
     letterlijke regel uit de kaart.
   - **Poort dicht: het AP hoeft niet gecontroleerd te worden.** Bijvoorbeeld "bariatrische chirurgie bij BMI ≥ 40" is
     niet relevant bij een BMI van 22. Een poort gaat alleen dicht als Python de waarde zeker weet.
   - **Poort open: het AP wordt gecontroleerd door het taalmodel.** Bij twijfel altijd deze kant op.
   - **Python-factor.** Bij samengestelde aandachtspunten (risicofactoren) voegt Python meetbare factoren toe als
     letterlijke passage, bijvoorbeeld nullipariteit (para 0), leeftijd ≥ 40 of BMI > 35 bij de risicofactoren voor
     pre-eclampsie. Python voegt alleen toe en haalt nooit iets weg.
2. **Focuspassages.** Kaartregels met een van de zoekwoorden van het aandachtspunt. Ze dienen als hint voor het model
   en als extra kandidaten, zodat een korte regel als "Zorgpad sectio ia" niet gemist wordt.
3. **Call 1.** Het model leest de hele kaart en geeft letterlijke citaten uit de zwangerenkaart terug, elk met een korte
   argumentatie (maximaal vier per aandachtspunt).
4. **Harde controle.** Elk citaat wordt teruggezocht in de kaarttekst. Kleine verschillen in hoofdletters, leestekens
   en regelafbrekingen zijn toegestaan; wat niet in de kaart te vinden is, valt weg. Vanaf hier wordt altijd de echte
   kaarttekst gebruikt, nooit de tekst zoals het model hem schreef.
5. **Python-filter.** Ontkenningen ("rookt niet"), lege velden, kale labkoppen zonder uitslag en passages over partner
   of familie vallen weg, behalve bij aandachtspunten waar de familieanamnese meetelt. Familie van de partner valt
   altijd weg.
6. **Call 2.** Per overgebleven quote gaat het systeem na of die aannemelijk bijdraagt aan het aandachtspunt. Het
   stelt die vraag aan het model en bepaalt uit de logprobs de kans op *ja* tegenover *nee*. De drempel voor die kans
   staat bewust laag, zodat de sensitiviteit hoog blijft: alleen quotes die duidelijk niet relevant zijn, worden
   weggefilterd. Bij samengestelde aandachtspunten (zoals risicofactoren voor pre-eclampsie) is de vraag of de quote een
   risicofactor is. Elke quote krijgt context mee: bij een kort citaat de zin eromheen, de regel erboven en de
   dichtstbijzijnde datum. De vraag noemt ook het begin van de huidige zwangerschap, zodat het model een brief over een
   eerdere bevalling herkent, en de waarden die Python zeker uit de kaart haalde (BMI, leeftijd, pariteit,
   interval), zodat het model een grens in de definitie ("BMI > 35", "≥ 40 jaar") niet zelf hoeft te toetsen. Die
   waarden staan alleen in de vraag aan het model, nooit in het rapport.
7. **Rapport.** Per categorie een tabel met één regel per aandachtspunt waarvoor passages zijn gevonden. In de tabel
   staan de twee belangrijkste quotes, letterlijk uit de kaart; zijn er meer, dan staat erbij hoeveel. Bijna gelijke
   passages staan er één keer in. In een bijlage staan per aandachtspunt alle passages als hele zin uit de kaart,
   belangrijkste eerst. De kans uit call 2 bepaalt alleen de volgorde en staat nergens in het rapport.

### De drempel

De drempel van call 2 is zo ingesteld dat op de ontwikkelset minstens 95% van de aandachtspunten die volgens de experts
van toepassing waren, passages kreeg. Een gemist aandachtspunt weegt zwaarder dan een passage te veel; de drempel ligt
daarom laag. De kans wordt alleen intern gebruikt om te filteren. Hij staat niet in het rapport en wordt niet aan de
zorgverlener getoond. De drempel ligt vast per versie en wordt elk kwartaal gecontroleerd op een steekproef (zie
[§14 van het validatieprotocol](validatieprotocol.html)).

## Ontwerpkeuzes

**Recall eerst.** Het systeem is afgesteld op het vinden van zoveel mogelijk relevante passages. Een passage te veel kost
de zorgverlener een paar seconden; een gemist aandachtspunt kan klinisch relevant zijn.

**Deterministisch waar het kan.** We hebben de voorkeur voor een deterministische methode. Een waarde als de BMI wordt
met zoekfuncties uit de kaart gehaald en met een vaste regel getoetst; daarvoor gebruiken we geen taalmodel.

**Alleen echte kaarttekst.** Doordat elk citaat wordt teruggezocht en daarna de kaarttekst zelf wordt gebruikt, kan het
rapport geen tekst bevatten die niet in de kaart staat.

## Model en instellingen

- MedGemma 27B (Google), lokaal via Ollama of vLLM. Kwantisatie en model-digest per versie in [Versies](versies.html).
- Temperatuur 0 en vaste instellingen: het model kiest steeds het meest waarschijnlijke antwoord, zodat dezelfde kaart
  met dezelfde versie dezelfde uitkomst geeft. Dat controleren we in de validatie met een herhaalde run.
- Eerst alle calls 1, dan alle calls 2: elke fase heeft één vaste systeemprompt met de kaart, die in de cache van het
  model blijft. Dat maakt de verwerking sneller.
- Raakt het model in een herhalingslus, dan wordt het antwoord afgebroken.

## Herleidbaarheid

Elke uitvoer bevat:

- **code:** de commit waaruit de software gebouwd is;
- **config-hash:** een hash over de code van de aandachtspunten, de prompts, de definities, de vragenlijst, de drempel
  en het model. Eén letter verschil geeft een andere hash;
- **kaart-hash:** om de invoer te herkennen zonder de kaart zelf op te slaan.

Zo is van elk resultaat na te gaan met welke versie het gemaakt is.

## Zelf narekenen

```
python3 tools/analyse.py <map met *_results.json> docs/resultaten/gouden_standaard_ontwikkelset.csv -o analyse.html
```

Het analysescript en de gouden standaard (kaartnummer, aandachtspunt, 0/1) staan in deze repository. Met de
resultaatbestanden van een run, die reviewers op aanvraag kunnen krijgen (zonder kaarttekst), berekent het script recall (met Wilson-interval en een bootstrap per kaart), PPV, fout-positieven en aandachtspunten per
kaart, en tekent de ROC- en PR-curve. Zonder de optie `--met-passages` staat er geen kaarttekst in de uitvoer.
