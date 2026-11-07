"""Kern der Demo (nur Standardbibliothek): die Packverfahren der Linie in drei Dimensionen, ihre Schranken und die unabhängigen Prüfer.

Alle Funktionen tragen die Dimension als Suffix: `_1d` Pakete mit einer Größe (Next Fit, First Fit, Best Fit, jeweils in Lieferreihenfolge oder absteigend), `_2d` Rechtecke (Regal, Skyline,
MaxRects mit der Regel BSSF, MaxRects mit einer Tausch-Suche nach der Reihenfolge), `_3d` Quader (Schichten, Extreme Points ohne und mit Projektionen, optional mit Mindest-Stützfläche).
Überall gilt dieselbe Bauart: eine Reihenfolge der Teile und eine Regel, wohin das nächste kommt; jedes Teil kommt in den ersten Behälter, in dem die Regel eine Stelle für es hat, sonst in einen neuen.
Alle Zufallszahlen der Suche kommen aus `random.Random(seed).random()` (auf jeder Python-Version gleich)."""

import random


# ==================================================================================================================================================
# 1D: Pakete mit einer Größe
# ==================================================================================================================================================


def reihenfolge_1d(sizes, absteigend: bool) -> list:
    """Paketnummern: wie geliefert oder absteigend nach Größe (Gleichstand: kleinere Nummer zuerst)."""
    idx = list(range(len(sizes)))
    return sorted(idx, key=lambda i: (-sizes[i], i)) if absteigend else idx


def pack_1d(sizes, order, cap: int, regel: int) -> list:
    """Packt die Pakete in der Reihenfolge `order`; Regel 0 Next Fit (nur der zuletzt geöffnete Behälter), 1 First Fit (der erste mit Platz), 2 Best Fit (der mit dem wenigsten Rest danach,
    bei Gleichstand der früher geöffnete). Gibt die Behälter als Listen von Paketnummern zurück."""
    if sorted(order) != list(range(len(sizes))):
        raise ValueError("order muss eine Permutation der Paketnummern sein")
    if any(s <= 0 or s > cap for s in sizes):
        raise ValueError("Paketgröße muss zwischen 1 und der Kapazität liegen")
    if regel not in (0, 1, 2):
        raise ValueError(f"unbekannte Regel {regel!r}")
    bins, loads = [], []
    for i in order:
        s = sizes[i]
        ziel = -1
        if regel == 0:
            if loads and loads[-1] + s <= cap:
                ziel = len(loads) - 1
        elif regel == 1:
            for b, load in enumerate(loads):
                if load + s <= cap:
                    ziel = b
                    break
        else:
            rest_best = None
            for b, load in enumerate(loads):
                rest = cap - load - s
                if rest >= 0 and (rest_best is None or rest < rest_best):
                    rest_best, ziel = rest, b
        if ziel < 0:
            bins.append([i])
            loads.append(s)
        else:
            bins[ziel].append(i)
            loads[ziel] += s
    return bins


# Die fünf Verfahren der Karte in 1D: (Reihenfolge absteigend?, Regel)
VERFAHREN_1D = ((False, 0), (False, 1), (False, 2), (True, 1), (True, 2))


def anzahl_1d(sizes, verfahren: int, cap: int) -> int:
    """Behälterzahl von Verfahren 0 NF, 1 FF, 2 BF (Lieferreihenfolge), 3 FFD, 4 BFD."""
    absteigend, regel = VERFAHREN_1D[verfahren]
    return len(pack_1d(sizes, reihenfolge_1d(sizes, absteigend), cap, regel))


def container_pruefen_1d(sizes, bins, cap: int) -> bool:
    """Unabhängiger Prüfer: jedes Paket genau einmal, keine Überfüllung, keine leeren Behälter."""
    gesehen = sorted(i for b in bins for i in b)
    return gesehen == list(range(len(sizes))) and all(b and sum(sizes[i] for i in b) <= cap for b in bins)


