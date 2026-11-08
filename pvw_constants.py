"""Konstanten: Bereiche der Karte, Verteilungen, Verfahren, Handbeispiele, Messraster, Farben und Presets."""

# --- Die vier Bereiche der Karte ----------------------------------------------------------------------------------------------------------------
# 0 Pakete mit einer Größe (1D), 1 Rechtecke (2D), 2 Quader ohne Stützbedingung (3D), 3 Quader mit 80 % Mindest-Stützfläche (3D)
EINS, ZWEI, DREI, DREI_STUETZ = 0, 1, 2, 3
BEREICHE = {0: "1D: Pakete mit einer Größe", 1: "2D: Rechtecke", 2: "3D: Quader ohne Stützbedingung", 3: "3D: Quader mit 80 % Stützfläche"}
BEREICH_KURZ = {0: "1D", 1: "2D", 2: "3D", 3: "3D mit Stützfläche"}
DIMENSION = {0: 1, 1: 2, 2: 3, 3: 3}
CAP = {0: 1000, 1: 100, 2: 100, 3: 100}          # Behältergröße im Raster und in den Zufallsinstanzen
HAND_CAP = {0: 100, 1: 100, 2: 100, 3: 100}      # Behältergröße der Handbeispiele
S_MIN = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.8}         # Mindest-Stützfläche des Bereichs (nur 3D)

# --- Verteilungen: (Schlüssel, Name, Bereiche der Größen) ----------------------------------------------------------------------------------------
VERTEILUNGEN = {
    0: (("klein", "kleine Teile (1 bis 25 % der Kapazität)", ((0.01, 0.25),)),
        ("mittel", "mittlere Teile (10 bis 50 %)", ((0.10, 0.50),)),
        ("gross", "große Teile (20 bis 80 %)", ((0.20, 0.80),)),
        ("breit", "breit gestreute Teile (1 bis 90 %)", ((0.01, 0.90),))),
    1: (("mittel", "mittlere Rechtecke (20 bis 60)", ((20, 60), (20, 60))),
        ("breit", "breit gestreute Rechtecke (5 bis 70)", ((5, 70), (5, 70))),
        ("klein", "kleine Rechtecke (10 bis 40)", ((10, 40), (10, 40))),
        ("hochschmal", "hohe schmale Rechtecke (Breite 5 bis 30, Höhe 30 bis 80)", ((5, 30), (30, 80)))),
    2: (("mittel", "mittlere Quader (alle Kanten 20 bis 60)", ((20, 60),) * 3),
        ("breit", "breit gestreute Quader (alle Kanten 5 bis 70)", ((5, 70),) * 3),
        ("klein", "kleine Quader (alle Kanten 10 bis 40)", ((10, 40),) * 3),
        ("flach", "flache Quader (Breite und Tiefe 30 bis 80, Höhe 5 bis 30)", ((30, 80), (30, 80), (5, 30)))),
}
VERTEILUNGEN[3] = VERTEILUNGEN[2]
VERTEILUNG_KURZ = {0: ("klein", "mittel", "groß", "breit"), 1: ("mittel", "breit", "klein", "hoch schmal"), 2: ("mittel", "breit", "klein", "flach"), 3: ("mittel", "breit", "klein", "flach")}
VERTEILUNG_LANG = {0: ("kleine Teile", "mittlere Teile", "große Teile", "breit gestreute Teile"), 1: ("mittlere Rechtecke", "breit gestreute Rechtecke", "kleine Rechtecke", "hohe schmale Rechtecke"),
                   2: ("mittlere Quader", "breit gestreute Quader", "kleine Quader", "flache Quader"), 3: ("mittlere Quader", "breit gestreute Quader", "kleine Quader", "flache Quader")}
VERTEILUNG_DAT = {0: ("kleinen Teilen", "mittleren Teilen", "großen Teilen", "breit gestreuten Teilen"), 1: ("mittleren Rechtecken", "breit gestreuten Rechtecken", "kleinen Rechtecken", "hohen schmalen Rechtecken"),
                  2: ("mittleren Quadern", "breit gestreuten Quadern", "kleinen Quadern", "flachen Quadern"), 3: ("mittleren Quadern", "breit gestreuten Quadern", "kleinen Quadern", "flachen Quadern")}
TEIL = {0: "Pakete", 1: "Rechtecke", 2: "Quader", 3: "Quader"}

