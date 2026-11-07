"""Kern an den Mini-Instanzen von Hand und an den Handbeispielen der App (DEMO-PLAYBOOK §1b).

1D, zwölf Pakete 42, 23, 19, 44, 30, 35, 47, 50, 51, 53, 51, 14 (Nummern 0 bis 11), Kapazität 100:
  First Fit, Lieferreihenfolge: 42 -> B1; 23 -> B1 (65); 19 -> B1 (84); 44 -> B2; 30 -> B2 (74); 35 passt weder in B1 (119) noch in B2 (109) -> B3; 47 -> B3 (82); 50 -> B4; 51 -> B5 (B4 hätte 101);
      53 -> B6; 51 -> B7; 14 -> B1 (98). => [[0, 1, 2, 11], [3, 4], [5, 6], [7], [8], [9], [10]]: 7 Behälter.
  Best Fit: wie First Fit bis zum letzten Paket; die 14 hat in B1 den kleinsten Rest (2): ebenfalls 7. Next Fit: 42, 23, 19 | 44, 30 | 35, 47 | 50 | 51 | 53 | 51, 14: 7 Behälter.
  FFD (53, 51, 51, 50, 47, 44, 42, 35, 30, 23, 19, 14): B1 53; B2 51; B3 51; B4 50; 47 -> B1 (100); 44 -> B2 (95); 42 -> B3 (93); 35 -> B4 (85); 30 passt nirgends -> B5; 23 -> B5 (53); 19 -> B5 (72);
      14 -> B4 (99). => 5 Behälter, Füllungen 100, 95, 93, 99, 72. BFD: dieselben Füllungen. L1 = ceil(459 / 100) = 5 = L2 = Optimum.
2D, vier Rechtecke (6,4), (5,3), (4,5), (4,2) mit den Nummern 0 bis 3, Behälter 10 mal 10, Reihenfolge 0, 1, 2, 3 (von Hand aus Stück 8 übernommen und hier nachgerechnet):
  Regal: 0 -> Regal 0 (Höhe 4, Breite 6); 1 -> 6 + 5 > 10, neues Regal bei y = 4 (Höhe 3); 2 (4,5) -> beide Regale zu niedrig, neues Regal bei y = 7: 7 + 5 > 10, neuer Behälter; 3 (4,2) -> Regal 0 (6 + 4 = 10).
      => [[0, 1, 3], [2]]. Skyline: (0,0), (0,4), (6,0), (5,5). MaxRects BSSF: (0,0), (0,4), (6,0), (5,5): ein Behälter.
  Nach Höhe sortiert (2, 0, 1, 3) braucht das Regal einen Behälter: 2 (4,5) -> Regal 0 (Höhe 5, Breite 4); 0 (6,4) -> 4 + 6 = 10, dasselbe Regal; 1 (5,3) -> Regal 0 ist voll, neues Regal bei y = 5 (5 + 3 <= 10);
      3 (4,2) -> Regal 1 (Breite 5 + 4 = 9).
3D, vier Quader (4,4,2), (2,5,8), (7,5,2), (4,8,2), Behälter 10 mal 10 mal 10, Reihenfolge 0, 1, 2, 3 (aus Stück 9 übernommen und hier nachgerechnet):
  Extreme Points mit Projektionen: 0 -> (0,0,0); 1 (2,5,8) -> (4,0,0); die Ecke (4,5,0) von Quader 1 projiziert in -x bis zur Wand auf (0,5,0), dort liegt Quader 2 (7,5,2); 3 (4,8,2) -> (0,0,2): ein Behälter.
  Ohne Projektionen: Quader 2 findet keinen Punkt ((6,0,0) und (4,5,0) sind zu breit, (0,0,2) überlappt Quader 1, (4,0,8) ist zu breit) und öffnet Behälter 1; Quader 3 passt in Behälter 0 an (6,0,0)
  (x 6 bis 10, y 0 bis 8, Quader 1 endet bei x = 6): [[0, 1, 3], [2]].
  Schichten: 0 -> Schicht 0 (z = 0, Höhe 2, Regal 0 Tiefe 4); 1 (2,5,8) ist höher als Schicht 0: neue Schicht bei z = 2 (2 + 8 = 10); 2 (7,5,2) -> Schicht 0, Regal 0 hat Tiefe 4 < 5, neues Regal bei y = 4;
  3 (4,8,2) passt in keine Schicht (neue Regale bei y = 9 und y = 5 überschreiten die Tiefe, eine dritte Schicht die Höhe) -> Behälter 1: [[0, 1, 2], [3]].
Stützfläche (Mini-Instanz (2,8,2), (4,7,4), (3,8,6), (4,8,3)): Quader 3 bei (0,0,4) liegt auf Quader 1 (x 2 bis 4, y 0 bis 7: 14 von 32 = 43,75 %); mit s >= 0,8 bei (2,0,4) (28 von 32 = 87,5 %); mit s = 1 in einem neuen Behälter."""

