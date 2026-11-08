"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds. Damit prüft der Test die Grenzen (Gleichstand nach Rundung, kleiner und größer) und jede genannte Zahl direkt."""

import pvw_constants as C
import pvw_evaluation as ev
from pvw_scenario import Instance


def _a(bereich, zaehlungen, schranke, empfehlung, art="Zelle", optimum=None):
    inst = Instance(bereich, (1, 2), 10) if bereich == 0 else Instance(bereich, ((1, 1),) if bereich == 1 else ((1, 1, 1),), 10)
    return ev.Analysis(inst, schranke, tuple(zaehlungen), ev.beste_verfahren(zaehlungen), optimum, tuple(empfehlung), art, ev.Settings(bereich))


def test_beste_verfahren_nennt_alle_mit_der_kleinsten_zahl():
    assert ev.beste_verfahren((7, 7, 7, 5, 5)) == (3, 4) and ev.beste_verfahren((3,)) == (0,) and ev.beste_verfahren((4, 3, 3, 5)) == (1, 2)


def test_instanzverdikt_empfehlung_stimmt():
    kind, text = ev.verdict_instanz(_a(0, (7, 7, 7, 5, 5), 5, (3, 4), "alle", 5))
    assert kind == "success"
    assert text == ("Am wenigsten Behälter braucht FFD oder BFD (**5**), am meisten NF (7); die Schranke ist 5. Das Optimum des Handbeispiels ist 5. "
                    "Die Karte empfiehlt FFD oder BFD (als ein Verfahren für alles in diesem Bereich): Das gehört hier zu den besten.")


def test_instanzverdikt_empfehlung_stimmt_nicht_und_zweiter_herkunftstext():
    kind, text = ev.verdict_instanz(_a(1, (9, 8, 9, 8), 7, (2,), "Zelle"))
    assert kind == "warning"
    assert text == ("Am wenigsten Behälter braucht Skyline oder MaxRects + Suche (**8**), am meisten Regal (9); die Schranke ist 7. "
                    "Die Karte empfiehlt MaxRects (für genau diese Zelle der Karte), das braucht hier 9 Behälter, 1 mehr als das beste.")


def test_instanzverdikt_stuetzbereich_nennt_das_optimum_ohne_stuetzbedingung():
    kind, text = ev.verdict_instanz(_a(3, (2, 2, 2), 1, (1,), "alle", 1))
    assert "Das Optimum des Handbeispiels ist 1 (ohne Stützbedingung)." in text and kind == "success"
    assert "Das Optimum" not in ev.verdict_instanz(_a(2, (2, 3, 2), 1, (2,)))[1]


def _z(bereich, mittel, verteilung=0, n=40, beste=None, instanzen=100):
    runden = [round(x, 2) for x in mittel]
    return {"bereich": bereich, "verteilung": verteilung, "n": n, "instanzen": instanzen, "mittel": mittel, "beste": beste or [50.0] * len(mittel), "regret": [0.0] * len(mittel),
            "gewinner": tuple(m for m, x in enumerate(runden) if x == min(runden))}


def test_kartenverdikt_gewinner_abstand_und_anteil():
    kind, text = ev.verdict_karte(_z(1, [1.13, 1.33, 1.13, 0.78], beste=[65.0, 46.0, 65.0, 100.0]))
    assert kind == "success"
    assert text == ("Für mittlere Rechtecke mit n = 40 gewinnt im Mittel MaxRects + Suche mit 0.78 Behältern über der Schranke (100 Instanzen), 0.35 vor dem Zweitbesten; in 100 % der Instanzen gehört er zu den besten.")


def test_kartenverdikt_gleichstand_nach_rundung_und_alle_gleich():
    kind, text = ev.verdict_karte(_z(1, [1.004, 1.33, 0.996, 1.5]))                 # 1,00 und 1,00: gleichauf
    assert kind == "info" and text.endswith("; 2 Verfahren liegen gleichauf.") and "Regal oder MaxRects mit 1.00" in text
    kind, text = ev.verdict_karte(_z(2, [0.0, 0.0, 0.0], verteilung=2, n=20))
    assert kind == "info" and text.endswith("; 3 Verfahren liegen gleichauf.") and "Schichten oder EP einfach oder EP voll mit 0.00" in text and "kleine Quader mit n = 20" in text


