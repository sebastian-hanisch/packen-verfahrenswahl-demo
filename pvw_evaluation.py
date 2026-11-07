"""Kennzahlen, Verdikt-Logik und das Messraster (vorberechnet in pvw_precomputed.json, erzeugt von generate_precomputed.py)."""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pvw_algorithm as A
import pvw_constants as C
from pvw_scenario import Instance, mess_seed, quelle_instanz, such_seed, zufallsinstanz

PRECOMPUTED = Path(__file__).resolve().parent / "pvw_precomputed.json"
BEREICHE = tuple(sorted(C.BEREICHE))


@dataclass(frozen=True)
class Settings:
    bereich: int = 0
    quelle: int = 0
    n_index: int = 0
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    inst: Instance
    schranke: int
    zaehlungen: tuple     # Behälterzahl je Verfahren des Bereichs
    beste: tuple          # Nummern der Verfahren mit der kleinsten Behälterzahl
    optimum: object       # Optimum (int) beim Handbeispiel, sonst None
    empfehlung: tuple     # Nummern der Verfahren, die die Karte empfiehlt
    empfehlung_art: str   # "Zelle" (die Karte hat genau diese Zelle) oder "alle" (ein Verfahren für alles im Bereich)
    settings: Settings


def app_n(bereich: int, n_index: int) -> int:
    """Zahl der Teile der Zufallsinstanz in der App; ein zu großer Index wählt die größte Zahl des Bereichs."""
    werte = C.APP_N[bereich]
    return werte[max(0, min(n_index, len(werte) - 1))]


def schranke(inst: Instance) -> int:
    """Untere Schranke: 1D L2, 2D Flächenschranke und große Rechtecke, 3D Volumenschranke und große Quader."""
    if inst.bereich == C.EINS:
        return A.l2_1d(list(inst.teile), inst.cap)
    if inst.bereich == C.ZWEI:
        return A.schranken_2d(inst.teile, inst.cap)[2]
    return A.schranken_3d(inst.teile, inst.cap)[2]


def zaehle(inst: Instance, seed: int) -> tuple:
    """Behälterzahl aller Verfahren des Bereichs; `seed` ist der Instanzseed (die Tausch-Suche der 2D-Verfahren nimmt daraus ihre Startzahl)."""
    b = inst.bereich
    if b == C.EINS:
        return tuple(A.anzahl_1d(list(inst.teile), m, inst.cap) for m in range(len(C.VERFAHREN[b])))
    if b == C.ZWEI:
        return tuple(A.anzahl_2d(inst.teile, m, inst.cap, such_seed(seed)) for m in range(len(C.VERFAHREN[b])))
    return tuple(A.anzahl_3d(inst.teile, v, k, inst.cap, C.S_MIN[b]) for v, k in C.DREI_VERFAHREN[b])


def beste_verfahren(zaehlungen) -> tuple:
    kleinste = min(zaehlungen)
    return tuple(m for m, z in enumerate(zaehlungen) if z == kleinste)


def analyse(s: Settings) -> Analysis:
    inst = quelle_instanz(s.bereich, s.quelle, app_n(s.bereich, s.n_index), s.seed)
    z = zaehle(inst, s.seed)
    emp, art = empfehlung(s.bereich, s.quelle - 1 if s.quelle > 0 else None, inst.n)
    optimum = C.BEISPIEL_OPTIMUM[s.bereich] if s.quelle == 0 else None
    return Analysis(inst, schranke(inst), z, beste_verfahren(z), optimum, emp, art, s)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Messraster


def messzelle(bereich: int, verteilung: int, n_index: int, instanzen=None) -> dict:
    """Rechnet eine Zelle des Messrasters frisch: Summen (ganze Zahlen, damit der Vergleich exakt ist) über die Instanzen der Zelle (oder nur über die Nummern `instanzen`, so rechnen die Tests
    Stichproben nach). ueber[m] = Summe von (Behälter minus Schranke) des Verfahrens m; beste[m] = Zahl der Instanzen, in denen m (gegebenenfalls mit anderen) die kleinste Behälterzahl hat;
    regret[m] = Summe von (Behälter minus kleinste Behälterzahl aller Verfahren dieser Instanz)."""
    n = C.MESS_N[bereich][n_index]
    k = len(C.VERFAHREN[bereich])
    out = {"ueber": [0] * k, "beste": [0] * k, "regret": [0] * k, "instanzen": 0}
    for j in (range(C.INSTANZEN[bereich]) if instanzen is None else instanzen):
        seed = mess_seed(bereich, verteilung, n_index, j)
        inst = zufallsinstanz(bereich, verteilung, n, seed)
        s = schranke(inst)
        z = zaehle(inst, seed)
        kleinste = min(z)
        out["instanzen"] += 1
        for m in range(k):
            out["ueber"][m] += z[m] - s
            out["beste"][m] += z[m] == kleinste
            out["regret"][m] += z[m] - kleinste
    return out