import pytest

import pvw_algorithm as A


# --- 1D ---------------------------------------------------------------------------------------------------------------------------------------


def test_1d_regeln_auf_den_zwoelf_paketen_von_hand(mini_1d):
    sizes, cap = mini_1d
    lief = A.reihenfolge_1d(sizes, False)
    assert A.pack_1d(sizes, lief, cap, 1) == [[0, 1, 2, 11], [3, 4], [5, 6], [7], [8], [9], [10]]
    assert A.pack_1d(sizes, lief, cap, 2) == [[0, 1, 2, 11], [3, 4], [5, 6], [7], [8], [9], [10]]
    assert A.pack_1d(sizes, lief, cap, 0) == [[0, 1, 2], [3, 4], [5, 6], [7], [8], [9], [10, 11]]
    absteigend = A.reihenfolge_1d(sizes, True)
    assert absteigend == [9, 8, 10, 7, 6, 3, 0, 5, 4, 1, 2, 11]
    ffd, bfd = A.pack_1d(sizes, absteigend, cap, 1), A.pack_1d(sizes, absteigend, cap, 2)
    for bins in (ffd, bfd):
        assert len(bins) == 5 and sorted(sum(sizes[i] for i in b) for b in bins) == [72, 93, 95, 99, 100]
    assert ffd == [[9, 6], [8, 3], [10, 0], [7, 5, 11], [4, 1, 2]]
    assert [A.anzahl_1d(sizes, m, cap) for m in range(5)] == [7, 7, 7, 5, 5]


def test_1d_schranken_und_optimum_der_zwoelf_pakete(mini_1d):
    sizes, cap = mini_1d
    assert A.l1_1d(sizes, cap) == 5 and A.l2_1d(sizes, cap) == 5 and A.optimum_1d(sizes, cap) == 5
    assert A.container_pruefen_1d(sizes, A.pack_1d(sizes, A.reihenfolge_1d(sizes, True), cap, 1), cap)
    assert A.optimum_1d(sizes + (1,), cap) is None and A.optimum_1d((), cap) == 0 and A.l1_1d([], cap) == 0 and A.l2_1d([], cap) == 0


def test_1d_l2_ist_staerker_als_l1_bei_grossen_paketen():
    # drei Pakete über der Hälfte brauchen drei Behälter, obwohl die Summe (51 + 51 + 51 = 153) nur zwei verlangt; ein viertes kleines füllt den Rest nicht
    assert A.l1_1d([51, 51, 51], 100) == 2 and A.l2_1d([51, 51, 51], 100) == 3
    assert A.l2_1d([60, 60, 20, 20, 20, 20], 100) == 2 == A.l1_1d([60, 60, 20, 20, 20, 20], 100)          # die vier kleinen füllen genau den Rest beider Behälter


def test_1d_pruefer_erkennt_fehler(mini_1d):
    sizes, cap = mini_1d
    gut = A.pack_1d(sizes, A.reihenfolge_1d(sizes, True), cap, 1)
    assert A.container_pruefen_1d(sizes, gut, cap)
    assert not A.container_pruefen_1d(sizes, gut[:-1], cap) and not A.container_pruefen_1d(sizes, gut + [[]], cap)
    assert not A.container_pruefen_1d(sizes, [[0, 1, 2, 3]] + gut[1:], cap) and not A.container_pruefen_1d(sizes, [[i for b in gut for i in b]], cap)


def test_1d_ungueltige_eingaben_werden_abgelehnt():
    for args in (((5, 5), [0, 0], 10, 1), ((5, 5), [0], 10, 1), ((0, 5), [0, 1], 10, 1), ((11, 5), [0, 1], 10, 1), ((5, 5), [0, 1], 10, 3)):
        with pytest.raises(ValueError):
            A.pack_1d(*args)


