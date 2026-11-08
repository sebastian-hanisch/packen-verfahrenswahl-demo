# Verfahrenswahl: welches Packverfahren wann? – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-packen-verfahrenswahl-demo.streamlit.app/)**

Stück 13, der Abschluss der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (ein Verfahren mit wachsendem Beispiel: eine Packung entsteht aus einer Reihenfolge der Teile und einer Regel, wohin das nächste kommt). Die Stücke davor haben Verfahren zum Packen in 1D, 2D und 3D gebaut und einzeln gemessen; diese Demo stellt sie auf **eine Karte**: Für vier Bereiche (Pakete mit einer Größe, Rechtecke, Quader ohne und mit Stützfläche) und vier Mischungen der Teilegrößen zeigt sie, welches Verfahren im Mittel am wenigsten Behälter braucht, was man verliert, wenn man immer dasselbe Verfahren nimmt, und wo sich die Rangfolge dreht. Alle Zahlen sind für diese Demo selbst gemessen.

## Warum dieses Problem

Wer packen muss, hat die Wahl zwischen einfachen und aufwendigen Verfahren und fragt: Lohnt sich der Aufwand, und gilt die Antwort für meine Mischung von Teilen? Die Karte beantwortet das mit Zahlen statt mit Faustregeln: wo sortieren allein genügt (1D), wo eine Suche nach der Reihenfolge noch etwas bringt (2D), wo die Projektionen der Eckpunkte entscheiden (3D) und wie eine Stützbedingung den besten Sortierschlüssel ändert (3D mit Stützfläche).

## Modell

Teile mit ganzzahligen Größen (1D eine Größe, 2D Breite und Höhe, 3D Breite, Tiefe und Höhe), ohne Drehung, alle vorab bekannt; jedes Teil kommt in den ersten Behälter, in dem die Regel des Verfahrens eine Stelle für es hat, sonst in einen neuen. Behälter: 1D Kapazität 1000 (Handbeispiel 100), 2D und 3D Kantenlänge 100. **Verfahren:** *1D* Next Fit (NF), First Fit (FF), Best Fit (BF), jeweils in Lieferreihenfolge, und FFD und BFD (größte zuerst). *2D* Regal (erstes passendes Regal, nach Höhe sortiert), Skyline (niedrigste Stelle, nach Fläche), MaxRects mit der kleinsten kurzen Restkante (BSSF, nach Fläche), MaxRects mit einer **Tausch-Suche** nach der Reihenfolge (zwei Positionen der besten Reihenfolge vertauschen, behalten, wenn (Behälter, Fläche im leersten Behälter) nicht größer wird; 200 Auswertungen). *3D* Schichten (nach Höhe), Extreme Points ohne und mit Projektionen der Eckpunkte (nach Volumen); im vierten Bereich mit einer **Mindest-Stützfläche von 80 %** Extreme Points mit Projektionen nach Volumen, Grundfläche oder Höhe. **Maßstab:** die untere Schranke (1D $L_2$, 2D Fläche und große Rechtecke, 3D Volumen und große Quader). **Gewinner** einer Zelle: das Verfahren mit dem kleinsten auf zwei Stellen gerundeten Mittel an Behältern über der Schranke (Gleichstände gemeinsam). **Regret:** Behälter mehr als das instanzweise Beste der Verfahren desselben Bereichs. **Ein Verfahren für alles:** das mit dem kleinsten Regret über alle Zellen des Bereichs. **Vier Verteilungen** je Bereich (1D: klein 1 bis 25 %, mittel 10 bis 50 %, groß 20 bis 80 %, breit 1 bis 90 % der Kapazität; 2D: mittel 20 bis 60, breit 5 bis 70, klein 10 bis 40, hoch schmal Breite 5 bis 30 und Höhe 30 bis 80; 3D: mittel, breit, klein wie in 2D mit drei Kanten, flach Breite und Tiefe 30 bis 80, Höhe 5 bis 30). Formeln im Expander 📐 der App.

## Methodik

