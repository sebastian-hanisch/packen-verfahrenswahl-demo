"""Randfälle: leere Eingabe, ein Teil, Teil gleich Behälter, Gleichstände, ungültige Eingaben, Grenzen der Regler und die Empfehlung der Karte."""

import pytest

import pvw_algorithm as A
import pvw_constants as C
import pvw_evaluation as ev
from pvw_scenario import Instance, beispiel, mess_seed, quelle_instanz, such_seed, zufallsinstanz


def test_leere_eingabe_in_jeder_dimension():
    assert A.pack_1d([], [], 10, 1) == [] and A.l1_1d([], 10) == 0 and A.l2_1d([], 10) == 0 and A.optimum_1d([], 10) == 0 and A.container_pruefen_1d([], [], 10)
    assert A.pack_2d((), [], 10, 2) == ([], []) and A.schranken_2d((), 10) == (0, 0, 0) and A.suche_2d((), 10, 3, 1) == ([], 0) and A.bewerten_2d((), [], 10) == (0, 0)
    assert A.pack_3d((), [], 10, A.EP_VOLL) == ([], []) and A.schranken_3d((), 10) == (0, 0, 0) and A.stuetz_minimum_3d((), []) == 1.0
    assert [A.anzahl_1d([], m, 10) for m in range(5)] == [0] * 5 and [A.anzahl_2d((), m, 10) for m in range(4)] == [0] * 4


@pytest.mark.parametrize("verfahren", range(3))
def test_ein_teil_und_teil_gleich_behaelter(verfahren):
    assert A.pack_2d(((7, 3),), [0], 10, verfahren) == ([[0]], [(0, 0, 0, 0)])
    assert A.pack_2d(((10, 10), (1, 1)), [0, 1], 10, verfahren)[0] == [[0], [1]]
    assert A.pack_3d(((7, 3, 5),), [0], 10, verfahren)[0] == [[0]]
    assert A.pack_3d(((10, 10, 10), (1, 1, 1)), [0, 1], 10, verfahren)[0] == [[0], [1]]
    assert A.pack_1d([10, 1], [0, 1], 10, verfahren) == [[0], [1]]


def test_ein_teil_bei_der_suche_und_gleiche_teile():
    assert A.suche_2d(((7, 3),), 10, 5, 1) == ([0], 1) and A.suche_2d(((5, 5), (5, 5)), 10, 20, 3)[1] == 1
    assert [A.anzahl_1d([5] * 20, m, 10) for m in range(5)] == [10] * 5                     # zehn Behälter zu je zwei Paketen: Gleichstände ändern nichts
    assert [A.anzahl_2d(((5, 5),) * 8, m, 10, 1) for m in range(4)] == [2, 2, 2, 2]


def test_acht_gleiche_wuerfel_fuellen_den_behaelter_genau():
    for verfahren in range(3):
        bins, platz = A.pack_3d(((5, 5, 5),) * 8, list(range(8)), 10, verfahren)
        assert bins == [list(range(8))] and A.packung_pruefen_3d(((5, 5, 5),) * 8, platz, 10)
        assert len(A.pack_3d(((5, 5, 5),) * 9, list(range(9)), 10, verfahren)[0]) == 2


def test_gleichstaende_der_sortierung_bleiben_in_lieferreihenfolge():
    assert A.reihenfolge_1d([5, 3, 5, 3], True) == [0, 2, 1, 3] and A.reihenfolge_1d([5, 3, 5, 3], False) == [0, 1, 2, 3]
    assert A.reihenfolge_2d(((3, 3), (3, 3), (1, 1)), A.FLAECHE_2D) == [0, 1, 2] and A.reihenfolge_2d(((3, 2), (2, 3), (1, 3)), A.HOEHE_2D) == [1, 2, 0]