# --- Verfahren je Bereich ------------------------------------------------------------------------------------------------------------------------
VERFAHREN = {
    0: ("NF", "FF", "BF", "FFD", "BFD"),
    1: ("Regal", "Skyline", "MaxRects", "MaxRects + Suche"),
    2: ("Schichten", "EP einfach", "EP voll"),
    3: ("EP voll Volumen", "EP voll Grundfläche", "EP voll Höhe"),
}
VERFAHREN_LANG = {
    0: ("Next Fit, Lieferreihenfolge", "First Fit, Lieferreihenfolge", "Best Fit, Lieferreihenfolge", "First Fit, größte zuerst (FFD)", "Best Fit, größte zuerst (BFD)"),
    1: ("Regal (First Fit), nach Höhe sortiert", "Skyline, nach Fläche sortiert", "MaxRects BSSF, nach Fläche sortiert", "MaxRects BSSF mit Tausch-Suche (200 Auswertungen)"),
    2: ("Schichten, nach Höhe sortiert", "Extreme Points ohne Projektionen, nach Volumen sortiert", "Extreme Points mit Projektionen, nach Volumen sortiert"),
    3: ("Extreme Points mit Projektionen, nach Volumen sortiert", "Extreme Points mit Projektionen, nach Grundfläche sortiert", "Extreme Points mit Projektionen, nach Höhe sortiert"),
}
# Auswertungen je Verfahren: eine Reihenfolge wird einmal dekodiert; die Tausch-Suche dekodiert 200 Reihenfolgen
AUSWERTUNGEN = {0: (1, 1, 1, 1, 1), 1: (1, 1, 1, 200), 2: (1, 1, 1), 3: (1, 1, 1)}
# 3D: (Verfahren, Schlüssel) je Verfahren des Bereichs; Verfahren 0 Schichten, 1 EP einfach, 2 EP voll; Schlüssel 1 Volumen, 2 Grundfläche, 3 Höhe
DREI_VERFAHREN = {2: ((0, 3), (1, 1), (2, 1)), 3: ((2, 1), (2, 2), (2, 3))}
SUCHBUDGET = 200

# --- Handbeispiele (zwölf Teile; Behälter 100) -----------------------------------------------------------------------------------------------------
# 1D: zwölf Pakete aus Stück 1 der Linie (Summe 459, L1 = L2 = Optimum 5); NF, FF, BF in Lieferreihenfolge 7, FFD und BFD 5.
# 2D und 3D: je zwölf Teile aus den Messrastern der Stücke 8 und 9 (Optimum 3 beziehungsweise 1, in den Tests mit CP-SAT nachgerechnet; 3D mit Stützfläche: Optimum ohne Stützbedingung).
BEISPIELE = {
    0: (42, 23, 19, 44, 30, 35, 47, 50, 51, 53, 51, 14),
    1: ((43, 57), (41, 57), (50, 43), (27, 59), (56, 24), (29, 39), (48, 40), (32, 25), (20, 51), (47, 50), (56, 60), (46, 51)),
    2: ((26, 29, 38), (41, 58, 28), (50, 32, 45), (26, 51, 32), (43, 50, 20), (42, 35, 39), (26, 47, 21), (54, 35, 21), (50, 33, 20), (22, 54, 41), (34, 39, 25), (51, 39, 37)),
}
BEISPIELE[3] = BEISPIELE[2]
BEISPIEL_OPTIMUM = {0: 5, 1: 3, 2: 1, 3: 1}

# Quellen der Instanz: 0 das Handbeispiel des Bereichs, 1 bis 4 Zufallsinstanzen mit der jeweiligen Verteilung des Bereichs
QUELLEN = {0: "Handbeispiel (zwölf Teile)", 1: "zufällig, 1. Verteilung", 2: "zufällig, 2. Verteilung", 3: "zufällig, 3. Verteilung", 4: "zufällig, 4. Verteilung"}
APP_N = {0: (12, 20, 50, 100), 1: (12, 20, 40, 80), 2: (12, 20, 40, 80), 3: (12, 20, 40, 80)}   # Zahl der Teile der Zufallsinstanzen in der App

SEED_MAX, DEFAULT_SEED = 999999, 7

# --- Messraster ---------------------------------------------------------------------------------------------------------------------------
MESS_N = {0: (20, 50, 100, 200), 1: (20, 40, 80), 2: (20, 40, 80), 3: (20, 40, 80)}
INSTANZEN = {0: 200, 1: 100, 2: 100, 3: 100}      # Instanzen je Zelle; der Wert steht neben jeder Zahl
STICHPROBE_J = (0, 1, 2)                          # Instanzen jeder Zelle, die einzeln gespeichert und in den Tests frisch nachgerechnet werden

COLOR_LINE = "#c0392b"
VERFAHREN_FARBEN = ("#9d755d", "#4c78a8", "#2F6B65", "#b279a2", "#f58518")