# --- 2D ---------------------------------------------------------------------------------------------------------------------------------------


def test_2d_verfahren_auf_der_mini_instanz_von_hand(mini_2d):
    rects, cap = mini_2d
    bins, platz = A.pack_2d(rects, [0, 1, 2, 3], cap, 0)
    assert bins == [[0, 1, 3], [2]] and sorted(platz) == [(0, 0, 0, 0), (1, 0, 0, 4), (2, 1, 0, 0), (3, 0, 6, 0)]
    bins, platz = A.pack_2d(rects, [0, 1, 2, 3], cap, 1)
    assert bins == [[0, 1, 2, 3]] and sorted(platz) == [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 6, 0), (3, 0, 5, 5)]
    bins, platz = A.pack_2d(rects, [0, 1, 2, 3], cap, 2)
    assert bins == [[0, 1, 2, 3]] and sorted(platz) == [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 6, 0), (3, 0, 5, 5)]
    bins, platz = A.pack_2d(rects, A.reihenfolge_2d(rects, A.HOEHE_2D), cap, 0)                # 2, 0, 1, 3
    assert A.reihenfolge_2d(rects, A.HOEHE_2D) == [2, 0, 1, 3] and bins == [[2, 0, 1, 3]] and sorted(platz) == [(0, 0, 4, 0), (1, 0, 0, 5), (2, 0, 0, 0), (3, 0, 5, 5)]
    assert [A.anzahl_2d(rects, m, cap, 1) for m in range(4)] == [1, 1, 1, 1] and A.schranken_2d(rects, cap) == (1, 0, 1)
    assert A.reihenfolge_2d(rects, A.FLAECHE_2D) == [0, 2, 1, 3] and A.reihenfolge_2d(rects, 0) == [0, 1, 2, 3]


def test_2d_zufall_und_suche_von_hand():
    import random

    assert random.Random(1).random() == pytest.approx(0.13436424411240122)
    assert A.Zufall(1).unter(10) == 1 and A.Zufall(1).paar(4) == (0, 3)            # 0,134 * 4 = 0; 0,847 * 3 = 2, weil 2 >= 0 wird 3
    rects = ((5, 4), (9, 2), (3, 5), (3, 2))
    # Reihenfolge nach Fläche 0, 1, 2, 3: 0 -> (0,0), 1 -> (0,4), 2 (3,5) passt in keinen freien Platz des ersten Behälters -> Behälter 2, 3 -> Behälter 1: zwei Behälter, leerster Behälter 15.
    # Der erste Tausch der Startzahl 1 ist (0, 3): Reihenfolge 3, 1, 2, 0 passt in einen Behälter (Fläche 59).
    assert A.bewerten_2d(rects, [0, 1, 2, 3], 10) == (2, 15) and A.bewerten_2d(rects, [3, 1, 2, 0], 10) == (1, 59)
    assert A.suche_2d(rects, 10, 2, 1) == ([3, 1, 2, 0], 1) and A.suche_2d(rects, 10, 1, 1) == ([0, 1, 2, 3], 2)
    assert A.anzahl_2d(rects, 3, 10, 1) == 1 and A.anzahl_2d(rects, 2, 10) == 2


def test_2d_suche_ist_deterministisch_und_nie_schlechter_als_der_start():
    import random

    rng = random.Random(4)
    for _ in range(6):
        rects = tuple((rng.randint(10, 60), rng.randint(10, 60)) for _ in range(rng.randint(2, 14)))
        start = A.anzahl_2d(rects, 2, 100)
        beste, anzahl = A.suche_2d(rects, 100, 60, 5)
        assert (beste, anzahl) == A.suche_2d(rects, 100, 60, 5) and sorted(beste) == list(range(len(rects))) and anzahl <= start
        assert anzahl == A.bewerten_2d(rects, beste, 100)[0] >= A.schranken_2d(rects, 100)[2]