- **Kern** (`pvw_algorithm.py`, nur Standardbibliothek): je Dimension die Verfahren (`pack_1d`, `pack_2d`, `pack_3d`, `suche_2d`), die Schranken (`l1_1d`, `l2_1d`, `schranken_2d`, `schranken_3d`), die Stützfläche (`stuetzflaeche_3d`) und je Dimension ein unabhängiger Packungsprüfer; dazu der exakte Teilmengen-DP `optimum_1d` für höchstens zwölf Pakete. Alle Zufallszahlen der Tausch-Suche kommen aus `random.Random(seed).random()`.
- **Handbeispiele:** je Bereich zwölf Teile mit bekanntem Optimum (1D der Handbeispiel-Satz von 459 Größeneinheiten in Behältern zu 100; 2D und 3D zwölf Teile aus Messrastern, Optimum mit CP-SAT in den Tests nachgerechnet).
- **Messraster:** vier Bereiche × je vier Verteilungen × drei Teilezahlen (2D und 3D: 20, 40, 80; 1D: 20, 50, 100, 200) × **100 feste Instanzen** je Zelle (1D **200**); jedes Verfahren des Bereichs läuft auf jeder Instanz. Es gibt kein Optimum im Raster, der Maßstab ist die Schranke. Die Summen stehen als ganze Zahlen in `pvw_precomputed.json` (erzeugt von `generate_precomputed.py`).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an den Instanzen dieser Demo (feste Seeds), nachgerechnet in `tests/test_claims.py`, `tests/test_algorithm.py` und `tests/test_oracle_verfahrenswahl.py`. Tabellenwerte sind Mittel über die Instanzen einer Zelle von (Behälter minus Schranke); ★ markiert den Gewinner.

| Frage | Befund |
|---|---|
| Handbeispiele | 1D: NF, FF, BF **7** Behälter, FFD und BFD **5** (Optimum 5). 2D: Regal **4**, Skyline, MaxRects und die Suche **3** (Optimum 3). 3D: Schichten und EP einfach **2**, EP voll **1** (Optimum 1) |
| 1D: Wer gewinnt? | **FFD und BFD in allen 16 Zellen** (in 14 gleichauf, in zwei, breit bei n = 20 und n = 200, BFD allein mit 0,01 Vorsprung). Sortieren bringt hier den größten Gewinn: Regret FFD und BFD unter 0,01 (beste Instanzen 99,9 % und 100 %, gerundet), First Fit 1,73, Best Fit 1,33, Next Fit **8,50** (alle drei in Lieferreihenfolge); sortiert ist die Regel fast egal |
| 1D: FFD gegen BFD | Sie unterscheiden sich in **2 von 3200** Instanzen (FFD braucht dann einen Behälter mehr als BFD) |
| 2D: Wer gewinnt? | **MaxRects mit Tausch-Suche in allen 12 Zellen**, in 99 bis 100 % der Instanzen gehört sie zu den besten; Vorsprung gegenüber MaxRects ohne Suche 0,01 bis 0,46 Behälter. Sie braucht 200 Auswertungen statt einer |
| 2D: Ein Verfahren mit einer Auswertung | **MaxRects** (Regret 0,20) vor Regal (0,34) und Skyline (0,39) |
| 2D: Dreht sich die Rangfolge? | **Ja, bei den einfachen Verfahren:** Regal ist besser als Skyline in 5 Zellen, schlechter in 6, gleich gut in 1; Regal ist besser als MaxRects in 1 Zelle, schlechter in 9, gleich gut in 2 |
| 3D: Wer gewinnt? | **Extreme Points mit Projektionen** in 10 Zellen allein, in zwei gleichauf (kleine Quader: bei n = 20 alle drei, bei n = 80 mit EP einfach). Regret EP voll **0,02**, EP einfach 0,20, Schichten **0,72** |
| 3D: Dreht sich die Rangfolge? | Nur bei den unterlegenen Verfahren: Schichten sind besser als EP einfach in **1** Zelle (flache Quader, n = 20: 0,89 gegen 1,01), schlechter in 10, gleich gut in 1 |
| 3D mit Stützfläche: Wer gewinnt? | **Extreme Points mit der Grundfläche als Schlüssel in allen 12 Zellen im Mittel vorn** (Regret **0,06**, Volumen 0,59, Höhe 1,11); flache Quader bei n = 80: Grundfläche 4,02, Volumen 6,20, Höhe 7,01. In vier Zellen (mittlere Quader bei n = 20, 40 und 80, kleine Quader bei n = 40) liegt der Vorsprung vor dem Volumen innerhalb der Streuung |
| Ändert die Stützbedingung die Wahl? | **Ja:** Ohne Bedingung gewinnt Extreme Points mit Projektionen nach Volumen (in allen 12 Zellen unter den Gewinnern), mit 80 % Stützfläche in allen 12 Zellen im Mittel die Grundfläche. Der Schlüssel Grundfläche ist ohne Bedingung in der Karte nicht gemessen. Die Bedingung kostet im jeweils besten Verfahren **0,33 bis 1,83** Behälter über der Schranke (am meisten bei flachen Quadern); bei kleinen Quadern mit n = 20 sind es nur +0,02, nicht von null zu trennen. Es sind Differenzen zweier getrennter Stichproben mit je 100 Instanzen |
| Gilt „ein Verfahren für alles“? | In jedem Bereich gewinnt im gerundeten Mittel dasselbe Verfahren (oder gleichauf) in allen Zellen: **der Gewinner dreht sich nirgends**; wo sich etwas dreht, sind es die Plätze dahinter. Die Wahl hängt in dieser Karte vom Bereich ab, nicht von den vier gemessenen Mischungen |

