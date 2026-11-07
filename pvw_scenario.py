"""Instanzen: die Handbeispiele und Zufallsinstanzen für App und Messraster, je Bereich der Karte."""

import math
import random
from dataclasses import dataclass

import pvw_constants as C


@dataclass(frozen=True)
class Instance:
    bereich: int          # Bereich der Karte (0 bis 3)
    teile: tuple          # 1D: Größen (ganze Zahlen); 2D: (Breite, Höhe); 3D: (Breite, Tiefe, Höhe); in Lieferreihenfolge, ganzzahlig und positiv
    cap: int              # Kantenlänge beziehungsweise Kapazität eines Behälters

    def __post_init__(self):
        if self.bereich not in C.BEREICHE:
            raise ValueError(f"Bereich {self.bereich!r} unbekannt")
        if self.cap <= 0:
            raise ValueError("Kapazität muss positiv sein")
        d = C.DIMENSION[self.bereich]
        for t in self.teile:
            maße = (t,) if d == 1 else t
            if (d > 1 and len(t) != d) or any((not isinstance(x, int)) or x <= 0 or x > self.cap for x in maße):
                raise ValueError(f"Teil {t!r} ungültig (ganze Maße, je 1 bis {self.cap})")

    @property
    def n(self) -> int:
        return len(self.teile)


def beispiel(bereich: int) -> Instance:
    return Instance(bereich, tuple(C.BEISPIELE[bereich]), C.HAND_CAP[bereich])


def mess_seed(bereich: int, verteilung: int, n_index: int, j: int) -> int:
    """Fester Seed der j-ten Instanz einer Zelle des Messrasters; stabil über Läufe und Rechner."""
    return 1_000_000 * (bereich + 1) + 10_000 * (verteilung + 1) + 1_000 * (n_index + 1) + j


def such_seed(seed: int) -> int:
    """Startzahl der Tausch-Suche zu einer Instanz (2D): ein Vielfaches des Instanzseeds plus 3, damit sie unabhängig von den Maßen der Teile ist."""
    return 10 * seed + 3


def zufallsinstanz(bereich: int, verteilung: int, n: int, seed: int) -> Instance:
    """n Teile, Größen gleichverteilt (ganzzahlig) in den Bereichen der Verteilung."""
    cap = C.CAP[bereich]
    _, _, bereiche = C.VERTEILUNGEN[bereich][verteilung]
    rng = random.Random(seed)
    if C.DIMENSION[bereich] == 1:
        lo, hi = bereiche[0]
        a, b = max(1, math.ceil(lo * cap)), int(hi * cap)
        teile = tuple(rng.randint(a, b) for _ in range(n))
    else:
        teile = tuple(tuple(rng.randint(*bereiche[k]) for k in range(len(bereiche))) for _ in range(n))
    return Instance(bereich, teile, cap)


def quelle_instanz(bereich: int, quelle: int, n: int, seed: int) -> Instance:
    """Instanz der App: Quelle 0 = Handbeispiel (n und seed ohne Wirkung), 1 bis 4 = Zufallsinstanz der Verteilung quelle - 1."""
    if quelle == 0:
        return beispiel(bereich)
    return zufallsinstanz(bereich, quelle - 1, n, seed)