def test_ungueltige_instanzen_werden_abgelehnt():
    for args in ((0, (0,), 10), (0, (11,), 10), (0, (2.5,), 10), (1, ((1,),), 10), (1, ((1, 11),), 10), (2, ((1, 1),), 10), (2, ((1, 1, 0),), 10), (3, ((1, 1, 1),), 0), (4, (1,), 10)):
        with pytest.raises(ValueError):
            Instance(*args)
    assert Instance(0, (3, 4), 10).n == 2 and Instance(2, ((1, 2, 3),), 10).n == 1


def test_zufallsinstanzen_haben_die_richtige_zahl_und_bleiben_im_bereich():
    for b in C.BEREICHE:
        cap = C.CAP[b]
        for v, (_, _, bereiche) in enumerate(C.VERTEILUNGEN[b]):
            inst = zufallsinstanz(b, v, 25, mess_seed(b, v, 0, 3))
            assert inst.n == 25 and inst.cap == cap and inst == zufallsinstanz(b, v, 25, mess_seed(b, v, 0, 3))
            if b == C.EINS:
                lo, hi = bereiche[0]
                assert all(round(lo * cap) <= s <= round(hi * cap) for s in inst.teile) and all(isinstance(s, int) for s in inst.teile)
            else:
                assert all(bereiche[k][0] <= t[k] <= bereiche[k][1] for t in inst.teile for k in range(len(bereiche)))


def test_mess_seeds_sind_verschieden_und_die_suche_hat_eine_eigene_startzahl():
    seeds = {mess_seed(b, v, ni, j) for b in C.BEREICHE for v in range(4) for ni in range(4) for j in range(200)}
    assert len(seeds) == 4 * 4 * 4 * 200 and such_seed(5) == 53 and such_seed(5) != 5


def test_beispiele_sind_zwoelf_teile_und_n_gilt_nur_fuer_zufallsinstanzen():
    for b in C.BEREICHE:
        assert beispiel(b).n == 12 and quelle_instanz(b, 0, 40, 99) == beispiel(b) and quelle_instanz(b, 1, 20, 5).n == 20


def test_app_n_begrenzt_den_index():
    assert [ev.app_n(0, i) for i in (0, 1, 2, 3, 4, 99, -3)] == [12, 20, 50, 100, 100, 100, 12] and [ev.app_n(1, i) for i in (0, 3, 9)] == [12, 80, 80]


def test_analyse_an_den_grenzen_der_regler():
    for b in C.BEREICHE:
        for q in C.QUELLEN:
            for n_index in range(4):
                for seed in (0, C.SEED_MAX):
                    a = ev.analyse(ev.Settings(b, q, n_index, seed))
                    assert len(a.zaehlungen) == len(C.VERFAHREN[b]) and a.beste and min(a.zaehlungen) >= a.schranke and all(m in a.beste for m in range(len(a.zaehlungen)) if a.zaehlungen[m] == min(a.zaehlungen))
                    assert (a.optimum is None) == (q != 0) and a.empfehlung and a.empfehlung_art in ("Zelle", "alle")


def test_empfehlung_zelle_oder_ein_verfahren_fuer_alles():
    # n = 12 ist keine Zelle der Karte: ein Verfahren für alles; n = 40 mit einer Verteilung des Bereichs ist eine Zelle
    emp, art = ev.empfehlung(1, 0, 12)
    assert art == "alle" and emp == ev.uebersicht(1)["ein_verfahren"]
    emp, art = ev.empfehlung(1, 0, 40)
    assert art == "Zelle" and emp == ev.zeile(1, 0, 1)["gewinner"]
    emp, art = ev.empfehlung(0, None, 20)
    assert art == "alle"                                                                    # das Handbeispiel (ohne Verteilung) hat keine Zelle
    for b in C.BEREICHE:
        assert C.AUSWERTUNGEN[b] and len(C.AUSWERTUNGEN[b]) == len(C.VERFAHREN[b]) == len(C.VERFAHREN_LANG[b])