**Die Handbeispiele** (Behälter je Verfahren; die Schranke ist beim 3D-Bereich mit Stützfläche ohne Bedingung berechnet, das Optimum ebenfalls):

{{BEISPIELE}}

**Regret und Anteil bester Instanzen** (über alle Zellen des Bereichs; Regret: Behälter mehr als das instanzweise Beste des Bereichs; Prozentwerte gerundet, 100 % kann knapp darunter liegen):

{{REGRET}}

**Karte 1D** (Mittel an Behältern über L2; 200 Instanzen je Zelle):

{{KARTE_1D}}

**Karte 2D** (Mittel über der Schranke aus Fläche und großen Rechtecken; 100 Instanzen je Zelle):

{{KARTE_2D}}

**Karte 3D** (Mittel über der Schranke aus Volumen und großen Quadern, ohne Stützbedingung):

{{KARTE_3D}}

**Karte 3D mit 80 % Stützfläche** (dieselben Verteilungen und Teilezahlen, aber eigene Zufallsinstanzen; die Verfahren sind drei Sortierschlüssel für Extreme Points mit Projektionen):

{{KARTE_3DS}}

**Wirkung der Stützbedingung auf die Wahl** (3D, Gewinner beider Karten je Zelle; Mehrbedarf = bestes Mittel mit Bedingung minus ohne):

{{STUETZ}}

## Ehrliche Grenzen

- Alle Aussagen gelten für diese Verfahren und Sortierschlüssel, vier Verteilungen je Bereich, die genannten Teilezahlen, Teile ohne Drehung und eine Behältergröße. Andere Regeln, andere Suchen und Praxisdaten sind nicht gemessen; die Empfehlung der Karte ist für andere Mischungen eine Extrapolation.
- Der Maßstab ist die **Schranke**; in 2D und 3D ist sie locker. Gelesen werden die Unterschiede zwischen den Verfahren, nicht der Abstand. Ein Optimum gibt es nur beim Handbeispiel.
- Die Tausch-Suche startet bei MaxRects und ist deshalb nie schlechter als MaxRects; ihr Vorsprung hat den Preis von 200 Auswertungen. Die Karte sagt nichts über Rechenzeit.
- Der Regret misst gegen das instanzweise Beste der Verfahren desselben Bereichs, nicht gegen das Optimum, und ist zwischen den Bereichen nicht vergleichbar.
- **Gelernte Platzierungsregeln** (Verfahren des Maschinenlernens, die die Regel „wohin kommt das nächste Teil“ aus Beispielen lernen) fehlen: Eine gelernte Regel ist nur eine weitere Platzierungsregel im Rückgrat „Reihenfolge und Regel“ und ersetzt die feste Regel, nicht das Problem. Die Übersichten dazu sind hier nur auf Abstract-Ebene bekannt und nicht gelesen; es wird keine Zahl aus ihnen übernommen.
- Die Extreme Points sind nach eigener Lesart der Originalarbeit umgesetzt (nicht gelesen); es wird keine Zahl und keine Aussage der Literatur übernommen.

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

{{ANNAHMEN}}

## Verifikation

