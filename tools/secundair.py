"""Secundaire uitkomsten van het validatieprotocol (§5 primair ter vergelijking, §6.1-6.9, §4.4, §7, §8-tabel).

  python3 tools/secundair.py <map> -o secundair.md [--teksten <map met Kaart_0xx.txt>]

<map> bevat (alle CSV's: kaart;AP;juist, scheidingsteken ';'):
  E0_A.csv, E0_B.csv   losse blinde scores van beoordelaar A en B
  E0.csv               consensus (blind)
  ZP.csv               gecodeerd zorgplan
  E1.csv               gouden standaard na inzage; optioneel kolommen 'aanleiding' en 'reden' bij wijzigingen
  bevestiging.csv      blinde derde beoordelaar (§4.4), optioneel
  antwoorden/          *_results.json van de validatierun; M = 1 als het rapport passages toont
juist: alleen 1 of 0, nooit leeg. E0_A, E0_B, E0 en E1 bevatten elke kaart en elk AP van de run; ZP mag een hele
kaart missen (geen zorgplannotitie); bevestiging.csv bevat alleen de voorgelegde regels. AP079 telt nooit mee.
Uitvoer bevat geen kaarttekst: alleen aantallen, kaartnummers en AP's.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ZAAD, HERHAAL = 7, 2000


def lees_csv(pad: Path, extra=()):
    """{(kaart, AP): 0 of 1}; plus de extra kolommen per sleutel. Stopt bij elke andere waarde."""
    if not pad.exists():
        return {}, {}
    uit, info = {}, {}
    with open(pad, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter=";"):
            k, ap, j = int(r["kaart"]), r["AP"].strip(), (r.get("juist") or "").strip()
            if j not in ("0", "1"):
                raise SystemExit(f"{pad.name}: kaart {k:03d} {ap} heeft '{j}', alleen 1 of 0 is toegestaan")
            if ap == "AP079":
                continue
            uit[(k, ap)] = int(j)
            info[(k, ap)] = {e: (r.get(e) or "").strip() for e in extra}
    return uit, info


def lees_m(map_: Path):
    """M per (kaart, AP) = passages in het rapport; plus categorie per AP en de passages (voor §7)."""
    m, cat, passages = {}, {}, {}
    for pad in sorted(map_.glob("*_results*.json")):
        k = int(re.search(r"Kaart_0*(\d+)", pad.name).group(1))
        for a in json.loads(pad.read_text(encoding="utf-8"))["aps"]:
            if a["id"] == "AP079":
                continue
            m[(k, a["id"])] = int(bool(a.get("passages")))
            cat[a["id"]] = a.get("categorie", "")
            passages[(k, a["id"])] = [p["tekst"] for p in a.get("passages") or [] if isinstance(p, dict)]
    return m, cat, passages


def paren(*bronnen):
    """Sleutels die in alle bronnen voorkomen."""
    return sorted(set.intersection(*(set(b) for b in bronnen)))


def volledig(naam, d, m, hele_kaarten_mogen_ontbreken=False):
    """Stopt als een (kaart, AP) van de run ontbreekt; bij ZP mag een hele kaart ontbreken."""
    kaarten = {k for k, _ in d} if hele_kaarten_mogen_ontbreken else {k for k, _ in m}
    mist = sorted(s for s in m if s[0] in kaarten and s not in d)
    if mist:
        raise SystemExit(f"{naam}: {len(mist)} regels ontbreken, bijv. " + ", ".join(f"{k:03d} {ap}" for k, ap in mist[:5]))


def tel(ref, test, sleutels):
    c = Counter((ref[s], test[s]) for s in sleutels)
    return c[(1, 1)], c[(0, 1)], c[(1, 0)], c[(0, 0)]              # tp, fp, fn, tn


def recall(ref, test, s):
    tp, fp, fn, tn = tel(ref, test, s)
    return tp / (tp + fn) if tp + fn else float("nan")


def precisie(ref, test, s):
    tp, fp, fn, tn = tel(ref, test, s)
    return tp / (tp + fp) if tp + fp else float("nan")


def pos_agreement(a, b, s):
    tp, fp, fn, tn = tel(a, b, s)
    return 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else float("nan")


def kappa(a, b, s):
    tp, fp, fn, tn = tel(a, b, s)
    n = tp + fp + fn + tn
    if not n:
        return float("nan")
    po = (tp + tn) / n
    pe = ((tp + fn) * (tp + fp) + (tn + fp) * (tn + fn)) / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def bootstrap(maat, sleutels):
    """95%-interval met cluster-bootstrap per kaart (§5): trek kaarten met teruglegging."""
    per_kaart = defaultdict(list)
    for s in sleutels:
        per_kaart[s[0]].append(s)
    kaarten, rng, waarden = sorted(per_kaart), random.Random(ZAAD), []
    for _ in range(HERHAAL):
        trek = [s for k in rng.choices(kaarten, k=len(kaarten)) for s in per_kaart[k]]
        w = maat(trek)
        if w == w:                                                    # nan overslaan
            waarden.append(w)
    waarden.sort()
    if not waarden:
        return float("nan"), float("nan")
    return waarden[int(0.025 * len(waarden))], waarden[min(len(waarden) - 1, int(0.975 * len(waarden)))]


def pct(x):
    return "–" if x != x else f"{100 * x:.1f}%"


def r2(x):
    return "–" if x != x else f"{x:.2f}"


def met_interval(maat, s, fmt=pct):
    lo, hi = bootstrap(maat, s)
    return f"{fmt(maat(s))} ({fmt(lo)}–{fmt(hi)})"


def letterlijk(passages, teksten: Path):
    """§7: elke getoonde passage moet in de kaarttekst staan (witruimte genormaliseerd)."""
    norm = lambda t: re.sub(r"\s+", " ", t).strip().lower()
    goed, fout = 0, []
    for (k, ap), ps in passages.items():
        pad = teksten / f"Kaart_{k:03d}.txt"
        if not pad.exists():
            continue
        tekst = norm(pad.read_text(encoding="utf-8", errors="ignore"))
        for p in ps:
            if norm(p) in tekst:
                goed += 1
            else:
                fout.append((k, ap))
    return goed, fout


def rapport(map_: Path, teksten: Path | None = None) -> str:
    a, _ = lees_csv(map_ / "E0_A.csv")
    b, _ = lees_csv(map_ / "E0_B.csv")
    e0, _ = lees_csv(map_ / "E0.csv")
    zp, _ = lees_csv(map_ / "ZP.csv")
    e1, info = lees_csv(map_ / "E1.csv", ("aanleiding", "reden"))
    bev, _ = lees_csv(map_ / "bevestiging.csv")
    m, cat, passages = lees_m(map_ / "antwoorden")
    for naam, d in (("E0_A.csv", a), ("E0_B.csv", b), ("E0.csv", e0), ("E1.csv", e1)):
        volledig(naam, d, m)
    volledig("ZP.csv", zp, m, hele_kaarten_mogen_ontbreken=True)
    kaarten = sorted({k for k, _ in m})
    r = [f"# Secundaire uitkomsten ({len(kaarten)} kaarten)", "",
         "Intervallen: 95%, cluster-bootstrap per kaart (2000×, zaad 7). AP079 telt niet mee.", ""]

    s1, s0 = paren(e1, m), paren(e0, m)
    r += ["## Systeem tegenover de referentie (§5, §6.1, §6.8)", "",
          "| | tegen E1 | tegen E0 |", "|---|---|---|",
          f"| recall | {met_interval(lambda s: recall(e1, m, s), s1)} | {met_interval(lambda s: recall(e0, m, s), s0)} |",
          f"| PPV | {met_interval(lambda s: precisie(e1, m, s), s1)} | {met_interval(lambda s: precisie(e0, m, s), s0)} |",
          f"| fout-positieven per kaart | {r2(tel(e1, m, s1)[1] / max(1, len(kaarten)))} | "
          f"{r2(tel(e0, m, s0)[1] / max(1, len(kaarten)))} |", ""]

    sab = paren(a, b)
    r += ["## Overeenstemming beoordelaars bij E0 (§6.2)", "",
          "| | n | positive agreement | kappa |", "|---|---|---|---|",
          f"| alle AP's | {len(sab)} | {met_interval(lambda s: pos_agreement(a, b, s), sab)} | "
          f"{met_interval(lambda s: kappa(a, b, s), sab, r2)} |"]
    for c in sorted({cat.get(ap, '') for _, ap in sab}):
        sc = [s for s in sab if cat.get(s[1], "") == c]
        r.append(f"| {c or '(onbekend)'} | {len(sc)} | {pct(pos_agreement(a, b, sc))} | {r2(kappa(a, b, sc))} |")
    r.append("")

    r += ["## Zorgplan tegenover de expert (§6.3)", "", "| referentie | recall ZP | precisie ZP | positive agreement | kappa |",
          "|---|---|---|---|---|"]
    for naam, ref in (("E0", e0), ("E1", e1)):
        s = paren(ref, zp)
        r.append(f"| {naam} | {met_interval(lambda x: recall(ref, zp, x), s)} | {pct(precisie(ref, zp, s))} | "
                 f"{pct(pos_agreement(ref, zp, s))} | {r2(kappa(ref, zp, s))} |")
    r.append("")

    s_alle = paren(e0, e1, m)
    extra = [s for s in s_alle if e0[s] == 0 and m[s] == 1 and e1[s] == 1]
    extra_zp0 = [s for s in extra if zp.get(s) == 0]
    omgekeerd = [s for s in paren(e0, e1) if e0[s] == 1 and e1[s] == 0]
    toegevoegd = [s for s in paren(e0, e1) if e0[s] == 0 and e1[s] == 1]
    bevestigd = [s for s in toegevoegd if bev.get(s) == 1]
    per_kaart_n = len(s_alle) / max(1, len({k for k, _ in s_alle}))     # AP's per kaart; trekking kan kaarten herhalen
    per100 = lambda sel: lambda trek: 100 * sum(1 for t in trek if t in sel) / max(1e-9, len(trek) / per_kaart_n)
    r += ["## Wijzigingen van E0 naar E1 (§6.4, §6.5, §4.4)", "",
          f"- Aanvullende signalering (E0 = 0, M = 1, E1 = 1): **{len(extra)}**, per 100 kaarten "
          f"{met_interval(per100(set(extra)), s_alle, r2)}; waarvan ook ZP = 0: **{len(extra_zp0)}**, per 100 kaarten "
          f"{met_interval(per100(set(extra_zp0)), s_alle, r2)}.",
          f"- Toegevoegd in E1 (E0 = 0, E1 = 1): {len(toegevoegd)}; blind bevestigd door de derde beoordelaar: "
          f"{len(bevestigd)} van {sum(1 for s in toegevoegd if s in bev)} voorgelegd "
          f"({pct(len(bevestigd) / max(1, sum(1 for s in toegevoegd if s in bev)))}).",
          f"- Omgekeerd (E0 = 1, E1 = 0): {len(omgekeerd)} — " + ", ".join(f"k{k:03d} {ap}" for k, ap in omgekeerd), ""]
    wijz = [s for s in paren(e0, e1) if e0[s] != e1[s]]
    if wijz:
        r += ["| aanleiding | reden | aantal |", "|---|---|---|"]
        for (aanl, red), n in Counter((info.get(s, {}).get("aanleiding", "") or "–", info.get(s, {}).get("reden", "") or "–")
                                      for s in wijz).most_common():
            r.append(f"| {aanl} | {red} | {n} |")
        r.append("")

    r += ["## Systeem en zorgplan, gepaard (§6.6, §6.7)", "", "| referentie | recall M | recall ZP | verschil M − ZP |",
          "|---|---|---|---|"]
    for naam, ref in (("E1", e1), ("E0", e0)):
        s = paren(ref, m, zp)
        r.append(f"| {naam} | {pct(recall(ref, m, s))} | {pct(recall(ref, zp, s))} | "
                 f"{met_interval(lambda x: recall(ref, m, x) - recall(ref, zp, x), s)} |")
    s = paren(e1, m, zp)
    pos = [x for x in s if e1[x] == 1]
    r += ["", f"- E1-positieven in ZP of M: {pct(sum(1 for x in pos if zp[x] or m[x]) / max(1, len(pos)))} "
              f"({sum(1 for x in pos if zp[x] or m[x])}/{len(pos)}); door beide gemist: "
              f"{sum(1 for x in pos if not zp[x] and not m[x])}.", ""]

    per_k = defaultdict(list)
    for x in s:
        per_k[x[0]].append(x)
    alles = sum(1 for k, xs in per_k.items() if all(m[x] for x in xs if e1[x] == 1))
    signaal = sum(1 for k, xs in per_k.items() if any(e1[x] == 1 and zp[x] == 0 and m[x] == 1 for x in xs))
    n_k = max(1, len(per_k))
    r += ["## Per kaart (§6.9)", "",
          f"- Alle E1-positieven gevonden: {pct(alles / n_k)} ({alles}/{len(per_k)}); minstens één misser: "
          f"{pct((len(per_k) - alles) / n_k)}.",
          f"- Systeem toonde een AP dat in het zorgplan ontbrak en in E1 bevestigd is: {pct(signaal / n_k)} "
          f"({signaal}/{len(per_k)}).", ""]

    acht = Counter((e1[x], zp[x], m[x]) for x in s)
    betekenis = {(1, 1, 1): "beide gevonden", (1, 0, 1): "systeem vond wat het zorgplan miste",
                 (1, 1, 0): "zorgplan vond wat het systeem miste", (1, 0, 0): "beide gemist",
                 (0, 0, 1): "fout-positief systeem", (0, 1, 0): "zorgplanpunt dat de experts niet uit de kaart halen",
                 (0, 1, 1): "beide fout-positief", (0, 0, 0): "terecht negatief"}
    r += ["## Indeling E1 · ZP · M (§8)", "", "| E1 | ZP | M | betekenis | aantal |", "|---|---|---|---|---|"]
    r += [f"| {e} | {z} | {mm} | {t} | {acht[(e, z, mm)]} |" for (e, z, mm), t in betekenis.items()]
    r.append("")

    if teksten:
        goed, fout = letterlijk(passages, teksten)
        r += ["## Letterlijkheid (§7)", "", f"- {goed} van {goed + len(fout)} getoonde passages letterlijk in de kaarttekst "
              f"({pct(goed / max(1, goed + len(fout)))}). Afwijkend: " + (", ".join(f"k{k:03d} {ap}" for k, ap in fout) or "geen"), ""]
    return "\n".join(r) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("map", type=Path)
    ap.add_argument("-o", "--uit", type=Path, default=Path("secundair.md"))
    ap.add_argument("--teksten", type=Path)
    a = ap.parse_args()
    a.uit.write_text(rapport(a.map, a.teksten), encoding="utf-8")
    print(f"-> {a.uit}")


if __name__ == "__main__":
    main()