@lru_cache(maxsize=1)
def vorberechnet() -> dict:
    return json.loads(PRECOMPUTED.read_text(encoding="utf-8"))


def zelle_schluessel(bereich: int, verteilung: int, n_index: int) -> str:
    return f"{bereich}|{C.VERTEILUNGEN[bereich][verteilung][0]}|{C.MESS_N[bereich][n_index]}"


def zeile(bereich: int, verteilung: int, n_index: int, daten: dict | None = None) -> dict:
    """Mittelwerte und Anteile einer Zelle aus den vorberechneten Summen: mittel[m] (Behälter über der Schranke), beste[m] (Prozent der Instanzen), regret[m] (mittlerer Regret) und die Gewinner
    (Verfahren mit dem kleinsten auf zwei Stellen gerundeten Mittel)."""
    daten = daten or vorberechnet()
    z = daten["zellen"][zelle_schluessel(bereich, verteilung, n_index)]
    k = z["instanzen"]
    mittel = [x / k for x in z["ueber"]]
    runden = [round(x, 2) for x in mittel]
    return {"bereich": bereich, "verteilung": verteilung, "n": C.MESS_N[bereich][n_index], "n_index": n_index, "instanzen": k, "mittel": mittel,
            "beste": [100.0 * x / k for x in z["beste"]], "regret": [x / k for x in z["regret"]],
            "gewinner": tuple(m for m, x in enumerate(runden) if x == min(runden))}


def zellen_von(bereich: int):
    return [(v, ni) for v in range(len(C.VERTEILUNGEN[bereich])) for ni in range(len(C.MESS_N[bereich]))]


def uebersicht(bereich: int, daten: dict | None = None) -> dict:
    """Über alle Zellen des Bereichs: Regret, Anteil bester und Mittel je Verfahren (Summen durch die Zahl aller Instanzen) und die Verfahren mit dem kleinsten gerundeten Regret („ein Verfahren
    für alles“)."""
    daten = daten or vorberechnet()
    k = len(C.VERFAHREN[bereich])
    summe = {"ueber": [0] * k, "beste": [0] * k, "regret": [0] * k}
    n_ges = 0
    for v, ni in zellen_von(bereich):
        z = daten["zellen"][zelle_schluessel(bereich, v, ni)]
        n_ges += z["instanzen"]
        for art in summe:
            for m in range(k):
                summe[art][m] += z[art][m]
    regret = [x / n_ges for x in summe["regret"]]
    gerundet = [round(x, 2) for x in regret]
    einfach = [m for m in range(k) if C.AUSWERTUNGEN[bereich][m] == 1]
    kleinster = min(gerundet[m] for m in einfach)
    return {"bereich": bereich, "instanzen": n_ges, "regret": regret, "beste": [100.0 * x / n_ges for x in summe["beste"]], "mittel": [x / n_ges for x in summe["ueber"]],
            "ein_verfahren": tuple(m for m, x in enumerate(gerundet) if x == min(gerundet)),
            "ein_verfahren_einfach": tuple(m for m in einfach if gerundet[m] == kleinster)}


def gewinner_je_zelle(bereich: int, daten: dict | None = None) -> dict:
    return {(v, ni): zeile(bereich, v, ni, daten)["gewinner"] for v, ni in zellen_von(bereich)}


def abweichende_zellen(bereich: int, daten: dict | None = None) -> list:
    """Zellen, in denen der Gewinner nicht zu den Verfahren gehört, die „ein Verfahren für alles“ wählt: dort dreht sich die Rangfolge."""
    eins = set(uebersicht(bereich, daten)["ein_verfahren"])
    return [zelle for zelle, g in gewinner_je_zelle(bereich, daten).items() if not eins & set(g)]


def empfehlung(bereich: int, verteilung, n: int, daten: dict | None = None) -> tuple:
    """(Verfahren, Art): bei einer Zufallsinstanz, deren Verteilung und Teilezahl eine Zelle der Karte sind, die Gewinner dieser Zelle (Art „Zelle“), sonst die Verfahren von „ein Verfahren für alles“
    im Bereich (Art „alle“)."""
    if verteilung is not None and n in C.MESS_N[bereich]:
        return zeile(bereich, verteilung, C.MESS_N[bereich].index(n), daten)["gewinner"], "Zelle"
    return uebersicht(bereich, daten)["ein_verfahren"], "alle"


