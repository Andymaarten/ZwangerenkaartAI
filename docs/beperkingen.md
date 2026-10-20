---
title: Beperkingen
---

# Beperkingen

Elke beperking staat hieronder met wat we eraan doen.

**Eén ziekenhuis.** Alle kaarten in de ontwikkel- en validatieset komen uit het Spaarne Gasthuis, als verwijzing uit de
eerste lijn in de regio. Het systeem zet elke kaart om naar platte tekst, zodat de opmaak van een kaart mag verschillen.
De meest gangbare kaartformaten in Nederland zijn getest. Kaarten uit andere regio's kunnen andere afkortingen bevatten;
die zijn als zoekwoorden toe te voegen zonder de code te wijzigen.

**De gouden standaard is een oordeel.** Experts kunnen een aandachtspunt verschillend interpreteren, en de gouden
standaard komt tot stand na inzage van het systeem en het zorgplan. Daarom beoordelen twee gynaecologen elke kaart eerst
onafhankelijk en blind, wordt hun overeenstemming gerapporteerd, staat de recall tegen dat blinde oordeel apart, krijgt
elke wijziging na inzage een reden, en controleert een derde gynaecoloog de toegevoegde aandachtspunten blind. Correcties in de gouden standaard zijn in het bestand gemarkeerd met de oorspronkelijke waarde.

**Zeldzame aandachtspunten.** Een hoge recall over alle aandachtspunten samen sluit een fout bij een zelden voorkomend
aandachtspunt niet uit; per aandachtspunt zijn de aantallen te klein voor een eigen schatting. Daarom wordt elke misser
afzonderlijk beschreven en geanalyseerd, en lopen de kwartaalsteekproeven na ingebruikname door, zodat ook zeldzame
aandachtspunten in de loop van de tijd vaker getoetst worden.

**Kaarten zonder tekst.** Een kaart die alleen als afbeelding is gescand, levert geen tekst op en kan niet worden
verwerkt. De meeste verwijzingen komen tegenwoordig digitaal binnen in Epic; het systeem meldt het als een kaart geen
tekst bevat, en die kaart gaat dan via de gewone werkwijze.

**Definities veranderen.** De definities van de aandachtspunten volgen landelijke richtlijnen en de protocollen van
het Spaarne Gasthuis, en moeten mee als een richtlijn wordt herzien. Daarom staan ze in een aparte repository, los van de code. Verandert een
definitie, dan draaien we de ontwikkelset en de validatieset opnieuw en controleren we dat het aandachtspunt geen
positieven verliest. Beide sets blijven daarvoor beschikbaar.

**Het zorgplan als vergelijking.** Het zorgplan legt vast wat de zorgverlener heeft opgeschreven, niet alles wat die
heeft gezien of gewogen. We gebruiken daarom steeds dezelfde notitie (de eerste zorgplannotitie na verwijzing), laten
die coderen door een onderzoeker die los staat van de experts, en rapporteren zorgplanpunten die niet uit de kaart komen
apart.