- **Kern:** je Dimension an einer von Hand gerechneten Mini-Instanz (1D zwölf Pakete: First, Best und Next Fit mit den Behältern von Hand, FFD und BFD mit den Füllungen 100, 95, 93, 99, 72, L1, L2 und Optimum; 2D vier Rechtecke: Regal, Skyline und MaxRects mit den Platzierungen, das Regal auch nach Höhe sortiert, die Zufallszahlen der Startzahl 1 und die Tausch-Suche von Hand; 3D zwei Mini-Instanzen: Extreme Points mit und ohne Projektionen, Schichten, die Stützfläche 43,75 / 87,5 / 100 %); unabhängige Prüfer in jeder Dimension; Randfälle (leere Eingabe, ein Teil, Teil gleich Behälter, acht Würfel füllen den Behälter genau, Gleichstände, ungültige Eingaben, Grenzen der Regler, die Empfehlung der Karte).
- **Orakel** (`tests/test_oracle_verfahrenswahl.py`): 1D First, Best und Next Fit gegen naive Umsetzungen, L2 gegen eine Rechnung über alle ganzzahligen alpha, Optimum gegen die Aufzählung aller Zuordnungen; 2D MaxRects gegen die Aufzählung aller maximalen leeren Rechtecke aus einem Belegungsraster, Skyline gegen das Profil aus der Liste, Regal gegen eine naive Neuberechnung; 3D Extreme Points (einfach, voll, mit Mindest-Stützfläche) gegen neu erzeugte Eckpunkte und eine Voxel-Stützfläche, Schichten gegen eine naive Neuberechnung; CP-SAT-Optimum in 2D und 3D nie über den Verfahren; jede Packung zulässig und nie unter der Schranke; gemeinsames Skalieren.
- **Messraster:** jede Zelle bei n = 20 wird frisch gerechnet und exakt mit `pvw_precomputed.json` verglichen, bei allen Zellen die ersten drei Instanzen einzeln (Stichprobe in der Datei); alle Zellen zusammen prüft `python generate_precomputed.py --check` (parallel). Die Handbeispiele werden mit CP-SAT beziehungsweise dem Teilmengen-DP nachgerechnet; jede Zahl dieser README als Textsuche (`tests/test_claims.py`).
- **Verdikte:** alle Zweige und Schwellen an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, erstes Preset gleich Standardeinstellung, jeder Hilfetext stimmt mit der Rechnung überein; Schnellstart oben in der Seitenleiste, fester Kopf, genau das passende Preset hervorgehoben (`tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, der Wechsel des Bereichs der Karte, Startzahl an den Grenzen) und Footer-Test.
- **Tests gesamt:** {{TESTS}}.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `dev/opt_2d.py`, `dev/opt_3d.py` | exaktes Optimum mit CP-SAT in 2D und 3D (nur für die Tests der Handbeispiele und Orakel) |
| `dev/readme_bauen.py`, `dev/readme_vorlage.md` | setzen die README aus der Vorlage, den Tabellen der Karte und dem Text der Annahmen zusammen |
| `generate_precomputed.py` | erzeugt `pvw_precomputed.json` (Messraster und Stichprobe); `--check` vergleicht, `--nur-stichprobe` ergänzt die Stichprobe |
| `pvw_algorithm.py` | Kern: Verfahren, Schranken, Stützfläche, Prüfer und Suche je Dimension |
| `pvw_constants.py` | Bereiche, Verteilungen, Verfahren, Handbeispiele, Messraster, Farben, Presets, Text der Annahmen |
| `pvw_evaluation.py` | Analyse, Karte, Regret, Verdikte, Messzellen |
| `pvw_layout.py` | Fester Kopf (Stylesheet) und Tabellen auf dem Telefon |
| `pvw_precomputed.json` | vorberechnete Summen und Stichprobe des Messrasters |
| `pvw_presets.py` | Permalink (Begrenzen), Presets (Schnellstart, aktives Preset hervorgehoben), Würfel-Button |
| `pvw_scenario.py` | Instanzen: Handbeispiele und Zufallsinstanzen mit festen Seeds, je Bereich |
| `pvw_visualization.py` | Plotly-Abbildungen (Balken, Karte als Wärmebild, Regret; Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest und ortools |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanzen und Handrechnung, Orakel, Randfälle, Verdikte, Presets, Layout, Abbildungen, Messraster und Zahlen der README, AppTest-Rauchtest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Gelernte Platzierungsregeln:** kein eigenes Stück, nur der Absatz oben; sie bräuchten ein trainiertes Modell und hätten kaum ein Orakel.
- **Weitere Verfahren und Suchen** (Tabu-Suche, genetische Verfahren, andere Dekodierer): nicht Gegenstand dieses Stücks.
- **Laufzeitvergleich:** hängt an der Umsetzung, keine Aussage; die Karte zählt nur Auswertungen.
- **Optimum im Raster:** zu teuer für die Teilezahlen der Karte; der Maßstab ist die Schranke.
- **Gütegarantien und Zahlen aus der Literatur:** keine übernommen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