# ------------------------------------------------------------------------------------------------------------------------------------------
# Verdikte (reine Funktionen: (Art, Text))


def _namen(bereich: int, verfahren) -> str:
    return " oder ".join(C.VERFAHREN[bereich][m] for m in verfahren)


def verdict_instanz(a: Analysis) -> tuple[str, str]:
    """Verdikt zur Instanz: das beste Verfahren dieser Instanz gegen den schlechtesten und die Schranke, und ob die Empfehlung der Karte in dieser Instanz zu den besten gehört."""
    b = a.settings.bereich
    z = a.zaehlungen
    kopf = f"Am wenigsten Behälter braucht {_namen(b, a.beste)} (**{z[a.beste[0]]}**), am meisten {C.VERFAHREN[b][z.index(max(z))]} ({max(z)}); die Schranke ist {a.schranke}."
    if a.optimum is not None:
        kopf += f" Das Optimum des Handbeispiels ist {a.optimum}" + (" (ohne Stützbedingung)." if b == C.DREI_STUETZ else ".")
    herkunft = "für genau diese Zelle der Karte" if a.empfehlung_art == "Zelle" else "als ein Verfahren für alles in diesem Bereich"
    if set(a.beste) & set(a.empfehlung):
        return "success", kopf + f" Die Karte empfiehlt {_namen(b, a.empfehlung)} ({herkunft}): Das gehört hier zu den besten."
    gut = z[a.empfehlung[0]]
    return "warning", kopf + f" Die Karte empfiehlt {_namen(b, a.empfehlung)} ({herkunft}), das braucht hier {gut} Behälter, {gut - z[a.beste[0]]} mehr als das beste."


def verdict_karte(z: dict) -> tuple[str, str]:
    """Verdikt zur gewählten Zelle: der Gewinner (kleinstes auf zwei Stellen gerundetes Mittel über der Schranke), der Abstand zum Zweitbesten und der Anteil der Instanzen, in denen der Gewinner zu den besten gehört."""
    b = z["bereich"]
    runden = [round(x, 2) for x in z["mittel"]]
    gewinner = z["gewinner"]
    rest = sorted({x for x in runden if x > min(runden)})
    teil = (f"Für {C.VERTEILUNG_LANG[b][z['verteilung']]} mit n = {z['n']} gewinnt im Mittel {_namen(b, gewinner)} mit {min(runden):.2f} Behältern über der Schranke ({z['instanzen']} Instanzen)")
    if len(gewinner) > 1:
        return "info", teil + f"; {len(gewinner)} Verfahren liegen gleichauf."
    beste = round(z["beste"][gewinner[0]])
    if not rest:
        return "info", teil + "."
    abstand = round(rest[0] - min(runden), 2)
    return "success", teil + f", {abstand:.2f} vor dem Zweitbesten; in {beste} % der Instanzen gehört er zu den besten."


def verdict_regret(u: dict) -> tuple[str, str]:
    """Verdikt zu „ein Verfahren für alles“: der kleinste mittlere Regret über alle Zellen und der Regret der anderen (auf zwei Stellen gerundet)."""
    b = u["bereich"]
    runden = [round(x, 2) for x in u["regret"]]
    wahl = u["ein_verfahren"]
    andere = ", ".join(f"{C.VERFAHREN[b][m]} {runden[m]:.2f}" for m in range(len(runden)) if m not in wahl)
    text = (f"Wer in {C.BEREICH_KURZ[b]} nur ein Verfahren benutzt, fährt mit {_namen(b, wahl)} am besten: im Mittel {min(runden):.2f} Behälter mehr als das instanzweise Beste "
            f"({u['instanzen']} Instanzen). Die anderen: {andere}.")
    if any(C.AUSWERTUNGEN[b][m] > 1 for m in wahl):
        einfach = u["ein_verfahren_einfach"]
        text += (f" Das gewählte Verfahren braucht {max(C.AUSWERTUNGEN[b][m] for m in wahl)} Auswertungen je Instanz statt einer; unter den Verfahren mit einer Auswertung ist {_namen(b, einfach)} "
                 f"am besten ({min(runden[m] for m in einfach):.2f}).")
    return "success", text


def paar_zaehlung(bereich: int, daten: dict | None = None) -> list:
    """Für jedes Paar von Verfahren (a < b) die Zahl der Zellen, in denen a im gerundeten Mittel besser, schlechter oder gleich gut ist als b: Liste von (a, b, a_besser, b_besser, gleich)."""
    zeilen = [zeile(bereich, v, ni, daten) for v, ni in zellen_von(bereich)]
    k = len(C.VERFAHREN[bereich])
    out = []
    for a in range(k):
        for b in range(a + 1, k):
            ra = [round(z["mittel"][a], 2) for z in zeilen]
            rb = [round(z["mittel"][b], 2) for z in zeilen]
            out.append((a, b, sum(x < y for x, y in zip(ra, rb)), sum(x > y for x, y in zip(ra, rb)), sum(x == y for x, y in zip(ra, rb))))
    return out


