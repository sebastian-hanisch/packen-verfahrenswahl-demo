"""Jede Zahl der README und der App-Texte, nachgerechnet (DEMO-PLAYBOOK §4 und §11a).

* Das vorberechnete Raster (pvw_precomputed.json): jede Zelle bei n = 20 frisch gerechnet, bei allen Zellen die ersten drei Instanzen einzeln (Stichprobe in der Datei); alle Zellen vollständig prüft
  `python generate_precomputed.py --check` (parallel). Die Optima der Handbeispiele werden mit dem Teilmengen-DP (1D) und CP-SAT (2D, 3D) nachgerechnet.
* Die Befunde der README werden aus denselben Auswertungsfunktionen wie in der App berechnet und als Text in der README gesucht.
* Der Text des Expanders „Annahmen, Grenzen und bekannte Probleme“ steht wörtlich in der README.
Dezimalzahlen stehen in der README mit Komma, in der App mit Punkt."""

import itertools
from pathlib import Path

import pytest

import pvw_algorithm as A
import pvw_constants as C
import pvw_evaluation as ev
from pvw_scenario import beispiel, mess_seed, zufallsinstanz

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
ZELLEN = [(b, v, ni) for b in C.BEREICHE for v, ni in ev.zellen_von(b)]


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def test_raster_hat_alle_zellen_und_die_parameter():
    daten = ev.vorberechnet()
    assert len(ZELLEN) == 16 + 12 + 12 + 12 == 52
    assert set(daten["zellen"]) == {ev.zelle_schluessel(*z) for z in ZELLEN} and set(daten["stichprobe"]) == set(daten["zellen"])
    for b, v, ni in ZELLEN:
        z = daten["zellen"][ev.zelle_schluessel(b, v, ni)]
        assert z["instanzen"] == C.INSTANZEN[b] and C.INSTANZEN == {0: 200, 1: 100, 2: 100, 3: 100}
        assert all(len(z[k]) == len(C.VERFAHREN[b]) for k in ("ueber", "beste", "regret"))


def _addiere(a, b):
    if isinstance(a, dict):
        return {k: _addiere(a[k], b[k]) for k in a}
    if isinstance(a, list):
        return [x + y for x, y in zip(a, b)]
    return a + b