def l1_1d(sizes, cap: int) -> int:
    """Volumenschranke: Summe der Größen durch die Kapazität, aufgerundet."""
    return -(-sum(sizes) // cap) if sizes else 0


def l2_1d(sizes, cap: int) -> int:
    """Schranke L2 nach Martello und Toth: für jedes alpha (null und jede Größe bis zur halben Kapazität) J1 = {s > cap - alpha}, J2 = {cap - alpha >= s > cap/2}, J3 = {cap/2 >= s >= alpha};
    L(alpha) = |J1| + |J2| + max(0, ceil((Summe J3 - (|J2| cap - Summe J2)) / cap)); L2 ist das Maximum (und mindestens L1)."""
    best = l1_1d(sizes, cap)
    for alpha in {0} | {s for s in sizes if 2 * s <= cap}:
        j1 = [s for s in sizes if s > cap - alpha]
        j2 = [s for s in sizes if cap - alpha >= s and 2 * s > cap]
        j3 = [s for s in sizes if 2 * s <= cap and s >= alpha]
        frei = len(j2) * cap - sum(j2)
        extra = max(0, -(-(sum(j3) - frei) // cap)) if j3 else 0
        best = max(best, len(j1) + len(j2) + extra)
    return best


def optimum_1d(sizes, cap: int, limit: int = 12):
    """Kleinste mögliche Behälterzahl per Teilmengen-DP, oder None, wenn mehr als `limit` Pakete vorliegen. dp[Menge] = (Behälter, Füllung des letzten), lexikographisch minimal."""
    n = len(sizes)
    if n > limit:
        return None
    if n == 0:
        return 0
    full = (1 << n) - 1
    inf = (n + 1, cap + 1)
    dp = [inf] * (full + 1)
    dp[0] = (1, 0)
    for mask in range(full + 1):
        b, last = dp[mask]
        if b > n:
            continue
        for i in range(n):
            if mask >> i & 1:
                continue
            s = sizes[i]
            nxt = (b, last + s) if last + s <= cap else (b + 1, s)
            m2 = mask | (1 << i)
            if nxt < dp[m2]:
                dp[m2] = nxt
    return dp[full][0]


# ==================================================================================================================================================
# 2D: Rechtecke
# ==================================================================================================================================================

HOEHE_2D, FLAECHE_2D = 1, 2


def reihenfolge_2d(rects, schluessel: int) -> list:
    """Teilenummern absteigend nach dem Schlüssel (1 Höhe, 2 Fläche); Gleichstände bleiben in der Lieferreihenfolge; Schlüssel 0: Lieferreihenfolge."""
    if schluessel == 0:
        return list(range(len(rects)))
    wert = [h for _, h in rects] if schluessel == HOEHE_2D else [w * h for w, h in rects]
    return sorted(range(len(rects)), key=lambda i: (-wert[i], i))


def _regal_setzen(regale, bins, platz, i, w, h, cap):
    """Regal, erstes passendes. Regal = [y, Höhe, belegte Breite]; ein Rechteck passt, wenn es nicht höher ist als das Regal und die Breite reicht; sonst ein neues Regal direkt über dem letzten im
    ersten Behälter mit genug Resthöhe."""
    for b in range(len(regale)):
        for sh in regale[b]:
            if h <= sh[1] and sh[2] + w <= cap:
                platz.append((i, b, sh[2], sh[0]))
                bins[b].append(i)
                sh[2] += w
                return True
    for b in range(len(regale)):
        oben = regale[b][-1][0] + regale[b][-1][1]
        if oben + h <= cap:
            regale[b].append([oben, h, w])
            bins[b].append(i)
            platz.append((i, b, 0, oben))
            return True
    return False


def _skyline_setzen(profile, bins, platz, i, w, h, cap):
    """Skyline: im ersten Behälter, in dem es passt, an die niedrigste Stelle (bei Gleichstand die linkeste); Höhlen unter Überhängen gehen verloren."""
    for b, prof in enumerate(profile):
        beste = None
        for x in range(0, cap - w + 1):
            y = max(prof[x:x + w])
            if y + h <= cap and (beste is None or y < beste[0]):
                beste = (y, x)
        if beste is not None:
            y, x = beste
            for k in range(x, x + w):
                prof[k] = y + h
            platz.append((i, b, x, y))
            bins[b].append(i)
            return True
    return False


def _maximal(frei):
    """Entfernt freie Rechtecke, die in einem anderen enthalten sind (bei Gleichheit bleibt das erste)."""
    behalten = []
    for i, a in enumerate(frei):
        if any(j != i and b[0] <= a[0] and b[1] <= a[1] and a[0] + a[2] <= b[0] + b[2] and a[1] + a[3] <= b[1] + b[3] and (b != a or j < i) for j, b in enumerate(frei)):
            continue
        behalten.append(a)
    return behalten


def _maxrects_setzen(behaelter, bins, platz, i, w, h, cap):
    """MaxRects mit der Regel BSSF: im ersten Behälter, der ein freies Rechteck für das Teil hat, an die linke untere Ecke des freien Rechtecks mit der kleinsten kurzen Restkante (dann kleinsten
    langen, dann tiefsten und linkesten Lage). Danach wird jedes überlappte freie Rechteck in bis zu vier Teile zerlegt und die Liste auf die maximalen Rechtecke gekürzt."""
    wahl = None
    for b, frei in enumerate(behaelter):
        for (fx, fy, fw, fh) in frei:
            if w <= fw and h <= fh:
                score = (min(fw - w, fh - h), max(fw - w, fh - h), fy, fx)
                if wahl is None or score < wahl[0]:
                    wahl = (score, b, fx, fy)
        if wahl is not None:
            break
    if wahl is None:
        behaelter.append([(0, 0, cap, cap)])
        bins.append([])
        wahl = (None, len(behaelter) - 1, 0, 0)
    _, b, px, py = wahl
    platz.append((i, b, px, py))
    bins[b].append(i)
    neu = []
    for (fx, fy, fw, fh) in behaelter[b]:
        if px >= fx + fw or px + w <= fx or py >= fy + fh or py + h <= fy:
            neu.append((fx, fy, fw, fh))
            continue
        if px > fx:
            neu.append((fx, fy, px - fx, fh))
        if px + w < fx + fw:
            neu.append((px + w, fy, fx + fw - px - w, fh))
        if py > fy:
            neu.append((fx, fy, fw, py - fy))
        if py + h < fy + fh:
            neu.append((fx, py + h, fw, fy + fh - py - h))
    behaelter[b] = _maximal(neu)


def pack_2d(rects, order, cap: int, verfahren: int):
    """Packt die Rechtecke in der Reihenfolge `order` (auch ein Anfang der Reihenfolge ist erlaubt). Verfahren 0 Regal (erstes passendes), 1 Skyline, 2 MaxRects BSSF. Gibt (bins, platz) zurück:
    bins[b] = Teilenummern, platz = (Teil, Behälter, x, y) mit der linken unteren Ecke."""
    if verfahren not in (0, 1, 2):
        raise ValueError(f"Verfahren {verfahren!r} unbekannt")
    order = list(order)
    if len(set(order)) != len(order) or any(not 0 <= i < len(rects) for i in order):
        raise ValueError("die Reihenfolge darf jedes Rechteck höchstens einmal enthalten")
    for t in rects:
        if len(t) != 2 or any(x <= 0 or x > cap for x in t):
            raise ValueError(f"Rechteck {t!r} ungültig (zwei Maße, je 1 bis {cap})")
    zustand, bins, platz = [], [], []
    for i in order:
        w, h = rects[i]
        if verfahren == 0:
            if not _regal_setzen(zustand, bins, platz, i, w, h, cap):
                zustand.append([[0, h, w]])
                bins.append([i])
                platz.append((i, len(zustand) - 1, 0, 0))
        elif verfahren == 1:
            if not _skyline_setzen(zustand, bins, platz, i, w, h, cap):
                prof = [0] * cap
                for k in range(w):
                    prof[k] = h
                zustand.append(prof)
                bins.append([i])
                platz.append((i, len(zustand) - 1, 0, 0))
        else:
            _maxrects_setzen(zustand, bins, platz, i, w, h, cap)
    return bins, platz


def packung_pruefen_2d(rects, platz, cap: int, vollstaendig: bool = True) -> bool:
    """Unabhängiger Prüfer: jedes Rechteck höchstens einmal (bei `vollstaendig` genau einmal), ganz im Behälter, keine zwei Rechtecke eines Behälters überlappen."""
    nummern = sorted(p[0] for p in platz)
    if vollstaendig and nummern != list(range(len(rects))):
        return False
    if len(set(nummern)) != len(nummern) or any(not 0 <= i < len(rects) for i in nummern):
        return False
    je = {}
    for i, b, x, y in platz:
        w, h = rects[i]
        if x < 0 or y < 0 or x + w > cap or y + h > cap:
            return False
        je.setdefault(b, []).append((x, y, x + w, y + h))
    for lst in je.values():
        for a in range(len(lst)):
            for c in range(a + 1, len(lst)):
                p, q = lst[a], lst[c]
                if p[0] < q[2] and q[0] < p[2] and p[1] < q[3] and q[1] < p[3]:
                    return False
    return True


def schranken_2d(rects, cap: int):
    """(Flächenschranke, Zahl der großen Rechtecke, Schranke): die Fläche aller Rechtecke durch die Behälterfläche aufgerundet; die Zahl der Rechtecke, die in beiden Maßen über die Hälfte reichen
    (zwei solche überlappen in jedem Behälter über dem Mittelpunkt); das Größere von beiden."""
    flaeche = -(-sum(w * h for w, h in rects) // (cap * cap))
    gross = sum(1 for w, h in rects if 2 * w > cap and 2 * h > cap)
    return flaeche, gross, max(flaeche, gross)


class Zufall:
    """Zufallsquelle, die nur `random.Random(seed).random()` benutzt (53-Bit-Gleitkommazahlen im Intervall [0, 1))."""

    def __init__(self, seed: int):
        self._r = random.Random(seed)

    def unter(self, n: int) -> int:
        """Ganze Zahl von 0 bis n - 1."""
        return int(self._r.random() * n)

    def paar(self, n: int) -> tuple:
        """Zwei verschiedene Positionen (i, j) von 0 bis n - 1; n >= 2."""
        i = self.unter(n)
        j = self.unter(n - 1)
        if j >= i:
            j += 1
        return i, j


def bewerten_2d(rects, order, cap: int) -> tuple:
    """(Zahl der Behälter, Fläche im am wenigsten gefüllten Behälter) von MaxRects BSSF in der Reihenfolge `order`; beides ist besser, wenn es kleiner ist."""
    bins = pack_2d(rects, order, cap, 2)[0]
    return len(bins), min(sum(rects[i][0] * rects[i][1] for i in b) for b in bins) if bins else 0


def suche_2d(rects, cap: int, budget: int, seed: int):
    """Tausch-Suche mit Zweitziel nach der Reihenfolge: Start ist die Reihenfolge nach Fläche (die erste Auswertung); jede weitere Auswertung vertauscht zwei zufällige Positionen der bisher besten
    Reihenfolge und behält die neue, wenn (Behälter, Fläche im leersten Behälter) lexikographisch nicht größer wird. Gibt (beste Reihenfolge, Zahl der Behälter) zurück."""
    if budget < 1:
        raise ValueError("das Budget muss mindestens 1 sein (die erste Auswertung ist der Start)")
    n = len(rects)
    beste = reihenfolge_2d(rects, FLAECHE_2D)
    zb = bewerten_2d(rects, beste, cap)
    zufall = Zufall(seed)
    for _ in range(1, budget):
        if n < 2:
            break
        i, j = zufall.paar(n)
        order = list(beste)
        order[i], order[j] = order[j], order[i]
        z = bewerten_2d(rects, order, cap)
        if z <= zb:
            beste, zb = order, z
    return beste, zb[0]


SUCHBUDGET_2D = 200


def anzahl_2d(rects, verfahren: int, cap: int, seed: int = 0) -> int:
    """Behälterzahl von Verfahren 0 Regal mit Höhe, 1 Skyline mit Fläche, 2 MaxRects BSSF mit Fläche, 3 MaxRects BSSF mit Tausch-Suche (200 Auswertungen, Startzahl `seed`)."""
    if verfahren == 0:
        return len(pack_2d(rects, reihenfolge_2d(rects, HOEHE_2D), cap, 0)[0])
    if verfahren == 1:
        return len(pack_2d(rects, reihenfolge_2d(rects, FLAECHE_2D), cap, 1)[0])
    if verfahren == 2:
        return len(pack_2d(rects, reihenfolge_2d(rects, FLAECHE_2D), cap, 2)[0])
    if verfahren == 3:
        return suche_2d(rects, cap, SUCHBUDGET_2D, seed)[1]
    raise ValueError(f"Verfahren {verfahren!r} unbekannt")


# ==================================================================================================================================================
# 3D: Quader
# ==================================================================================================================================================

VOLUMEN_3D, GRUNDFLAECHE_3D, HOEHE_3D = 1, 2, 3
SCHICHTEN, EP_EINFACH, EP_VOLL = 0, 1, 2


def reihenfolge_3d(kisten, schluessel: int) -> list:
    """Quadernummern absteigend nach dem Schlüssel (1 Volumen, 2 Grundfläche, 3 Höhe); Gleichstände bleiben in der Lieferreihenfolge; Schlüssel 0: Lieferreihenfolge."""
    if schluessel == 0:
        return list(range(len(kisten)))
    f = {VOLUMEN_3D: lambda k: k[0] * k[1] * k[2], GRUNDFLAECHE_3D: lambda k: k[0] * k[1], HOEHE_3D: lambda k: k[2]}[schluessel]
    return sorted(range(len(kisten)), key=lambda i: (-f(kisten[i]), i))


def _ueberlappt(a, b) -> bool:
    """Zwei Quader (x, y, z, w, d, h) überlappen in einem Rauminhalt über null (Berührung zählt nicht)."""
    return a[0] < b[0] + b[3] and b[0] < a[0] + a[3] and a[1] < b[1] + b[4] and b[1] < a[1] + a[4] and a[2] < b[2] + b[5] and b[2] < a[2] + a[5]


def packung_pruefen_3d(kisten, platz, cap: int, vollstaendig: bool = True) -> bool:
    """Unabhängiger Prüfer: jeder Quader höchstens einmal (bei `vollstaendig` genau einmal), ganz im Behälter, keine zwei Quader eines Behälters überlappen."""
    nummern = sorted(p[0] for p in platz)
    if vollstaendig and nummern != list(range(len(kisten))):
        return False
    if len(set(nummern)) != len(nummern) or any(not 0 <= i < len(kisten) for i in nummern):
        return False
    je = {}
    for i, b, x, y, z in platz:
        w, d, h = kisten[i]
        if x < 0 or y < 0 or z < 0 or x + w > cap or y + d > cap or z + h > cap:
            return False
        je.setdefault(b, []).append((x, y, z, w, d, h))
    for lst in je.values():
        for a in range(len(lst)):
            for c in range(a + 1, len(lst)):
                if _ueberlappt(lst[a], lst[c]):
                    return False
    return True


def schranken_3d(kisten, cap: int):
    """(Volumenschranke, Zahl der großen Quader, Schranke): das Volumen aller Quader durch das Behältervolumen aufgerundet; die Zahl der Quader, die in allen drei Maßen über die Hälfte reichen;
    das Größere von beiden."""
    volumen = -(-sum(w * d * h for w, d, h in kisten) // cap ** 3)
    gross = sum(1 for w, d, h in kisten if 2 * w > cap and 2 * d > cap and 2 * h > cap)
    return volumen, gross, max(volumen, gross)


def _stuetz_gegen(quader, gesetzt) -> float:
    """Anteil der Grundfläche von `quader` (x, y, z, w, d, h), der auf dem Boden oder auf Oberseiten der Quader `gesetzt` aufliegt."""
    x, y, z, w, d, _h = quader
    if z == 0:
        return 1.0
    flaeche = 0
    for q in gesetzt:
        if q[2] + q[5] == z:
            flaeche += max(0, min(x + w, q[0] + q[3]) - max(x, q[0])) * max(0, min(y + d, q[1] + q[4]) - max(y, q[1]))
    return flaeche / (w * d)


def stuetzflaeche_3d(kisten, platz, i: int) -> float:
    """Anteil der Grundfläche von Quader i, der auf dem Boden oder auf den Oberseiten anderer Quader desselben Behälters aufliegt (1,0 am Boden)."""
    _, b, x, y, z = next(p for p in platz if p[0] == i)
    andere = [(x2, y2, z2, *kisten[j]) for j, bb, x2, y2, z2 in platz if bb == b and j != i]
    return _stuetz_gegen((x, y, z, *kisten[i]), andere)


def stuetz_minimum_3d(kisten, platz) -> float:
    """Kleinste Stützfläche aller Quader der Packung (1,0 bei leerer Packung)."""
    return min((stuetzflaeche_3d(kisten, platz, p[0]) for p in platz), default=1.0)


def _schichten(kisten, order, cap):
    behaelter = []          # je Behälter: Liste von Schichten {"z", "h", "regale": [{"y", "d", "x"}]}
    platz = []
    for i in order:
        w, d, h = kisten[i]
        gesetzt = False
        for b, lagen in enumerate(behaelter):
            for s in lagen:
                if h > s["h"]:
                    continue
                for r in s["regale"]:
                    if d <= r["d"] and r["x"] + w <= cap:
                        platz.append((i, b, r["x"], r["y"], s["z"]))
                        r["x"] += w
                        gesetzt = True
                        break
                if gesetzt:
                    break
                y0 = sum(r["d"] for r in s["regale"])
                if y0 + d <= cap:
                    s["regale"].append({"y": y0, "d": d, "x": w})
                    platz.append((i, b, 0, y0, s["z"]))
                    gesetzt = True
                    break
            if gesetzt:
                break
            z0 = sum(s["h"] for s in lagen)
            if z0 + h <= cap:
                lagen.append({"z": z0, "h": h, "regale": [{"y": 0, "d": d, "x": w}]})
                platz.append((i, b, 0, 0, z0))
                gesetzt = True
                break
        if not gesetzt:
            behaelter.append([{"z": 0, "h": h, "regale": [{"y": 0, "d": d, "x": w}]}])
            platz.append((i, len(behaelter) - 1, 0, 0, 0))
    bins = [[] for _ in behaelter]
    for i, b, _x, _y, _z in platz:
        bins[b].append(i)
    return bins, platz


def _projiziere(p, achse: int, gesetzt):
    """Punkt p in negativer Richtung der Achse (0 x, 1 y, 2 z) bis zur nächsten Fläche eines gesetzten Quaders oder bis zur Wand schieben."""
    a, b = [k for k in (0, 1, 2) if k != achse]
    wert = 0
    for q in gesetzt:
        qa = q[achse] + q[3 + achse]
        if qa <= p[achse] and q[a] <= p[a] < q[a] + q[3 + a] and q[b] <= p[b] < q[b] + q[3 + b]:
            wert = max(wert, qa)
    r = list(p)
    r[achse] = wert
    return tuple(r)


def _extreme_points(kisten, order, cap, voll: bool, s_min: float):
    """Extreme Points: je Behälter eine Menge von Eckpunkten; ein Quader kommt in den ersten Behälter, in dem ein Punkt ihn aufnimmt (kein Überlapp, im Behälter, Stützfläche mindestens s_min), an
    den Punkt mit kleinstem (z, y, x). Neue Punkte: die Ecken rechts, hinten und oben, bei `voll` auch deren Projektionen auf die nächste Fläche oder die Wand."""
    behaelter = []          # je Behälter: {"punkte": set, "gesetzt": [(x, y, z, w, d, h)]}
    platz = []
    bins = []
    for i in order:
        w, d, h = kisten[i]
        wahl = None
        for b, c in enumerate(behaelter):
            for (x, y, z) in sorted(c["punkte"], key=lambda p: (p[2], p[1], p[0])):
                if x + w > cap or y + d > cap or z + h > cap:
                    continue
                k = (x, y, z, w, d, h)
                if any(_ueberlappt(k, q) for q in c["gesetzt"]):
                    continue
                if s_min > 0 and _stuetz_gegen(k, c["gesetzt"]) < s_min - 1e-9:
                    continue
                wahl = (b, x, y, z)
                break
            if wahl:
                break
        if not wahl:
            behaelter.append({"punkte": {(0, 0, 0)}, "gesetzt": []})
            bins.append([])
            wahl = (len(behaelter) - 1, 0, 0, 0)
        b, x, y, z = wahl
        c = behaelter[b]
        platz.append((i, b, x, y, z))
        bins[b].append(i)
        c["punkte"].discard((x, y, z))
        for p, achsen in (((x + w, y, z), (1, 2)), ((x, y + d, z), (0, 2)), ((x, y, z + h), (0, 1))):
            if max(p) < cap:
                c["punkte"].add(p)
            if voll:
                for a in achsen:
                    q = _projiziere(p, a, c["gesetzt"])
                    if max(q) < cap:
                        c["punkte"].add(q)
        c["gesetzt"].append((x, y, z, w, d, h))
        c["punkte"] = {p for p in c["punkte"] if not any(q[0] <= p[0] < q[0] + q[3] and q[1] <= p[1] < q[1] + q[4] and q[2] <= p[2] < q[2] + q[5] for q in c["gesetzt"])}
    return bins, platz


def pack_3d(kisten, order, cap: int, verfahren: int, s_min: float = 0.0):
    """Packt die Quader in der Reihenfolge `order`. Verfahren 0 Schichten (nur ohne Stützbedingung), 1 Extreme Points ohne Projektionen, 2 Extreme Points mit Projektionen; `s_min` ist die
    Mindest-Stützfläche der Extreme Points. Gibt (bins, platz) mit platz = (Quader, Behälter, x, y, z) zurück."""
    order = list(order)
    if len(set(order)) != len(order) or any(not 0 <= i < len(kisten) for i in order):
        raise ValueError("die Reihenfolge darf jeden Quader höchstens einmal enthalten")
    if verfahren not in (SCHICHTEN, EP_EINFACH, EP_VOLL):
        raise ValueError(f"Verfahren {verfahren!r} unbekannt")
    if not 0 <= s_min <= 1:
        raise ValueError("die Mindest-Stützfläche liegt zwischen 0 und 1")
    if verfahren == SCHICHTEN and s_min > 0:
        raise ValueError("Schichten kennen keine Stützbedingung")
    for k in kisten:
        if len(k) != 3 or any(not isinstance(x, int) or x <= 0 or x > cap for x in k):
            raise ValueError(f"Quader {k!r} ungültig (drei ganze Maße, je 1 bis {cap})")
    if verfahren == SCHICHTEN:
        return _schichten(kisten, order, cap)
    return _extreme_points(kisten, order, cap, verfahren == EP_VOLL, s_min)


def anzahl_3d(kisten, verfahren: int, schluessel: int, cap: int, s_min: float = 0.0) -> int:
    """Behälterzahl von Verfahren (0 Schichten, 1 EP einfach, 2 EP voll) mit dem Schlüssel (0 Lieferung, 1 Volumen, 2 Grundfläche, 3 Höhe) und der Mindest-Stützfläche."""
    return len(pack_3d(kisten, reihenfolge_3d(kisten, schluessel), cap, verfahren, s_min)[0])
