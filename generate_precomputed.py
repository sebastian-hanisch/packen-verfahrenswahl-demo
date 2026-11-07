"""Erzeugt pvw_precomputed.json: das Messraster der Karte (vier Bereiche: 1D, 2D, 3D, 3D mit Stützfläche; je vier Verteilungen × drei oder vier Teilezahlen × 100 beziehungsweise 200 feste Instanzen ×
alle Verfahren des Bereichs) und die Stichprobe (die ersten Instanzen jeder Zelle einzeln, für die Tests).

    python generate_precomputed.py                         # rechnet alles neu (mehrere Prozesse)
    python generate_precomputed.py --nur-stichprobe        # ergänzt in der vorhandenen Datei nur die Stichprobe
    python generate_precomputed.py --check                 # rechnet das Raster (parallel) nach und vergleicht mit der Datei

Es gibt kein Optimum im Raster: Der Maßstab ist die Schranke (1D L2, 2D Fläche und große Rechtecke, 3D Volumen und große Quader). Die Summen sind ganze Zahlen."""

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import pvw_constants as C
import pvw_evaluation as ev


def _alle_zellen():
    return [(b, v, ni) for b in ev.BEREICHE for v, ni in ev.zellen_von(b)]


def _zelle(args):
    b, v, ni = args
    t = time.perf_counter()
    return b, v, ni, ev.messzelle(b, v, ni), time.perf_counter() - t


def _stichprobe_zelle(args):
    b, v, ni = args
    return ev.zelle_schluessel(b, v, ni), {str(j): ev.messzelle(b, v, ni, [j]) for j in C.STICHPROBE_J}


def _frisch(args):
    b, v, ni = args
    return ev.zelle_schluessel(b, v, ni), ev.messzelle(b, v, ni)


def _pool():
    return ProcessPoolExecutor(max(1, min(6, (os.cpu_count() or 2) // 2)))


def stichprobe_ergaenzen(daten: dict) -> None:
    with _pool() as pool:
        daten["stichprobe"] = dict(pool.map(_stichprobe_zelle, _alle_zellen()))


def erzeugen() -> dict:
    daten = {"zellen": {}}
    zellen = sorted(_alle_zellen(), key=lambda z: -(C.MESS_N[z[0]][z[2]] * (200 if z[0] == C.ZWEI else 1)))      # die langsamen Zellen zuerst
    with _pool() as pool:
        for b, v, ni, z, sekunden in pool.map(_zelle, zellen):
            daten["zellen"][ev.zelle_schluessel(b, v, ni)] = z
            print(f"{ev.zelle_schluessel(b, v, ni)}: {sekunden:.0f} s", flush=True)
    daten["zellen"] = {ev.zelle_schluessel(b, v, ni): daten["zellen"][ev.zelle_schluessel(b, v, ni)] for b, v, ni in _alle_zellen()}
    stichprobe_ergaenzen(daten)
    return daten


def schreiben(daten: dict) -> None:
    ev.PRECOMPUTED.write_text(json.dumps(daten, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("geschrieben:", ev.PRECOMPUTED.name)


def pruefen() -> int:
    gespeichert = ev.vorberechnet()
    schlecht = 0
    with _pool() as pool:
        for schl, frisch in pool.map(_frisch, _alle_zellen()):
            if frisch != gespeichert["zellen"][schl]:
                schlecht += 1
                print("ABWEICHUNG", schl, flush=True)
    print("gleich" if not schlecht else f"{schlecht} Abweichungen")
    return 1 if schlecht else 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(pruefen())
    if "--nur-stichprobe" in sys.argv:
        d = json.loads(ev.PRECOMPUTED.read_text(encoding="utf-8"))
        stichprobe_ergaenzen(d)
        schreiben(d)
        sys.exit(0)
    schreiben(erzeugen())