def _nicht_kleiner(a, b):
    if isinstance(a, dict):
        return all(_nicht_kleiner(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return all(x >= y for x, y in zip(a, b))
    return a >= b


@pytest.mark.parametrize("b", list(C.BEREICHE))
def test_jede_zelle_bei_n_20_stimmt_mit_frischer_rechnung(b):
    for v in range(4):
        assert ev.messzelle(b, v, 0) == ev.vorberechnet()["zellen"][ev.zelle_schluessel(b, v, 0)]


@pytest.mark.parametrize("b,v,ni", ZELLEN)
def test_stichprobe_jeder_zelle_stimmt_mit_frischer_rechnung(b, v, ni):
    schl = ev.zelle_schluessel(b, v, ni)
    daten = ev.vorberechnet()
    summe = None
    for j in C.STICHPROBE_J:
        gespeichert = daten["stichprobe"][schl][str(j)]
        assert ev.messzelle(b, v, ni, [j]) == gespeichert, (schl, j)
        summe = gespeichert if summe is None else {k: _addiere(summe[k], gespeichert[k]) for k in gespeichert}
    zelle = daten["zellen"][schl]
    for k in summe:                          # die Stichprobe ist Teil der Zelle: jede Summe der Zelle ist mindestens so groß (alle Beiträge sind nicht negativ)
        assert _nicht_kleiner(zelle[k], summe[k]), (schl, k)


@pytest.mark.parametrize("b,v,ni", ZELLEN)
def test_summen_sind_in_sich_stimmig(b, v, ni):
    z = ev.vorberechnet()["zellen"][ev.zelle_schluessel(b, v, ni)]
    k = z["instanzen"]
    assert all(x >= 0 for x in z["ueber"]) and all(x >= 0 for x in z["regret"]) and all(0 <= x <= k for x in z["beste"])
    assert sum(z["beste"]) >= k and min(z["regret"]) >= 0                         # jede Instanz hat mindestens ein bestes Verfahren
    assert all(z["ueber"][m] >= z["regret"][m] for m in range(len(z["ueber"])))   # über der Schranke ist mindestens so viel wie über dem Besten
    if C.AUSWERTUNGEN[b][-1] > 1:                                                 # 2D: die Suche startet bei MaxRects und wird nie schlechter
        assert z["ueber"][3] <= z["ueber"][2]


# --- Handbeispiele ------------------------------------------------------------------------------------------------------------------------------


def test_handbeispiele_haben_die_behaelterzahlen_und_optima_der_konstanten():
    assert [ev.zaehle(beispiel(b), C.DEFAULT_SEED) for b in C.BEREICHE] == [(7, 7, 7, 5, 5), (4, 3, 3, 3), (2, 2, 1), (2, 2, 2)]
    assert [ev.schranke(beispiel(b)) for b in C.BEREICHE] == [5, 3, 1, 1] and C.BEISPIEL_OPTIMUM == {0: 5, 1: 3, 2: 1, 3: 1}
    assert A.optimum_1d(list(beispiel(0).teile), 100) == 5 and sum(beispiel(0).teile) == 459
    for zeile in ("| 1D | NF | 7 | 5 | 5 |", "| 1D | FFD | 5 | 5 | 5 |", "| 2D | Regal | 4 | 3 | 3 |", "| 2D | MaxRects + Suche | 3 | 3 | 3 |", "| 3D | EP voll | 1 | 1 | 1 |", "| 3D | EP einfach | 2 | 1 | 1 |"):
        assert zeile in README
    assert "1D: NF, FF, BF **7** Behälter, FFD und BFD **5** (Optimum 5). 2D: Regal **4**, Skyline, MaxRects und die Suche **3** (Optimum 3). 3D: Schichten und EP einfach **2**, EP voll **1** (Optimum 1)" in README


def test_optima_der_2d_und_3d_handbeispiele_mit_cpsat():
    pytest.importorskip("ortools")
    from dev.opt_2d import optimum_cpsat as opt2
    from dev.opt_3d import optimum_cpsat as opt3

    b2, b3 = beispiel(1), beispiel(2)
    assert opt2(b2.teile, b2.cap, 3, 60.0, 2) == C.BEISPIEL_OPTIMUM[1] == 3 and A.schranken_2d(b2.teile, b2.cap)[2] == 3
    assert opt3(b3.teile, b3.cap, 2, 60.0, 2) == C.BEISPIEL_OPTIMUM[2] == 1 and beispiel(3).teile == b3.teile


# --- Befunde der README --------------------------------------------------------------------------------------------------------------------


def test_1d_sortieren_ist_alles():
    u = ev.uebersicht(0)
    assert [round(x, 2) for x in u["regret"]] == [8.5, 1.73, 1.33, 0.0, 0.0] and u["ein_verfahren"] == (3, 4) and u["instanzen"] == 3200
    gewinner = [ev.zeile(0, v, ni)["gewinner"] for v, ni in ev.zellen_von(0)]
    assert gewinner.count((3, 4)) == 14 and gewinner.count((4,)) == 2 and len(gewinner) == 16
    breit = [(v, ni) for v, ni in ev.zellen_von(0) if ev.zeile(0, v, ni)["gewinner"] == (4,)]
    assert [(C.VERTEILUNG_KURZ[0][v], C.MESS_N[0][ni]) for v, ni in breit] == [("breit", 20), ("breit", 200)]
    assert all(round(ev.zeile(0, v, ni)["mittel"][3], 2) - round(ev.zeile(0, v, ni)["mittel"][4], 2) == pytest.approx(0.01) for v, ni in breit)
    d = ev.vorberechnet()["zellen"]
    assert (sum(d[ev.zelle_schluessel(0, v, ni)]["regret"][3] for v, ni in ev.zellen_von(0)), sum(d[ev.zelle_schluessel(0, v, ni)]["regret"][4] for v, ni in ev.zellen_von(0))) == (3, 1)
    # Regret FFD und BFD ungerundet: Summen 3 und 1 über 3200 Instanzen, also unter 0,01; beste Instanzen 3197 und 3199 von 3200 (99,9 % und 100 %)
    summe_regret = [sum(d[ev.zelle_schluessel(0, v, ni)]["regret"][m] for v, ni in ev.zellen_von(0)) for m in (3, 4)]
    summe_beste = [sum(d[ev.zelle_schluessel(0, v, ni)]["beste"][m] for v, ni in ev.zellen_von(0)) for m in (3, 4)]
    assert all(s / 3200 < 0.01 for s in summe_regret) and [round(100 * s / 3200, 1) for s in summe_beste] == [99.9, 100.0]
    assert "**FFD und BFD in allen 16 Zellen** (in 14 gleichauf, in zwei, breit bei n = 20 und n = 200, BFD allein mit 0,01 Vorsprung). Sortieren bringt hier den größten Gewinn: Regret FFD und BFD unter 0,01 (beste Instanzen 99,9 % und 100 %, gerundet), First Fit 1,73, Best Fit 1,33, Next Fit **8,50** (alle drei in Lieferreihenfolge); sortiert ist die Regel fast egal" in README
    assert "Sie unterscheiden sich in **2 von 3200** Instanzen (FFD braucht dann einen Behälter mehr als BFD)" in README


def test_1d_ffd_gegen_bfd_direkt_gezaehlt():
    """Direkter Vergleich der Behälterzahlen je Instanz (nicht aus den Regretsummen abgeleitet): FFD braucht in 2 von 3200 Instanzen einen Behälter mehr als BFD, BFD nie mehr als FFD."""
    ffd_mehr = bfd_mehr = gesamt = 0
    for v, ni in ev.zellen_von(0):
        for j in range(200):
            inst = zufallsinstanz(0, v, C.MESS_N[0][ni], mess_seed(0, v, ni, j))
            a, b = A.anzahl_1d(list(inst.teile), 3, inst.cap), A.anzahl_1d(list(inst.teile), 4, inst.cap)
            gesamt += 1
            ffd_mehr += a > b
            bfd_mehr += b > a
    assert (gesamt, ffd_mehr, bfd_mehr) == (3200, 2, 0)


def test_2d_die_suche_gewinnt_und_die_einfachen_verfahren_drehen():
    u = ev.uebersicht(1)
    assert [round(x, 2) for x in u["regret"]] == [0.34, 0.39, 0.2, 0.0] and u["ein_verfahren"] == (3,) and u["ein_verfahren_einfach"] == (2,)
    zeilen = [ev.zeile(1, v, ni) for v, ni in ev.zellen_von(1)]
    assert all(z["gewinner"] == (3,) for z in zeilen) and min(z["beste"][3] for z in zeilen) == 99.0 and max(z["beste"][3] for z in zeilen) == 100.0
    vorsprung = [round(round(z["mittel"][2], 2) - round(z["mittel"][3], 2), 2) for z in zeilen]
    assert (min(vorsprung), max(vorsprung)) == (0.01, 0.46)
    paare = {(a, b): (x, y, g) for a, b, x, y, g in ev.paar_zaehlung(1)}
    assert paare[(0, 1)] == (5, 6, 1) and paare[(0, 2)] == (1, 9, 2) and [p[:2] for p in ev.drehende_paare(1)] == [(0, 1), (0, 2)]
    assert "**MaxRects mit Tausch-Suche in allen 12 Zellen**, in 99 bis 100 % der Instanzen gehört sie zu den besten; Vorsprung gegenüber MaxRects ohne Suche 0,01 bis 0,46 Behälter. Sie braucht 200 Auswertungen statt einer" in README
    assert "**MaxRects** (Regret 0,20) vor Regal (0,34) und Skyline (0,39)" in README
    assert "Regal ist besser als Skyline in 5 Zellen, schlechter in 6, gleich gut in 1; Regal ist besser als MaxRects in 1 Zelle, schlechter in 9, gleich gut in 2" in README


def test_3d_extreme_points_mit_projektionen_gewinnen():
    u = ev.uebersicht(2)
    assert [round(x, 2) for x in u["regret"]] == [0.72, 0.2, 0.02] and u["ein_verfahren"] == (2,)
    gewinner = [ev.zeile(2, v, ni)["gewinner"] for v, ni in ev.zellen_von(2)]
    assert gewinner.count((2,)) == 10 and gewinner.count((0, 1, 2)) == 1 and gewinner.count((1, 2)) == 1
    assert ev.zeile(2, 2, 0)["gewinner"] == (0, 1, 2) and ev.zeile(2, 2, 2)["gewinner"] == (1, 2) and C.VERTEILUNG_KURZ[2][2] == "klein"
    paare = {(a, b): (x, y, g) for a, b, x, y, g in ev.paar_zaehlung(2)}
    assert paare[(0, 1)] == (1, 10, 1) and [p[:2] for p in ev.drehende_paare(2)] == [(0, 1)]
    flach20 = ev.zeile(2, 3, 0)
    assert (round(flach20["mittel"][0], 2), round(flach20["mittel"][1], 2)) == (0.89, 1.01)
    assert "**Extreme Points mit Projektionen** in 10 Zellen allein, in zwei gleichauf (kleine Quader: bei n = 20 alle drei, bei n = 80 mit EP einfach). Regret EP voll **0,02**, EP einfach 0,20, Schichten **0,72**" in README
    assert "Schichten sind besser als EP einfach in **1** Zelle (flache Quader, n = 20: 0,89 gegen 1,01), schlechter in 10, gleich gut in 1" in README


def test_3d_mit_stuetzflaeche_gewinnt_die_grundflaeche():
    u = ev.uebersicht(3)
    assert [round(x, 2) for x in u["regret"]] == [0.59, 0.06, 1.11] and u["ein_verfahren"] == (1,)
    assert all(ev.zeile(3, v, ni)["gewinner"] == (1,) for v, ni in ev.zellen_von(3))
    assert [round(x, 2) for x in ev.zeile(3, 3, 2)["mittel"]] == [6.2, 4.02, 7.01]
    assert "**Extreme Points mit der Grundfläche als Schlüssel in allen 12 Zellen im Mittel vorn** (Regret **0,06**, Volumen 0,59, Höhe 1,11); flache Quader bei n = 80: Grundfläche 4,02, Volumen 6,20, Höhe 7,01. In vier Zellen (mittlere Quader bei n = 20, 40 und 80, kleine Quader bei n = 40) liegt der Vorsprung vor dem Volumen innerhalb der Streuung" in README


def test_die_stuetzbedingung_aendert_die_wahl():
    zeilen = ev.stuetz_zeilen()
    assert len(zeilen) == 12 and all(2 in z["ohne"] for z in zeilen) and all(z["mit"] == (1,) for z in zeilen)
    assert (min(z["mehr"] for z in zeilen), max(z["mehr"] for z in zeilen)) == (0.02, 1.83) and max(zeilen, key=lambda z: z["mehr"])["verteilung"] == 3
    assert ev.verdict_stuetz_wahl(zeilen)[1].startswith("Ohne Stützbedingung gewinnt in 12 von 12 Zellen Extreme Points mit Projektionen")
    mehr = sorted(z["mehr"] for z in zeilen)
    assert mehr[:2] == [0.02, 0.33] and [z["mehr"] for z in zeilen if z["verteilung"] == 2 and z["n"] == 20] == [0.02]
    assert ("Ohne Bedingung gewinnt Extreme Points mit Projektionen nach Volumen (in allen 12 Zellen unter den Gewinnern), mit 80 % Stützfläche in allen 12 Zellen im Mittel die Grundfläche. "
            "Der Schlüssel Grundfläche ist ohne Bedingung in der Karte nicht gemessen. "
            "Die Bedingung kostet im jeweils besten Verfahren **0,33 bis 1,83** Behälter über der Schranke (am meisten bei flachen Quadern); bei kleinen Quadern mit n = 20 sind es nur +0,02, nicht von null zu trennen. "
            "Es sind Differenzen zweier getrennter Stichproben mit je 100 Instanzen") in README


def test_der_gewinner_dreht_sich_nirgends():
    for b in C.BEREICHE:
        assert ev.abweichende_zellen(b) == []
    assert ("In jedem Bereich gewinnt im gerundeten Mittel dasselbe Verfahren (oder gleichauf) in allen Zellen: **der Gewinner dreht sich nirgends**; wo sich etwas dreht, sind es die Plätze dahinter. "
            "Die Wahl hängt in dieser Karte vom Bereich ab, nicht von den vier gemessenen Mischungen") in README
    assert ev.verdict_wechsel(1)[1].startswith("In allen 12 Zellen von 2D gehört MaxRects + Suche zu den Gewinnern: Der Gewinner dreht sich nirgends.")


# --- Tabellen der README -------------------------------------------------------------------------------------------------------------------


def test_readme_tabellen_geben_jede_zeile_wieder():
    from dev.readme_bauen import beispiel_tabelle, karte, regret_tabelle, stuetz_tabelle

    for tabelle in (karte(0), karte(1), karte(2), karte(3), regret_tabelle(), stuetz_tabelle(), beispiel_tabelle()):
        for zeile in tabelle.split("\n"):
            assert zeile in README, zeile


# --- Texte ---------------------------------------------------------------------------------------------------------------------------------------


def test_annahmen_text_der_app_steht_woertlich_in_der_readme():
    assert C.ASSUMPTIONS_MARKDOWN in README


def test_zahlen_im_annahmen_text_sind_die_der_konstanten():
    t = C.ASSUMPTIONS_MARKDOWN
    assert "In 1D hat der Behälter die Kapazität 1000 (die Handbeispiele 100), in 2D und 3D die Kantenlänge 100" in t and "(1D mit 200, sonst mit 100 Instanzen je Zelle)" in t and "200 Auswertungen" in t
    assert C.CAP == {0: 1000, 1: 100, 2: 100, 3: 100} and C.HAND_CAP == {0: 100, 1: 100, 2: 100, 3: 100} and C.SUCHBUDGET == A.SUCHBUDGET_2D == 200 and C.S_MIN[3] == 0.8
    assert "Mindest-Stützfläche von 80 %" in t and "nicht gelesen" in t and "keine Zahl aus ihnen übernommen" in t


def test_readme_nennt_das_raster_wie_der_code():
    assert C.MESS_N == {0: (20, 50, 100, 200), 1: (20, 40, 80), 2: (20, 40, 80), 3: (20, 40, 80)}
    assert "vier Bereiche × je vier Verteilungen × drei Teilezahlen (2D und 3D: 20, 40, 80; 1D: 20, 50, 100, 200) × **100 feste Instanzen** je Zelle (1D **200**)" in README
    assert [v[0] for v in C.VERTEILUNGEN[0]] == ["klein", "mittel", "gross", "breit"] and [v[2] for v in C.VERTEILUNGEN[1]] == [((20, 60), (20, 60)), ((5, 70), (5, 70)), ((10, 40), (10, 40)), ((5, 30), (30, 80))]
    assert "klein 1 bis 25 %, mittel 10 bis 50 %, groß 20 bis 80 %, breit 1 bis 90 % der Kapazität" in README and "hoch schmal Breite 5 bis 30 und Höhe 30 bis 80" in README
    assert [v[2] for v in C.VERTEILUNGEN[2]][3] == ((30, 80), (30, 80), (5, 30)) and "flach Breite und Tiefe 30 bis 80, Höhe 5 bis 30" in README


def test_readme_hat_keine_offenen_platzhalter_ausser_dem_live_link():
    ohne_link = README.replace("<!-- TODO nach dem Deploy", "")
    assert "{{" not in README and "TESTZAHL" not in README and ohne_link.count("TODO") == 0
    assert len(list(itertools.chain(*[ev.zellen_von(b) for b in C.BEREICHE]))) == 52
