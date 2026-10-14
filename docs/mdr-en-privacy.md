---
title: MDR en privacy
---

# MDR en privacy

## Beoogd gebruik

ZwangerenkaartAI zet een verloskundige zwangerenkaart om in een overzicht voor de zorgverlener die het zorgplan opstelt:
patiëntgegevens, medische gegevens en 88 aandachtspunten, elk met de letterlijke passages uit de kaart die erover gaan.

- **Gebruikers:** gynaecologen, arts-assistenten, physician assistants en klinisch verloskundigen van de afdeling Verloskunde en Gynaecologie
  van het Spaarne Gasthuis.
- **Patiënten:** zwangeren die vanuit de eerste lijn naar het ziekenhuis zijn verwezen.
- **Moment:** bij de voorbereiding van het eerste consult na verwijzing.

## Wat het systeem niet doet

- Het stelt geen diagnose en geeft geen risicoscore, advies of behandelvoorstel.
- Het geeft per aandachtspunt geen ja of nee.
- Het vervangt de zwangerenkaart en het oordeel van de zorgverlener niet. Het rapport zegt dat ook, bovenaan.
- Het ziet alleen wat in de kaart staat. Wat er niet in staat, kan het niet vinden.

## Classificatie

ZwangerenkaartAI is software die het Spaarne Gasthuis zelf ontwikkelt en alleen binnen het eigen ziekenhuis gebruikt.
Het valt daarmee onder de regeling voor in-house hulpmiddelen van de Europese verordening medische hulpmiddelen (MDR,
artikel 5, lid 5). Onze beoordeling is dat het systeem in klasse I valt:

- het selecteert en toont tekst die al in de kaart staat, letterlijk en zonder interpretatie;
- het geeft geen oordeel, score of advies over de patiënt;
- de zorgverlener leest de passages en neemt elke beslissing zelf.

Intern gebruikt het systeem een kans om passages die niet bijdragen weg te filteren (zie [Methode](methode.html)).
Die kans wordt niet getoond en is geen uitspraak over de patiënt.

## Privacy

- **Lokaal.** Het taalmodel en de software draaien op servers van het Spaarne Gasthuis. Er gaan geen patiëntgegevens naar
  externe diensten of naar de ontwikkelaars van het model.
- **Geen geheugen.** Elke aanroep van het model staat op zichzelf. De cache van het model hergebruikt alleen een
  identiek begin van een vraag: binnen één kaart de kaarttekst, tussen kaarten alleen de vaste instructie.
- **Wat wordt bewaard.** Per kaart het rapport, de uitgelezen tekst en logbestanden, in de omgeving van het ziekenhuis,
  volgens het beleid van het Spaarne Gasthuis.
- **Deze repository** bevat geen patiëntgegevens. De gouden standaard bevat alleen kaartnummers, aandachtspunten en 0/1.

## Veiligheid

- Elke getoonde passage komt letterlijk uit de kaart; de code controleert dat bij elke passage.
- Elke uitvoer draagt de versie van de code, een hash van prompts en instellingen, en een hash van de kaart.
- De vragen en definities worden niet automatisch bijgewerkt; elke wijziging is een nieuwe versie, die eerst op een
  vaste testset wordt gecontroleerd.
- De werking wordt na ingebruikname doorlopend en per kwartaal gecontroleerd (zie
  [validatieprotocol, §14](validatieprotocol.html)).