def test_2d_pruefer_und_ungueltige_eingaben(mini_2d):
    rects, cap = mini_2d
    gut = [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 6, 0), (3, 0, 5, 5)]
    assert A.packung_pruefen_2d(rects, gut, cap) and not A.packung_pruefen_2d(rects, gut[:3], cap) and A.packung_pruefen_2d(rects, gut[:3], cap, vollstaendig=False)
    assert not A.packung_pruefen_2d(rects, gut + [(0, 1, 0, 0)], cap) and not A.packung_pruefen_2d(rects, [(0, 0, 0, 0), (1, 0, 0, 3), (2, 0, 6, 0), (3, 0, 5, 5)], cap)
    assert not A.packung_pruefen_2d(rects, [(0, 0, 6, 0), (1, 0, 0, 4), (2, 0, 6, 5), (3, 0, 5, 5)], cap) and not A.packung_pruefen_2d(rects, [(0, 0, -1, 0)] + gut[1:], cap)
    for args in ((rects, [0, 0], cap, 0), (rects, [4], cap, 0), (((11, 3),), [0], cap, 0), (((0, 3),), [0], cap, 0), (((3, 3, 3),), [0], cap, 0), (rects, [0], cap, 3)):
        with pytest.raises(ValueError):
            A.pack_2d(*args)
    with pytest.raises(ValueError):
        A.suche_2d(rects, cap, 0, 1)
    with pytest.raises(ValueError):
        A.anzahl_2d(rects, 4, cap)


# --- 3D ---------------------------------------------------------------------------------------------------------------------------------------


def test_3d_verfahren_auf_der_mini_instanz_von_hand(mini_3d):
    kisten, cap = mini_3d
    bins, platz = A.pack_3d(kisten, [0, 1, 2, 3], cap, A.EP_VOLL)
    assert bins == [[0, 1, 2, 3]] and platz == [(0, 0, 0, 0, 0), (1, 0, 4, 0, 0), (2, 0, 0, 5, 0), (3, 0, 0, 0, 2)]
    bins, platz = A.pack_3d(kisten, [0, 1, 2, 3], cap, A.EP_EINFACH)
    assert bins == [[0, 1, 3], [2]] and platz == [(0, 0, 0, 0, 0), (1, 0, 4, 0, 0), (2, 1, 0, 0, 0), (3, 0, 6, 0, 0)]
    bins, platz = A.pack_3d(kisten, [0, 1, 2, 3], cap, A.SCHICHTEN)
    assert bins == [[0, 1, 2], [3]] and platz == [(0, 0, 0, 0, 0), (1, 0, 0, 0, 2), (2, 0, 0, 4, 0), (3, 1, 0, 0, 0)]
    assert A.schranken_3d(kisten, cap) == (1, 0, 1) and A.schranken_3d(((6, 6, 6),) * 3, 10) == (1, 3, 3) and A.schranken_3d(((10, 10, 10), (10, 10, 10), (1, 1, 1)), 10) == (3, 2, 3)


def test_3d_stuetzflaeche_auf_der_mini_instanz_von_hand(mini_3d_stuetz):
    kisten, cap = mini_3d_stuetz
    ohne = A.pack_3d(kisten, [0, 1, 2, 3], cap, A.EP_VOLL)
    assert ohne[0] == [[0, 1, 2, 3]] and ohne[1][3] == (3, 0, 0, 0, 4) and A.stuetzflaeche_3d(kisten, ohne[1], 3) == 14 / 32 and A.stuetz_minimum_3d(kisten, ohne[1]) == 14 / 32
    mit80 = A.pack_3d(kisten, [0, 1, 2, 3], cap, A.EP_VOLL, 0.8)
    assert mit80[0] == [[0, 1, 2, 3]] and mit80[1][3] == (3, 0, 2, 0, 4) and A.stuetzflaeche_3d(kisten, mit80[1], 3) == 28 / 32
    mit100 = A.pack_3d(kisten, [0, 1, 2, 3], cap, A.EP_VOLL, 1.0)
    assert mit100[0] == [[0, 1, 2], [3]] and mit100[1][3] == (3, 1, 0, 0, 0) and A.stuetz_minimum_3d(kisten, mit100[1]) == 1.0
    assert A.anzahl_3d(kisten, A.EP_VOLL, 0, cap, 0.0) == 1 and A.anzahl_3d(kisten, A.EP_VOLL, 0, cap, 1.0) == 2


