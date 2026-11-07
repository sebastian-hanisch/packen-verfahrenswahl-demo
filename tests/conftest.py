"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b), je Dimension."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def mini_1d():
    """Die zwölf Pakete 42, 23, 19, 44, 30, 35, 47, 50, 51, 53, 51, 14 bei Kapazität 100 (Summe 459, L1 = L2 = Optimum 5): Next, First und Best Fit in Lieferreihenfolge brauchen 7, FFD und BFD 5."""
    return (42, 23, 19, 44, 30, 35, 47, 50, 51, 53, 51, 14), 100


@pytest.fixture
def mini_2d():
    """Vier Rechtecke (Breite, Höhe) = (6, 4), (5, 3), (4, 5), (4, 2) mit den Nummern 0 bis 3, Behälter 10 mal 10, Fläche 69, Schranke 1."""
    return ((6, 4), (5, 3), (4, 5), (4, 2)), 10


@pytest.fixture
def mini_3d():
    """Vier Quader (Breite, Tiefe, Höhe) = (4, 4, 2), (2, 5, 8), (7, 5, 2), (4, 8, 2), Behälter 10 mal 10 mal 10, Volumen 246, Schranke 1: Extreme Points mit Projektionen brauchen 1 Behälter, ohne Projektionen 2,
    Schichten 2 (Reihenfolge 0, 1, 2, 3)."""
    return ((4, 4, 2), (2, 5, 8), (7, 5, 2), (4, 8, 2)), 10


@pytest.fixture
def mini_3d_stuetz():
    """Vier Quader (2, 8, 2), (4, 7, 4), (3, 8, 6), (4, 8, 3), Behälter 10 mal 10 mal 10, Volumen 384, Schranke 1: Quader 3 liegt ohne Bedingung bei (0, 0, 4) auf 43,75 % Stützfläche, mit 80 % bei (2, 0, 4)
    auf 87,5 %, mit 100 % braucht er einen neuen Behälter (Reihenfolge 0, 1, 2, 3)."""
    return ((2, 8, 2), (4, 7, 4), (3, 8, 6), (4, 8, 3)), 10