PRESETS = {
    "1D: das Handbeispiel": {"bereich": 0, "quelle": 0, "n_index": 0, "seed": DEFAULT_SEED},
    "2D: das Handbeispiel": {"bereich": 1, "quelle": 0, "n_index": 0, "seed": DEFAULT_SEED},
    "2D: mittlere Rechtecke, 40 Stück": {"bereich": 1, "quelle": 1, "n_index": 2, "seed": 20},
    "3D: flache Quader, 20 Stück": {"bereich": 2, "quelle": 4, "n_index": 1, "seed": DEFAULT_SEED},
    "3D mit Stützfläche: flache Quader, 40 Stück": {"bereich": 3, "quelle": 4, "n_index": 2, "seed": 1},
}
PRESET_HELP = {
    "1D: das Handbeispiel": "Zwölf Pakete: In Lieferreihenfolge brauchen Next, First und Best Fit sieben Behälter, größte zuerst (FFD und BFD) fünf, so viele wie das Optimum. Die Karte empfiehlt in 1D FFD oder BFD.",
    "2D: das Handbeispiel": "Zwölf Rechtecke: Das Regal braucht vier Behälter, Skyline, MaxRects und die Suche drei, das Optimum. Die Karte empfiehlt MaxRects mit Tausch-Suche; sie braucht dafür 200 Auswertungen statt einer.",
    "2D: mittlere Rechtecke, 40 Stück": "Vierzig mittlere Rechtecke, die Schranke ist sieben: Regal, Skyline und MaxRects brauchen acht Behälter, MaxRects mit Tausch-Suche sieben (die Schranke).",
    "3D: flache Quader, 20 Stück": "Zwanzig flache Quader: Schichten brauchen zwei Behälter, Extreme Points ohne Projektionen drei, mit Projektionen zwei. Bei diesen zwanzig flachen Quadern sind Schichten besser als Extreme Points ohne Projektionen (auf der Karte nur bei n = 20 so).",
    "3D mit Stützfläche: flache Quader, 40 Stück": "Vierzig flache Quader mit 80 % Mindest-Stützfläche: Mit der Grundfläche als Schlüssel fünf Behälter, mit dem Volumen acht, mit der Höhe neun. Mit der Bedingung gewinnt die Grundfläche.",
}

# Text des Expanders „Annahmen, Grenzen und bekannte Probleme“; derselbe Wortlaut steht in der README (tests/test_claims.py vergleicht beide).
ASSUMPTIONS_MARKDOWN = """**Annahmen.** Teile mit ganzzahligen Größen (1D eine Größe, 2D Breite und Höhe, 3D Breite, Tiefe und Höhe), ohne Drehung; alle Teile sind vor dem Packen bekannt; jedes Teil kommt in den ersten Behälter, in dem die Regel des Verfahrens eine Stelle für es hat. In 1D hat der Behälter die Kapazität 1000 (die Handbeispiele 100), in 2D und 3D die Kantenlänge 100. Jedes Verfahren läuft mit einem festen Sortierschlüssel (1D Lieferreihenfolge oder größte zuerst; 2D Regal nach Höhe, Skyline und MaxRects nach Fläche; 3D Schichten nach Höhe, Extreme Points nach Volumen, im Bereich mit Stützfläche nach Volumen, Grundfläche oder Höhe). In 3D gilt im vierten Bereich eine Mindest-Stützfläche von 80 %.

**Grenzen.** Die Karte deckt vier Bereiche, je vier Verteilungen der Teilegrößen und drei oder vier Teilezahlen ab (1D mit 200, sonst mit 100 Instanzen je Zelle). Es sind nur diese Verfahren; andere Regeln, andere Suchen, Drehung und Praxisdaten kommen nicht vor. Der Maßstab ist die Schranke (1D L2, 2D Fläche und große Rechtecke, 3D Volumen und große Quader), in 2D und 3D ist sie locker: Gelesen werden nur die Unterschiede zwischen den Verfahren, nicht der Abstand. Ein Optimum gibt es nur beim Handbeispiel. Die Tausch-Suche in 2D ist eine Suche mit 200 Auswertungen (eine Dekodierung einer Reihenfolge) und einer festen Startzahl je Instanz; die Karte sagt nichts über ihre Rechenzeit. Die Extreme Points sind nach eigener Lesart umgesetzt. **Gelernte Platzierungsregeln** (Verfahren des Maschinenlernens, die die Regel „wohin kommt das nächste Teil“ aus Beispielen lernen) kommen nicht vor: Sie sind nur eine weitere Platzierungsregel im Rückgrat „Reihenfolge und Regel“, sie ersetzen die feste Regel, nicht das Problem; die Übersichten dazu sind hier nur auf Abstract-Ebene bekannt und nicht gelesen, und es wird keine Zahl aus ihnen übernommen.

**Bekannte Probleme und Unsicherheiten.** Der „Gewinner“ einer Zelle ist das Verfahren mit dem kleinsten auf zwei Stellen gerundeten Mittel; Gleichstände werden gemeinsam genannt. Der Regret misst gegen das instanzweise Beste nur der Verfahren desselben Bereichs, nicht gegen das Optimum. Die Tausch-Suche enthält als Start die Reihenfolge von MaxRects und ist deshalb nie schlechter als MaxRects; ihr Vorsprung hat den Preis von 200 Auswertungen. Die Empfehlung der Karte gilt für die Zellen des Rasters (Verteilung und Teilezahl wie dort); für andere Instanzen ist sie ein Verfahren für alles im Bereich und eine Extrapolation. Die App wurde im Browser bedient (Presets, Würfel-Button, Auswahlen und Diagramme auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät."""