def test_3d_stuetzflaeche_grenzen():
    kisten = ((10, 10, 2), (4, 4, 2), (4, 4, 2))
    platz = [(0, 0, 0, 0, 0), (1, 0, 0, 0, 2), (2, 0, 0, 5, 6)]                            # Quader 2 schwebt
    assert [A.stuetzflaeche_3d(kisten, platz, i) for i in (0, 1, 2)] == [1.0, 1.0, 0.0] and A.stuetz_minimum_3d(kisten, platz) == 0.0 and A.stuetz_minimum_3d((), []) == 1.0
    kisten2 = ((8, 10, 2), (5, 4, 2))                                                      # 16 von 20 = 80 %
    assert A.stuetzflaeche_3d(kisten2, [(0, 0, 0, 0, 0), (1, 0, 4, 0, 2)], 1) == 0.8
    assert A.stuetzflaeche_3d(((10, 10, 2), (4, 4, 2)), [(0, 0, 0, 0, 0), (1, 1, 0, 0, 2)], 1) == 0.0                 # anderer Behälter trägt nicht
    assert A.stuetzflaeche_3d(((10, 10, 2), (4, 4, 2)), [(0, 0, 0, 0, 0), (1, 0, 0, 0, 3)], 1) == 0.0                 # andere Höhe trägt nicht


def test_3d_pruefer_und_ungueltige_eingaben(mini_3d):
    kisten, cap = mini_3d
    gut = [(0, 0, 0, 0, 0), (1, 0, 4, 0, 0), (2, 0, 0, 5, 0), (3, 0, 0, 0, 2)]
    assert A.packung_pruefen_3d(kisten, gut, cap) and not A.packung_pruefen_3d(kisten, gut[:3], cap) and A.packung_pruefen_3d(kisten, gut[:3], cap, vollstaendig=False)
    assert not A.packung_pruefen_3d(kisten, gut + [(0, 1, 0, 0, 0)], cap) and not A.packung_pruefen_3d(kisten, [(0, 0, 0, 0, 0), (1, 0, 3, 0, 0), (2, 0, 0, 5, 0), (3, 0, 0, 0, 2)], cap)
    assert not A.packung_pruefen_3d(kisten, [(0, 0, 0, 0, 0), (1, 0, 4, 0, 3), (2, 0, 0, 5, 0), (3, 0, 0, 0, 2)], cap) and not A.packung_pruefen_3d(kisten, [(0, 0, -1, 0, 0)] + gut[1:], cap)
    assert A.packung_pruefen_3d(kisten, [(0, 0, 0, 0, 0), (1, 0, 4, 0, 0), (2, 0, 0, 5, 0), (3, 1, 0, 0, 0)], cap)                       # Berührung ist keine Überlappung, anderer Behälter
    for args, kw in (((kisten, [0, 0], cap, A.EP_VOLL), {}), ((kisten, [4], cap, A.EP_VOLL), {}), ((((11, 3, 3),), [0], cap, A.EP_VOLL), {}), ((((0, 3, 3),), [0], cap, A.EP_VOLL), {}),
                     ((((3, 3),), [0], cap, A.EP_VOLL), {}), ((kisten, [0], cap, 3), {}), ((kisten, [0], cap, A.EP_VOLL), {"s_min": 1.5}), ((kisten, [0], cap, A.SCHICHTEN), {"s_min": 0.5})):
        with pytest.raises(ValueError):
            A.pack_3d(*args, **kw)


def test_3d_reihenfolge_je_schluessel_mit_gleichstaenden_in_lieferreihenfolge(mini_3d):
    k, _ = mini_3d                       # Volumen 32, 80, 70, 64; Grundfläche 16, 10, 35, 32; Höhe 2, 8, 2, 2
    assert A.reihenfolge_3d(k, 0) == [0, 1, 2, 3] and A.reihenfolge_3d(k, A.VOLUMEN_3D) == [1, 2, 3, 0]
    assert A.reihenfolge_3d(k, A.GRUNDFLAECHE_3D) == [2, 3, 0, 1] and A.reihenfolge_3d(k, A.HOEHE_3D) == [1, 0, 2, 3]
    assert A.reihenfolge_3d(((3, 3, 3), (3, 3, 3), (1, 1, 1), (3, 3, 3)), A.VOLUMEN_3D) == [0, 1, 3, 2]