def test_kartenverdikt_zweitbester_nach_rundung():
    kind, text = ev.verdict_karte(_z(0, [0.504, 0.496, 0.9, 0.9, 0.9]))              # beide 0,50: gleichauf, nicht „vor dem Zweitbesten“
    assert kind == "info" and "gleichauf" in text
    kind, text = ev.verdict_karte(_z(0, [0.494, 0.506, 0.9, 0.9, 0.9], beste=[60.0, 40.0, 0.0, 0.0, 0.0]))     # 0,49 gegen 0,51
    assert kind == "success" and "NF mit 0.49" in text and "0.02 vor dem Zweitbesten; in 60 % der Instanzen" in text


def _u(bereich, regret, ein, einfach=None, instanzen=1200):
    k = len(regret)
    return {"bereich": bereich, "instanzen": instanzen, "regret": regret, "beste": [50.0] * k, "mittel": [0.0] * k, "ein_verfahren": tuple(ein), "ein_verfahren_einfach": tuple(einfach or ein)}


def test_regretverdikt_ohne_und_mit_suche():
    kind, text = ev.verdict_regret(_u(2, [0.72, 0.2, 0.02], (2,)))
    assert kind == "success"
    assert text == ("Wer in 3D nur ein Verfahren benutzt, fährt mit EP voll am besten: im Mittel 0.02 Behälter mehr als das instanzweise Beste (1200 Instanzen). Die anderen: Schichten 0.72, EP einfach 0.20.")
    kind, text = ev.verdict_regret(_u(1, [0.34, 0.39, 0.2, 0.0], (3,), (2,)))
    assert text == ("Wer in 2D nur ein Verfahren benutzt, fährt mit MaxRects + Suche am besten: im Mittel 0.00 Behälter mehr als das instanzweise Beste (1200 Instanzen). Die anderen: Regal 0.34, Skyline 0.39, MaxRects 0.20. "
                    "Das gewählte Verfahren braucht 200 Auswertungen je Instanz statt einer; unter den Verfahren mit einer Auswertung ist MaxRects am besten (0.20).")
    kind, text = ev.verdict_regret(_u(0, [8.5, 1.73, 1.33, 0.0, 0.0], (3, 4)))
    assert "mit FFD oder BFD am besten" in text and "Auswertungen" not in text


def _daten(bereich, zellen):
    """Synthetische Rasterdaten: zellen = {(verteilung, n_index): mittel je Verfahren}; der Regret ist hier gleich dem Mittel (Summe 100 mal mittel)."""
    k = len(C.VERFAHREN[bereich])
    return {"zellen": {ev.zelle_schluessel(bereich, v, ni): {"instanzen": 100, "ueber": [round(100 * x) for x in m], "beste": [50] * k, "regret": [round(100 * x) for x in m]} for (v, ni), m in zellen.items()}}


def _voll(bereich, mittel):
    return {(v, ni): mittel for v, ni in ev.zellen_von(bereich)}


def test_paarzaehlung_und_drehende_paare():
    zellen = _voll(2, [1.0, 0.5, 0.2])
    zellen[(0, 0)] = [0.4, 0.5, 0.2]              # Schichten schlagen EP einfach in einer Zelle
    zellen[(1, 0)] = [0.5, 0.5, 0.2]              # gleich in einer Zelle
    d = _daten(2, zellen)
    paare = ev.paar_zaehlung(2, d)
    assert paare[0] == (0, 1, 1, 10, 1) and paare[1] == (0, 2, 0, 12, 0) and paare[2] == (1, 2, 0, 12, 0)
    assert ev.drehende_paare(2, d) == [(0, 1, 1, 10, 1)]


def test_wechselverdikt_gewinner_dreht_nicht_aber_ein_paar():
    zellen = _voll(2, [1.0, 0.5, 0.2])
    zellen[(0, 0)] = [0.4, 0.5, 0.2]
    kind, text = ev.verdict_wechsel(2, _daten(2, zellen))
    assert kind == "info"
    assert text == ("In allen 12 Zellen von 3D gehört EP voll zu den Gewinnern: Der Gewinner dreht sich nirgends. Zwischen anderen Verfahren dreht sie sich: Schichten ist in 1 Zellen besser als EP einfach, "
                    "in 11 schlechter, in 0 gleich gut.")
    kind, text = ev.verdict_wechsel(2, _daten(2, _voll(2, [1.0, 0.5, 0.2])))
    assert kind == "info" and text.endswith("Auch zwischen den übrigen Verfahren dreht sich die Reihenfolge in keiner Zelle.")


