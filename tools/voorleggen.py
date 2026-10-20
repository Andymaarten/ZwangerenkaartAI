"""Stap E0 -> E1 van het validatieprotocol (§4.3): voorleglijst maken en de ingevulde lijst omzetten naar E1.csv.

  python3 voorleggen.py lijst <map> -o voorleglijst.csv
  python3 voorleggen.py e1 <map> --lijst voorleglijst.csv -o E1.csv

<map> bevat E0.csv, ZP.csv en antwoorden/ (de *_results.json van de validatierun), zoals bij secundair.py.

lijst: alle gevallen waarin E0 afwijkt van het systeem (M) of van het zorgplan (ZP), met de passages van het systeem.
       De experts vullen per regel E1 (1 of 0) in, en bij een wijziging aanleiding en reden.
       Bevat passages uit de kaart: alleen lokaal, niet delen.
e1:    E1 = de ingevulde waarde voor elk voorgelegd geval, E0 voor alle andere regels. Stopt bij een lege of ongeldige
       waarde, of bij een wijziging zonder aanleiding of reden.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from secundair import lees_csv, lees_m

AANLEIDING = {"systeem", "zorgplan", "beide", "eigen herlezing"}
REDEN = {"a", "b", "c", "d"}
KOP = ["kaart", "AP", "label", "verschil", "E0", "M", "ZP", "passages", "E1", "aanleiding", "reden"]


def lees_rijen(pad: Path):
    with open(pad, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def schrijf(pad: Path, kop, rijen):
    with open(pad, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=kop, delimiter=";", lineterminator="\n")
        w.writeheader()
        w.writerows(rijen)


def lijst(map_: Path):
    e0, _ = lees_csv(map_ / "E0.csv")
    zp, _ = lees_csv(map_ / "ZP.csv")
    m, _, passages = lees_m(map_ / "antwoorden")
    labels = {(int(r["kaart"]), r["AP"].strip()): r.get("label", "") for r in lees_rijen(map_ / "E0.csv")}
    uit = []
    for s in sorted(e0):
        if s not in m:
            continue
        ander_m, ander_zp = e0[s] != m[s], s in zp and e0[s] != zp[s]
        if not (ander_m or ander_zp):
            continue
        uit.append({"kaart": f"{s[0]:03d}", "AP": s[1], "label": labels.get(s, ""),
                    "verschil": "beide" if ander_m and ander_zp else ("systeem" if ander_m else "zorgplan"),
                    "E0": e0[s], "M": m[s], "ZP": zp.get(s, "-"),   # '-' = kaart zonder zorgplannotitie
                    "passages": " | ".join(passages.get(s, [])), "E1": "", "aanleiding": "", "reden": ""})
    return uit


def e1(map_: Path, lijst_pad: Path):
    besluit, fouten = {}, []
    for r in lees_rijen(lijst_pad):
        s = (r["kaart"].strip().zfill(3), r["AP"].strip())
        w, aanl, red = r["E1"].strip(), r["aanleiding"].strip().lower(), r["reden"].strip().lower()
        if w not in ("0", "1"):
            fouten.append(f"{s[0]} {s[1]}: E1 is '{w}', alleen 1 of 0")
        elif w != r["E0"].strip() and (aanl not in AANLEIDING or red not in REDEN):
            fouten.append(f"{s[0]} {s[1]}: gewijzigd, maar aanleiding '{aanl}' of reden '{red}' ontbreekt of is ongeldig")
        besluit[s] = (w, aanl, red)
    if fouten:
        raise SystemExit("E1 niet gemaakt:\n" + "\n".join(fouten[:20]))
    uit = []
    for r in lees_rijen(map_ / "E0.csv"):
        s = (r["kaart"].strip().zfill(3), r["AP"].strip())
        w, aanl, red = besluit.get(s, (r["juist"].strip(), "", ""))
        uit.append({"kaart": s[0], "AP": s[1], "label": r.get("label", ""), "juist": w,
                    "aanleiding": aanl if w != r["juist"].strip() else "", "reden": red if w != r["juist"].strip() else ""})
    return uit


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("stap", choices=["lijst", "e1"])
    ap.add_argument("map", type=Path)
    ap.add_argument("--lijst", type=Path, default=Path("voorleglijst.csv"))
    ap.add_argument("-o", "--uit", type=Path, required=True)
    a = ap.parse_args()
    if a.stap == "lijst":
        rijen = lijst(a.map)
        schrijf(a.uit, KOP, rijen)
        print(f"{len(rijen)} gevallen voorleggen -> {a.uit} (bevat passages: alleen lokaal)")
    else:
        rijen = e1(a.map, a.lijst)
        schrijf(a.uit, ["kaart", "AP", "label", "juist", "aanleiding", "reden"], rijen)
        print(f"{sum(1 for r in rijen if r['aanleiding'])} wijzigingen ten opzichte van E0 -> {a.uit}")


if __name__ == "__main__":
    main()
