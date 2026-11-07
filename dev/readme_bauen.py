"""Setzt die README zusammen: Tabellen und Text der Annahmen kommen aus denselben Funktionen wie in der App (nur zum Schreiben der README, nicht Teil der Laufzeit).

    python dev/readme_bauen.py [ANZAHL_TESTS]
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pvw_constants as C  # noqa: E402
import pvw_evaluation as ev  # noqa: E402
from pvw_scenario import beispiel  # noqa: E402


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def karte(bereich: int) -> str:
    """Die Karte eines Bereichs als Tabelle: je Zelle die mittleren Behälter über der Schranke, der Gewinner mit ★."""
    zeilen = ["| Verteilung | n | " + " | ".join(C.VERFAHREN[bereich]) + " |", "|---|---|" + "---|" * len(C.VERFAHREN[bereich])]
    for v, ni in ev.zellen_von(bereich):
        z = ev.zeile(bereich, v, ni)
        zeilen.append(f"| {C.VERTEILUNG_KURZ[bereich][v]} | {z['n']} | " + " | ".join(de(x) + (" ★" if m in z["gewinner"] else "") for m, x in enumerate(z["mittel"])) + " |")
    return "\n".join(zeilen)


def regret_tabelle() -> str:
    """Je Bereich und Verfahren der mittlere Regret, der Anteil bester Instanzen und die Auswertungen."""
    zeilen = ["| Bereich | Verfahren | Regret | beste Instanzen | Auswertungen |", "|---|---|---|---|---|"]
    for b in ev.BEREICHE:
        u = ev.uebersicht(b)
        for m, name in enumerate(C.VERFAHREN[b]):
            zeilen.append(f"| {C.BEREICH_KURZ[b]} | {name} | {de(u['regret'][m])} | {u['beste'][m]:.0f} % | {C.AUSWERTUNGEN[b][m]} |")
    return "\n".join(zeilen)


def stuetz_tabelle() -> str:
    zeilen = ["| Verteilung | n | ohne Stützbedingung: Gewinner | mit 80 % Stützfläche: Gewinner | Mehrbedarf des Besten |", "|---|---|---|---|---|"]
    for r in ev.stuetz_zeilen():
        ohne = " / ".join(C.VERFAHREN[C.DREI][m] for m in r["ohne"])
        mit = " / ".join(C.VERFAHREN[C.DREI_STUETZ][m] for m in r["mit"])
        zeilen.append(f"| {C.VERTEILUNG_KURZ[C.DREI][r['verteilung']]} | {r['n']} | {ohne} | {mit} | {r['mehr']:+.2f} |".replace(".", ","))
    return "\n".join(zeilen)


def beispiel_tabelle() -> str:
    """Behälterzahl der Verfahren in den vier Handbeispielen (Spalten: Bereiche)."""
    zeilen = ["| Bereich | Verfahren | Behälter | Schranke | Optimum |", "|---|---|---|---|---|"]
    for b in ev.BEREICHE:
        inst = beispiel(b)
        z = ev.zaehle(inst, C.DEFAULT_SEED)
        for m, name in enumerate(C.VERFAHREN[b]):
            zeilen.append(f"| {C.BEREICH_KURZ[b]} | {name} | {z[m]} | {ev.schranke(inst)} | {C.BEISPIEL_OPTIMUM[b]} |")
    return "\n".join(zeilen)


if __name__ == "__main__":
    vorlage = (ROOT / "dev" / "readme_vorlage.md").read_text(encoding="utf-8")
    anzahl = sys.argv[1] if len(sys.argv) > 1 else "TESTZAHL"
    text = (vorlage.replace("{{KARTE_1D}}", karte(0)).replace("{{KARTE_2D}}", karte(1)).replace("{{KARTE_3D}}", karte(2)).replace("{{KARTE_3DS}}", karte(3)).replace("{{REGRET}}", regret_tabelle())
            .replace("{{STUETZ}}", stuetz_tabelle()).replace("{{BEISPIELE}}", beispiel_tabelle()).replace("{{ANNAHMEN}}", C.ASSUMPTIONS_MARKDOWN).replace("{{TESTS}}", anzahl))
    (ROOT / "README.md").write_text(text, encoding="utf-8")
    print("README.md geschrieben")
