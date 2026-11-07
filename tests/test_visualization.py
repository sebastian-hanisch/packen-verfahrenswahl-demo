"""Abbildungen: die Balken einer Instanz, die Karte als Wärmebild und der Regret; alle Achsen sind gesperrt."""

import pvw_constants as C
import pvw_evaluation as ev
import pvw_visualization as V


def test_instanzbalken_markieren_beste_und_empfehlung():
    fig = V.build_instanz(0, (7, 7, 7, 5, 5), 5, (3, 4), (3, 4))
    balken = fig.data[0]
    assert list(balken.x) == ["NF", "FF", "BF", "FFD ★", "BFD ★"] and list(balken.y) == [7, 7, 7, 5, 5]
    assert list(balken.marker.color) == ["rgba(150,150,150,0.55)"] * 3 + [C.VERFAHREN_FARBEN[3], C.VERFAHREN_FARBEN[4]]
    assert fig.layout.shapes[0].y0 == 5 and fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange


def test_instanzbalken_zur_analyse_der_app_fuer_jeden_bereich():
    for b in C.BEREICHE:
        a = ev.analyse(ev.Settings(b))
        fig = V.build_instanz(b, a.zaehlungen, a.schranke, a.beste, a.empfehlung)
        assert len(fig.data[0].x) == len(C.VERFAHREN[b]) and list(fig.data[0].y) == list(a.zaehlungen)


def test_karte_hat_je_zelle_eine_zeile_und_markiert_die_gewinner():
    mittel = [[0.74, 0.76, 0.57, 0.42], [1.13, 1.33, 1.13, 0.78]]
    fig = V.build_karte(1, ["mittel, n = 20", "mittel, n = 40"], mittel, [(3,), (3,)])
    h = fig.data[0]
    assert list(h.x) == list(C.VERFAHREN[1]) and list(h.y) == ["mittel, n = 20", "mittel, n = 40"] and [list(r) for r in h.z] == mittel
    assert [list(r) for r in h.text] == [["0.74", "0.76", "0.57", "0.42 ★"], ["1.13", "1.33", "1.13", "0.78 ★"]]
    assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange and fig.layout.yaxis.autorange == "reversed"


def test_karte_zur_echten_karte_jedes_bereichs():
    for b in C.BEREICHE:
        zeilen = [ev.zeile(b, v, ni) for v, ni in ev.zellen_von(b)]
        fig = V.build_karte(b, [str(i) for i in range(len(zeilen))], [z["mittel"] for z in zeilen], [z["gewinner"] for z in zeilen])
        assert len(fig.data[0].y) == len(zeilen) == 4 * len(C.MESS_N[b])


def test_regret_balken_haben_zwei_achsen():
    fig = V.build_regret(2, [0.72, 0.2, 0.02], [38.0, 80.0, 98.0])
    assert [t.name for t in fig.data] == ["mittlerer Regret (Behälter)", "Anteil bester Instanzen (%)"] and list(fig.data[0].y) == [0.72, 0.2, 0.02] and fig.data[1].yaxis == "y2"
    assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange
