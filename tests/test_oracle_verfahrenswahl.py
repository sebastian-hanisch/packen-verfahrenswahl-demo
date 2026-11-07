"""Orakel-Tests (DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg, feste Seeds, zusammen unter 30 Sekunden.

  1D  First, Best und Next Fit      gegen  naive Umsetzungen, die die Füllung jedes Behälters vor jedem Paket neu aus den Listen summieren; L1 <= L2 <= Optimum (Teilmengen-DP) und jedes Verfahren >= Optimum;
      L2 gegen eine Brute-Force-Rechnung über alle ganzzahligen alpha.
  2D  MaxRects BSSF                 gegen  eine Umsetzung, die in jedem Schritt ALLE maximalen leeren Rechtecke nach Definition aus einem Belegungsraster aufzählt (kleine Behälter); Skyline gegen das Profil,
      jedes Mal neu aus der Liste der gesetzten Rechtecke gelesen; Regal gegen eine naive Neuberechnung.
  3D  Extreme Points (einfach, voll, mit Mindest-Stützfläche)  gegen  eine Umsetzung, die die Eckpunkte nach jedem Quader aus der Liste der gesetzten Quader NEU erzeugt und die Stützfläche aus einem
      Voxelraster liest; Schichten gegen eine naive Neuberechnung.
  Optimum (CP-SAT)  2D und 3D gegen die Behälterzahlen der Verfahren (nie darüber), in tests/test_claims.py für die Handbeispiele.
  Eigenschaften:  jede Packung zulässig und nie unter der Schranke, gemeinsames Skalieren, Anfang der Reihenfolge ist Anfang der Packung.
"""

import itertools
import random

import pytest

import pvw_algorithm as A


# --- 1D ---------------------------------------------------------------------------------------------------------------------------------------


def regel_naiv(sizes, order, cap, regel):
    bins = []
    for i in order:
        s = sizes[i]
        kandidaten = [b for b in range(len(bins)) if sum(sizes[j] for j in bins[b]) + s <= cap]
        if regel == 0:
            kandidaten = [b for b in kandidaten if b == len(bins) - 1]
        if not kandidaten:
            bins.append([i])
            continue
        if regel == 2:
            ziel = min(kandidaten, key=lambda b: (cap - sum(sizes[j] for j in bins[b]) - s, b))
        else:
            ziel = kandidaten[0]
        bins[ziel].append(i)
    return bins


def instanzen_1d(anzahl, n_lo, n_hi, cap_lo=10, cap_hi=100, seed0=0):
    for seed in range(seed0, seed0 + anzahl):
        rng = random.Random(seed)
        cap = rng.randint(cap_lo, cap_hi)
        yield cap, [rng.randint(1, cap) for _ in range(rng.randint(n_lo, n_hi))]


def test_1d_regeln_gegen_die_naive_neuberechnung():
    for cap, sizes in instanzen_1d(60, 1, 30, seed0=100):
        for absteigend in (False, True):
            order = A.reihenfolge_1d(sizes, absteigend)
            for regel in (0, 1, 2):
                assert A.pack_1d(sizes, order, cap, regel) == regel_naiv(sizes, order, cap, regel), (cap, sizes, absteigend, regel)


def l2_brute_force(sizes, cap):
    """L2 über alle ganzzahligen alpha von 0 bis cap / 2 (statt nur über die vorkommenden Größen): dasselbe Maximum."""
    best = -(-sum(sizes) // cap) if sizes else 0
    for alpha in range(0, cap // 2 + 1):
        j1 = [s for s in sizes if s > cap - alpha]
        j2 = [s for s in sizes if cap - alpha >= s and 2 * s > cap]
        j3 = [s for s in sizes if 2 * s <= cap and s >= alpha]
        frei = len(j2) * cap - sum(j2)
        best = max(best, len(j1) + len(j2) + (max(0, -(-(sum(j3) - frei) // cap)) if j3 else 0))
    return best


def test_1d_schranken_gegen_brute_force_und_optimum():
    for cap, sizes in instanzen_1d(60, 1, 10, cap_lo=10, cap_hi=40, seed0=300):
        opt = A.optimum_1d(sizes, cap)
        assert A.l2_1d(sizes, cap) == l2_brute_force(sizes, cap) and A.l1_1d(sizes, cap) <= A.l2_1d(sizes, cap) <= opt, (cap, sizes)
        for m in range(5):
            assert A.anzahl_1d(sizes, m, cap) >= opt
    # Optimum gegen Aufzählung aller Zuordnungen zu höchstens n Behältern (n <= 6)
    for cap, sizes in instanzen_1d(15, 1, 6, cap_lo=10, cap_hi=30, seed0=400):
        n = len(sizes)
        beste = min(len(set(z)) for z in itertools.product(range(n), repeat=n) if all(sum(sizes[i] for i in range(n) if z[i] == b) <= cap for b in set(z)))
        assert A.optimum_1d(sizes, cap) == beste


# --- 2D ---------------------------------------------------------------------------------------------------------------------------------------


def instanzen_2d(anzahl, n_lo, n_hi, cap_lo=10, cap_hi=40, seed0=0):
    for seed in range(seed0, seed0 + anzahl):
        rng = random.Random(seed)
        cap = rng.randint(cap_lo, cap_hi)
        yield cap, tuple((rng.randint(1, cap), rng.randint(1, cap)) for _ in range(rng.randint(n_lo, n_hi)))


def belegung(gesetzt, cap):
    return [[any(x <= c < x + w and y <= r < y + h for (x, y, w, h) in gesetzt) for c in range(cap)] for r in range(cap)]


def maximale_leere(gesetzt, cap):
    """Alle maximalen leeren Rechtecke (x, y, w, h) nach Definition: leer und in keiner der vier Richtungen um eine Zelle erweiterbar."""
    raster = belegung(gesetzt, cap)

    def leer(x, y, w, h):
        return all(not raster[r][c] for r in range(y, y + h) for c in range(x, x + w))

    gefunden = []
    for x in range(cap):
        for y in range(cap):
            for w in range(1, cap - x + 1):
                for h in range(1, cap - y + 1):
                    if not leer(x, y, w, h):
                        break
                    if not ((x > 0 and leer(x - 1, y, 1, h)) or (x + w < cap and leer(x + w, y, 1, h)) or (y > 0 and leer(x, y - 1, w, 1)) or (y + h < cap and leer(x, y + h, w, 1))):
                        gefunden.append((x, y, w, h))
    return gefunden


def maxrects_naiv(rects, order, cap):
    gesetzt, platz = [], []
    for i in order:
        w, h = rects[i]
        wahl = None
        for b, lst in enumerate(gesetzt):
            for (fx, fy, fw, fh) in maximale_leere(lst, cap):
                if w <= fw and h <= fh:
                    score = (min(fw - w, fh - h), max(fw - w, fh - h), fy, fx)
                    if wahl is None or score < wahl[0]:
                        wahl = (score, b, fx, fy)
            if wahl is not None:
                break
        if wahl is None:
            gesetzt.append([])
            wahl = (None, len(gesetzt) - 1, 0, 0)
        _, b, x, y = wahl
        gesetzt[b].append((x, y, w, h))
        platz.append((i, b, x, y))
    return platz


def skyline_naiv(rects, order, cap):
    gesetzt, platz = [], []
    for i in order:
        w, h = rects[i]
        wahl = None
        for b, lst in enumerate(gesetzt):
            def hoehe(x):
                return max([y + hh for (xx, y, ww, hh) in lst if xx < x + 1 and x < xx + ww] + [0])
            kandidaten = [(max(hoehe(c) for c in range(x, x + w)), x) for x in range(cap - w + 1)]
            kandidaten = [(y, x) for y, x in kandidaten if y + h <= cap]
            if kandidaten:
                y, x = min(kandidaten)
                wahl = (b, x, y)
                break
        if wahl is None:
            gesetzt.append([])
            wahl = (len(gesetzt) - 1, 0, 0)
        b, x, y = wahl
        gesetzt[b].append((x, y, w, h))
        platz.append((i, b, x, y))
    return platz


def regal_naiv(rects, order, cap):
    behaelter = []
    for i in order:
        w, h = rects[i]
        platziert = False
        for b in range(len(behaelter)):
            for sh in behaelter[b]:
                if h <= rects[sh["teile"][0]][1] and sum(rects[t][0] for t in sh["teile"]) + w <= cap:
                    sh["teile"].append(i)
                    platziert = True
                    break
            if platziert:
                break
        if platziert:
            continue
        for b in range(len(behaelter)):
            if sum(rects[sh["teile"][0]][1] for sh in behaelter[b]) + h <= cap:
                behaelter[b].append({"teile": [i]})
                platziert = True
                break
        if not platziert:
            behaelter.append([{"teile": [i]}])
    return [[t for sh in b for t in sh["teile"]] for b in behaelter]


def test_2d_skyline_und_maxrects_gegen_die_naiven_umsetzungen():
    for cap, rects in instanzen_2d(30, 1, 12, cap_lo=8, cap_hi=14, seed0=500):
        for schluessel in (A.HOEHE_2D, A.FLAECHE_2D):
            order = A.reihenfolge_2d(rects, schluessel)
            assert A.pack_2d(rects, order, cap, 1)[1] == skyline_naiv(rects, order, cap), (cap, rects, schluessel)
            assert A.pack_2d(rects, order, cap, 2)[1] == maxrects_naiv(rects, order, cap), (cap, rects, schluessel)


def test_2d_regal_gegen_die_naive_neuberechnung():
    for cap, rects in instanzen_2d(40, 1, 25, cap_lo=10, cap_hi=100, seed0=700):
        for schluessel in (0, A.HOEHE_2D, A.FLAECHE_2D):
            order = A.reihenfolge_2d(rects, schluessel)
            bins, _ = A.pack_2d(rects, order, cap, 0)
            assert sorted(sorted(b) for b in bins) == sorted(sorted(b) for b in regal_naiv(rects, order, cap)), (cap, rects, schluessel)


def test_2d_alle_packungen_sind_zulaessig_und_nie_unter_der_schranke():
    for cap, rects in instanzen_2d(30, 1, 25, cap_lo=10, cap_hi=100, seed0=900):
        for verfahren in range(3):
            for schluessel in (0, A.HOEHE_2D, A.FLAECHE_2D):
                bins, platz = A.pack_2d(rects, A.reihenfolge_2d(rects, schluessel), cap, verfahren)
                assert A.packung_pruefen_2d(rects, platz, cap) and len(bins) >= A.schranken_2d(rects, cap)[2], (cap, rects, verfahren, schluessel)
        assert A.anzahl_2d(rects, 3, cap, 7) <= A.anzahl_2d(rects, 2, cap)                      # die Suche startet bei MaxRects nach Fläche und wird nie schlechter


def test_2d_zustand_ist_der_anfang_der_packung():
    for cap, rects in instanzen_2d(15, 2, 12, cap_lo=10, cap_hi=40, seed0=1100):
        order = A.reihenfolge_2d(rects, A.FLAECHE_2D)
        for verfahren in range(3):
            voll = A.pack_2d(rects, order, cap, verfahren)[1]
            for k in range(len(order) + 1):
                assert A.pack_2d(rects, order[:k], cap, verfahren)[1] == voll[:k]


# --- 3D ---------------------------------------------------------------------------------------------------------------------------------------


def instanzen_3d(anzahl, n_lo, n_hi, cap_lo=10, cap_hi=24, seed0=0, kante_hi=None):
    for seed in range(seed0, seed0 + anzahl):
        rng = random.Random(seed)
        cap = rng.randint(cap_lo, cap_hi)
        n = rng.randint(n_lo, n_hi)
        yield cap, tuple(tuple(rng.randint(1, min(kante_hi or cap, cap)) for _ in range(3)) for _ in range(n))


def innen(p, q):
    return q[0] <= p[0] < q[0] + q[3] and q[1] <= p[1] < q[1] + q[4] and q[2] <= p[2] < q[2] + q[5]


def projektion(p, achse, davor):
    a, b = [k for k in range(3) if k != achse]
    kandidaten = [0] + [q[achse] + q[3 + achse] for q in davor if q[achse] + q[3 + achse] <= p[achse] and q[a] <= p[a] < q[a] + q[3 + a] and q[b] <= p[b] < q[b] + q[3 + b]]
    return max(kandidaten)


def eckpunkte_neu(gesetzt, cap, voll):
    punkte = {(0, 0, 0)}
    for s, q in enumerate(gesetzt):
        x, y, z, w, d, h = q
        for p, achsen in (((x + w, y, z), (1, 2)), ((x, y + d, z), (0, 2)), ((x, y, z + h), (0, 1))):
            punkte.add(p)
            if voll:
                for a in achsen:
                    r = list(p)
                    r[a] = projektion(p, a, gesetzt[:s])
                    punkte.add(tuple(r))
    return sorted((p for p in punkte if max(p) < cap and not any(innen(p, q) for q in gesetzt)), key=lambda p: (p[2], p[1], p[0]))


def stuetz_voxel(quader, gesetzt):
    x0, y0, z0, w, d, _h = quader
    if z0 == 0:
        return 1.0
    belegt = sum(1 for x in range(x0, x0 + w) for y in range(y0, y0 + d) if any(q[0] <= x < q[0] + q[3] and q[1] <= y < q[1] + q[4] and q[2] <= z0 - 1 < q[2] + q[5] for q in gesetzt))
    return belegt / (w * d)


def ep_naiv(kisten, order, cap, voll, s_min):
    behaelter, platz = [], []
    for i in order:
        w, d, h = kisten[i]
        wahl = None
        for b, lst in enumerate(behaelter):
            for (x, y, z) in eckpunkte_neu(lst, cap, voll):
                k = (x, y, z, w, d, h)
                if x + w <= cap and y + d <= cap and z + h <= cap and not any(A._ueberlappt(k, q) for q in lst) and (s_min == 0 or stuetz_voxel(k, lst) >= s_min - 1e-9):
                    wahl = (b, x, y, z)
                    break
            if wahl:
                break
        if wahl is None:
            behaelter.append([])
            wahl = (len(behaelter) - 1, 0, 0, 0)
        b, x, y, z = wahl
        behaelter[b].append((x, y, z, w, d, h))
        platz.append((i, b, x, y, z))
    return platz


def schichten_naiv(kisten, order, cap):
    platz = []

    def lagen(b):
        out = []
        for z in sorted({p[4] for p in platz if p[1] == b}):
            erster = next(p for p in platz if p[1] == b and p[4] == z)
            out.append((z, kisten[erster[0]][2]))
        return out

    def regale(b, z):
        out = []
        for y in sorted({p[3] for p in platz if p[1] == b and p[4] == z}):
            im = [p for p in platz if p[1] == b and p[4] == z and p[3] == y]
            out.append((y, kisten[im[0][0]][1], sum(kisten[p[0]][0] for p in im)))
        return out

    anzahl_b = 0
    for i in order:
        w, d, h = kisten[i]
        wahl = None
        for b in range(anzahl_b):
            for z, hoehe in lagen(b):
                if h > hoehe:
                    continue
                rs = regale(b, z)
                for y, tiefe, belegt in rs:
                    if d <= tiefe and belegt + w <= cap:
                        wahl = (b, belegt, y, z)
                        break
                if wahl:
                    break
                y0 = sum(r[1] for r in rs)
                if y0 + d <= cap:
                    wahl = (b, 0, y0, z)
                    break
            if wahl:
                break
            z0 = sum(hh for _, hh in lagen(b))
            if z0 + h <= cap:
                wahl = (b, 0, 0, z0)
                break
        if wahl is None:
            wahl = (anzahl_b, 0, 0, 0)
            anzahl_b += 1
        b, x, y, z = wahl
        platz.append((i, b, x, y, z))
    return platz


@pytest.mark.parametrize("verfahren,voll,s_min", [(A.EP_EINFACH, False, 0.0), (A.EP_VOLL, True, 0.0), (A.EP_VOLL, True, 0.8), (A.EP_VOLL, True, 1.0)])
def test_3d_extreme_points_gegen_neu_erzeugte_eckpunkte_und_voxelstuetzflaeche(verfahren, voll, s_min):
    geprueft = mehrere = 0
    for cap, kisten in list(instanzen_3d(20, 1, 12, seed0=500)) + list(instanzen_3d(20, 5, 14, cap_lo=12, seed0=600, kante_hi=7)):
        rng = random.Random(cap)
        for order in (A.reihenfolge_3d(kisten, A.GRUNDFLAECHE_3D), rng.sample(range(len(kisten)), len(kisten))):
            bins, platz = A.pack_3d(kisten, order, cap, verfahren, s_min)
            assert platz == ep_naiv(kisten, order, cap, voll, s_min), (cap, kisten, order)
            geprueft += 1
            mehrere += len(bins) >= 2
    assert geprueft == 80 and mehrere >= 20                                                  # der Test prüft wirklich etwas


def test_3d_schichten_gegen_die_naive_zweitumsetzung():
    for cap, kisten in instanzen_3d(40, 1, 25, cap_lo=10, cap_hi=100, seed0=300):
        rng = random.Random(cap)
        for order in (A.reihenfolge_3d(kisten, A.HOEHE_3D), A.reihenfolge_3d(kisten, A.VOLUMEN_3D), rng.sample(range(len(kisten)), len(kisten))):
            assert A.pack_3d(kisten, order, cap, A.SCHICHTEN)[1] == schichten_naiv(kisten, order, cap), (cap, kisten, order)


def test_3d_alle_packungen_zulaessig_nie_unter_der_schranke_und_jede_stuetzflaeche_mindestens_s():
    for cap, kisten in instanzen_3d(30, 1, 20, cap_lo=10, cap_hi=100, seed0=1300):
        for verfahren, s_min in ((A.SCHICHTEN, 0.0), (A.EP_EINFACH, 0.0), (A.EP_VOLL, 0.0), (A.EP_VOLL, 0.8)):
            for schluessel in (A.VOLUMEN_3D, A.GRUNDFLAECHE_3D, A.HOEHE_3D):
                bins, platz = A.pack_3d(kisten, A.reihenfolge_3d(kisten, schluessel), cap, verfahren, s_min)
                assert A.packung_pruefen_3d(kisten, platz, cap) and len(bins) >= A.schranken_3d(kisten, cap)[2], (cap, kisten, verfahren, s_min)
                if s_min > 0:
                    assert A.stuetz_minimum_3d(kisten, platz) >= s_min - 1e-9


@pytest.mark.parametrize("bereich", range(3))
def test_gemeinsames_skalieren_aendert_die_behaelterzahl_nicht(bereich):
    if bereich == 0:
        for cap, sizes in instanzen_1d(20, 1, 15, seed0=1500):
            assert [A.anzahl_1d([3 * s for s in sizes], m, 3 * cap) for m in range(5)] == [A.anzahl_1d(sizes, m, cap) for m in range(5)]
    elif bereich == 1:
        for cap, rects in instanzen_2d(15, 1, 12, cap_lo=10, cap_hi=30, seed0=1600):
            gross = tuple((3 * w, 3 * h) for w, h in rects)
            assert [A.anzahl_2d(gross, m, 3 * cap) for m in range(3)] == [A.anzahl_2d(rects, m, cap) for m in range(3)]
    else:
        for cap, kisten in instanzen_3d(15, 1, 12, cap_lo=10, cap_hi=30, seed0=1700):
            gross = tuple(tuple(3 * x for x in k) for k in kisten)
            for verfahren, s in ((0, 0.0), (1, 0.0), (2, 0.0), (2, 0.8)):
                assert A.anzahl_3d(gross, verfahren, 1, 3 * cap, s) == A.anzahl_3d(kisten, verfahren, 1, cap, s)


def test_optimum_von_cpsat_nie_ueber_den_verfahren_und_nie_unter_der_schranke():
    pytest.importorskip("ortools")
    from dev.opt_2d import optimum_cpsat as opt2
    from dev.opt_3d import optimum_cpsat as opt3

    for cap, rects in instanzen_2d(6, 3, 7, cap_lo=10, cap_hi=20, seed0=1900):
        beste = min(A.anzahl_2d(rects, m, cap, 1) for m in range(4))
        opt = opt2(rects, cap, beste, 20.0, 2)
        assert 0 < A.schranken_2d(rects, cap)[2] <= opt <= beste, (cap, rects)
    for cap, kisten in instanzen_3d(6, 3, 7, cap_lo=10, cap_hi=20, seed0=2000):
        beste = min(A.anzahl_3d(kisten, v, k, cap) for v in range(3) for k in range(1, 4))
        opt = opt3(kisten, cap, beste, 20.0, 2)
        assert 0 < A.schranken_3d(kisten, cap)[2] <= opt <= beste, (cap, kisten)
