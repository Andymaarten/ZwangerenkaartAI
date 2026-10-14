"""Validatie-analyse: van een map met *_results.json en een gouden standaard naar één HTML-pagina.

  python3 tools/analyse.py <map met results> <gouden_standaard.csv> [-o analyse.html] [--met-passages]

De gouden standaard is een CSV `kaart;AP;juist` (1 = aandachtspunt van toepassing). Het kaartnummer van een
resultatenbestand is het eerste getal in de bestandsnaam (Kaart_007_results.json -> 7).

Zonder --met-passages staat er geen kaarttekst in de pagina: alleen AP-nummers, scores en tellingen. Die pagina mag
gedeeld worden. Met --met-passages komen per AP de passages met hun kans erbij (patiëntgegevens: alleen lokaal), en
ook een passages.csv naast de HTML.

Score per AP (voor de curves): Python-AP 1 of 0; model-AP de hoogste P(ja) over zijn passages (een passage zonder kans
telt als 1, want die blijft in het rapport staan); geen passages = 0. Een AP staat in het rapport bij score >= drempel.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any, Dict

UITGESLOTEN = {"AP079"}          # kwetsbaarheden: apart beoordeeld (validatieplan)


def gouden_standaard(pad: Path) -> Dict[tuple, int]:
    with open(pad, encoding="utf-8-sig") as f:
        return {(int(r["kaart"]), r["AP"].strip()): int(r["juist"]) for r in csv.DictReader(f, delimiter=";")
                if r.get("juist", "").strip() in ("0", "1")}


def score(ap: Dict[str, Any]) -> float:
    if ap.get("modus") == "python" or "kandidaten" not in ap:      # oudere runs zonder call 2: passage = 1
        return 1.0 if ap.get("passages") else 0.0
    kansen = [1.0 if p.get("kans") is None else p["kans"] for p in ap.get("kandidaten") or []]
    return max(kansen, default=0.0)


def lees(map_: Path, gs: Dict[tuple, int], met_passages: bool) -> Dict[str, Any]:
    kaarten, versies, passages, drempels = [], {}, [], set()
    paden = (sorted(map_.rglob("*_results.json"))
             or sorted(p for p in map_.rglob("kaart_*.json") if re.fullmatch(r"kaart_\d+", p.stem)))
    for pad in paden:
        m = re.search(r"(\d+)", pad.stem)
        if not m:
            continue
        k, d = int(m.group(1)), json.loads(pad.read_text(encoding="utf-8"))
        meta = d.get("meta") or {}
        versies.setdefault(meta.get("config-hash", "?"), []).append(k)
        if meta.get("drempel") is not None:
            drempels.add(str(meta["drempel"]))
        aps, massa_laag, zonder_kans = [], 0, 0
        for a in d.get("aps", []):
            e = gs.get((k, a["id"]))
            for p in a.get("kandidaten") or []:
                zonder_kans += p.get("kans") is None
                massa_laag += p.get("kans") is not None and p.get("massa", 1.0) < 0.9
                passages.append({"kaart": k, "AP": a["id"], "juist": "" if e is None else e, "bron": p.get("bron", ""),
                                 "kans": p.get("kans"), "massa": p.get("massa"), "logodds": p.get("logodds"),
                                 **({"tekst": p.get("tekst", "")} if met_passages
                                    else {"tekens": len(p.get("tekst", ""))})})
            if e is None or a["id"] in UITGESLOTEN:
                continue
            rij = {"id": a["id"], "label": a.get("label", ""), "cat": a.get("categorie", ""), "modus": a.get("modus"),
                   "s": round(score(a), 4), "y": e, "kand": len(a.get("kandidaten") or a.get("passages") or [])}
            if met_passages:
                rij["p"] = [[p.get("tekst", ""), p.get("kans")]
                            for p in (a.get("kandidaten") or a.get("passages") or [])]
            aps.append(rij)
        kaarten.append({"k": k, "aps": aps, "duur": meta.get("duur_sec") or d.get("duur_sec"),
                        "massa_laag": massa_laag, "zonder_kans": zonder_kans,
                        "fout": [a["id"] for a in d.get("aps", []) if a.get("fout")]})
    return {"kaarten": kaarten, "versies": versies, "passages": passages, "drempel_meta": sorted(drempels)}


def schrijf(data: Dict[str, Any], uit: Path, met_passages: bool) -> None:
    sjabloon = (Path(__file__).parent / "analyse_sjabloon.html").read_text(encoding="utf-8")
    payload = {k: v for k, v in data.items() if k != "passages"}
    pagina = sjabloon.replace("/*DATA*/null", json.dumps(payload, ensure_ascii=False)) \
                     .replace("<!--WAARSCHUWING-->", '<p class="let-op">Bevat passages uit de kaarten '
                              '(patiëntgegevens). Alleen lokaal bekijken, niet delen.</p>' if met_passages else "")
    uit.write_text(pagina, encoding="utf-8")
    if met_passages:
        with open(uit.with_name("passages.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data["passages"][0]) if data["passages"] else ["kaart"],
                               delimiter=";")
            w.writeheader(); w.writerows(data["passages"])


def bijwerken(map_: Path, gs_pad: Path, uit: Path) -> str:
    """Voor de pijplijn: na elke kaart de analyse over alle resultaten opnieuw, zonder passages. Geeft een samenvatting."""
    data = lees(map_, gouden_standaard(gs_pad), False)
    schrijf(data, uit, False)
    rijen = [r for k in data["kaarten"] for r in k["aps"]]
    pos = [r for r in rijen if r["y"]]
    drempel = float((data["drempel_meta"] or ["0.3"])[0])
    tp = sum(r["s"] >= drempel for r in pos)
    fp = sum(r["s"] >= drempel for r in rijen if not r["y"])
    return (f"{len(data['kaarten'])} kaarten met gouden standaard · recall {tp}/{len(pos)} · "
            f"PPV {tp}/{tp + fp} · drempel {drempel}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("map", type=Path); ap.add_argument("gouden_standaard", type=Path)
    ap.add_argument("-o", "--uit", type=Path, default=Path("analyse.html"))
    ap.add_argument("--met-passages", action="store_true")
    a = ap.parse_args()
    data = lees(a.map, gouden_standaard(a.gouden_standaard), a.met_passages)
    if not data["kaarten"]:
        raise SystemExit(f"geen resultaten gevonden in {a.map}")
    schrijf(data, a.uit, a.met_passages)
    n_pos = sum(r["y"] for k in data["kaarten"] for r in k["aps"])
    print(f"{len(data['kaarten'])} kaarten, {n_pos} positieve AP's -> {a.uit}"
          + (f" (+ {a.uit.with_name('passages.csv')})" if a.met_passages else ""))
    if len(data["versies"]) > 1:
        print("LET OP: meer dan één config-hash:", {h: sorted(ks) for h, ks in data["versies"].items()})


if __name__ == "__main__":
    main()