def drehende_paare(bereich: int, daten: dict | None = None) -> list:
    """Die Paare, deren Reihenfolge sich zwischen den Zellen dreht (beide Verfahren sind in mindestens einer Zelle besser), nach Ausgewogenheit sortiert (zuerst das Paar, dessen schwächere Seite die
    meisten Zellen hat)."""
    paare = [p for p in paar_zaehlung(bereich, daten) if p[2] > 0 and p[3] > 0]
    return sorted(paare, key=lambda p: (-min(p[2], p[3]), p[0], p[1]))


def verdict_wechsel(bereich: int, daten: dict | None = None) -> tuple[str, str]:
    """Verdikt zur Rangfolge: Gewinner in jeder Zelle gleich? Und welche Paare von Verfahren drehen ihre Reihenfolge zwischen den Zellen?"""
    abw = abweichende_zellen(bereich, daten)
    gesamt = len(zellen_von(bereich))
    eins = uebersicht(bereich, daten)["ein_verfahren"]
    drehend = drehende_paare(bereich, daten)
    if abw:
        teile = ", ".join(f"{C.VERTEILUNG_KURZ[bereich][v]} {C.MESS_N[bereich][ni]} ({_namen(bereich, gewinner_je_zelle(bereich, daten)[(v, ni)])})" for v, ni in abw)
        kopf = f"In {len(abw)} von {gesamt} Zellen von {C.BEREICH_KURZ[bereich]} gewinnt ein anderes Verfahren als {_namen(bereich, eins)}: {teile}."
        art = "warning"
    else:
        kopf = f"In allen {gesamt} Zellen von {C.BEREICH_KURZ[bereich]} gehört {_namen(bereich, eins)} zu den Gewinnern: Der Gewinner dreht sich nirgends."
        art = "info"
    if not drehend:
        return art, kopf + " Auch zwischen den übrigen Verfahren dreht sich die Reihenfolge in keiner Zelle."
    a, b, ab, ba, gl = drehend[0]
    return art, kopf + f" Zwischen anderen Verfahren dreht sie sich: {C.VERFAHREN[bereich][a]} ist in {ab} Zellen besser als {C.VERFAHREN[bereich][b]}, in {ba} schlechter, in {gl} gleich gut."


def stuetz_zeilen(daten: dict | None = None) -> list:
    """Experiment 4: je Zelle (Verteilung, Teilezahl) der 3D-Karten das Gewinnerverfahren ohne und mit Mindest-Stützfläche 80 % und das beste gerundete Mittel über der Schranke beider Bereiche."""
    zeilen = []
    for v, ni in zellen_von(C.DREI):
        z2, z3 = zeile(C.DREI, v, ni, daten), zeile(C.DREI_STUETZ, v, ni, daten)
        b2, b3 = min(round(x, 2) for x in z2["mittel"]), min(round(x, 2) for x in z3["mittel"])
        zeilen.append({"verteilung": v, "n": z2["n"], "ohne": z2["gewinner"], "mit": z3["gewinner"], "bester_ohne": b2, "bester_mit": b3, "mehr": round(b3 - b2, 2)})
    return zeilen


def verdict_stuetz_wahl(zeilen: list) -> tuple[str, str]:
    """Verdikt zu Experiment 4: Wie viele Zellen haben mit der Stützbedingung ein anderes Gewinnerverfahren (Verfahren der Bereiche heißen verschieden), und was kostet die Bedingung im besten Verfahren (kleinster
    und größter Mehrbedarf der Zellen)?"""
    ohne_ep = sum(1 for z in zeilen if 2 in z["ohne"])
    mit_grund = sum(1 for z in zeilen if z["mit"] == (1,))
    mehr = [z["mehr"] for z in zeilen]
    return "warning", (f"Ohne Stützbedingung gewinnt in {ohne_ep} von {len(zeilen)} Zellen Extreme Points mit Projektionen (nach Volumen sortiert); mit 80 % Stützfläche gewinnt in {mit_grund} von {len(zeilen)} Zellen "
                       f"Extreme Points nach der Grundfläche. Die Bedingung kostet im jeweils besten Verfahren {min(mehr):.2f} bis {max(mehr):.2f} Behälter über der Schranke.")