def test_wechselverdikt_gewinner_dreht_sich():
    zellen = _voll(3, [0.5, 0.2, 1.0])
    zellen[(2, 1)] = [0.1, 0.2, 1.0]                    # Zelle klein, n = 40: ein anderer Gewinner
    kind, text = ev.verdict_wechsel(3, _daten(3, zellen))
    assert kind == "warning" and text.startswith("In 1 von 12 Zellen von 3D mit Stützfläche gewinnt ein anderes Verfahren als EP voll Grundfläche: klein 40 (EP voll Volumen).")


def test_stuetz_wahl_verdikt():
    zeilen = [{"verteilung": v, "n": 20, "ohne": (2,), "mit": (1,), "bester_ohne": 0.5, "bester_mit": 0.5 + 0.1 * (v + 1), "mehr": round(0.1 * (v + 1), 2)} for v in range(4)]
    kind, text = ev.verdict_stuetz_wahl(zeilen)
    assert kind == "warning"
    assert text == ("Ohne Stützbedingung gewinnt in 4 von 4 Zellen Extreme Points mit Projektionen (nach Volumen sortiert); mit 80 % Stützfläche gewinnt im Mittel in 4 von 4 Zellen Extreme Points nach der Grundfläche. "
                    "Die Bedingung kostet im jeweils besten Verfahren 0.10 bis 0.40 Behälter über der Schranke "
                    "(Differenz zweier getrennter Stichproben; ein Wert nahe null ist nicht von null zu trennen).")
    zeilen[0] = {**zeilen[0], "ohne": (0, 1, 2), "mit": (0,)}
    text = ev.verdict_stuetz_wahl(zeilen)[1]
    assert "in 4 von 4 Zellen Extreme Points mit Projektionen" in text and "in 3 von 4 Zellen Extreme Points nach der Grundfläche" in text


def test_zeile_rechnet_mittel_anteile_regret_und_gewinner_aus_den_summen():
    d = {"zellen": {ev.zelle_schluessel(1, 0, 0): {"instanzen": 4, "ueber": [4, 6, 2, 2], "beste": [1, 0, 3, 4], "regret": [2, 4, 0, 0]}}}
    z = ev.zeile(1, 0, 0, d)
    assert z["mittel"] == [1.0, 1.5, 0.5, 0.5] and z["beste"] == [25.0, 0.0, 75.0, 100.0] and z["regret"] == [0.5, 1.0, 0.0, 0.0] and z["gewinner"] == (2, 3) and z["n"] == 20 and z["instanzen"] == 4


def test_uebersicht_summiert_ueber_alle_zellen_und_nennt_ein_verfahren_fuer_alles():
    zellen = {}
    for v, ni in ev.zellen_von(2):
        zellen[ev.zelle_schluessel(2, v, ni)] = {"instanzen": 100, "ueber": [100, 50, 20], "beste": [10, 80, 100], "regret": [60, 20, 0]}
    u = ev.uebersicht(2, {"zellen": zellen})
    assert u["instanzen"] == 1200 and u["regret"] == [0.6, 0.2, 0.0] and u["beste"] == [10.0, 80.0, 100.0] and u["mittel"] == [1.0, 0.5, 0.2] and u["ein_verfahren"] == (2,)
    zellen2 = {k: {**z, "regret": [60, 3, 4]} for k, z in zellen.items()}                  # 0,03 und 0,04: nicht gleich
    assert ev.uebersicht(2, {"zellen": zellen2})["ein_verfahren"] == (1,)
    zellen3 = {k: {**z, "regret": [60, 4, 4]} for k, z in zellen.items()}                  # gleich
    assert ev.uebersicht(2, {"zellen": zellen3})["ein_verfahren"] == (1, 2)
    zellen4 = {k: {**z, "regret": [3, 20, 20]} for k, z in zellen.items()}                 # in 2D gibt es die Suche; hier 3D: einfach = alle
    assert ev.uebersicht(2, {"zellen": zellen4})["ein_verfahren_einfach"] == (0,)
