"""Packen: Verfahrenswahl, welches Packverfahren wann? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 13 der Reihe „Packen: Reihenfolge und Platzierungsregel“, der Abschluss. Die Karte zeigt, welches Verfahren bei welcher Mischung gewinnt: selbst gemessen an je 100 oder 200 Zufallsinstanzen
je Zelle, in vier Bereichen (1D, 2D, 3D, 3D mit Stützfläche). Das Messraster ist in pvw_precomputed.json vorberechnet.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import pvw_constants as C
from pvw_evaluation import (
    Settings,
    analyse,
    paar_zaehlung,
    stuetz_zeilen,
    uebersicht,
    verdict_instanz,
    verdict_karte,
    verdict_regret,
    verdict_stuetz_wahl,
    verdict_wechsel,
    zeile,
    zellen_von,
)
from pvw_layout import dunkles_design, kopf_css
from pvw_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from pvw_visualization import build_instanz, build_karte, build_regret

st.set_page_config(page_title="Packen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in pvw_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧭 Verfahrenswahl: welches Packverfahren wann?")
st.markdown(
    """
Zwölf Stücke dieser Reihe haben Verfahren zum Packen gebaut und einzeln gemessen. Hier steht alles auf **einer Karte**: Für vier Bereiche (Pakete mit einer Größe, Rechtecke, Quader ohne und mit Stützfläche) und vier Mischungen der Teilegrößen zeigt sie, **welches Verfahren im Mittel am wenigsten Behälter braucht**, wie viel man verliert, wenn man **immer dasselbe Verfahren** nimmt, und **wo sich die Rangfolge dreht**. Oben wählen Sie eine Instanz und sehen, ob die Empfehlung der Karte stimmt.

Weiter unten: der Abschnitt **🔬 Experimente**, **🚧 Wo die Annahmen enden**, der Expander **⚠️ Annahmen, Grenzen und bekannte Probleme** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So lesen Sie die Karte", expanded=True):
    st.markdown(
        """
1. **Bereich und Instanz wählen:** links ein Bereich (1D, 2D, 3D, 3D mit Stützfläche) und eine Instanz (das Handbeispiel oder eine Zufallsinstanz mit einer der vier Verteilungen). Alle Verfahren des Bereichs packen dieselben Teile.
2. **Maßstab:** die untere **Schranke** (1D L2, 2D Fläche und große Rechtecke, 3D Volumen und große Quader). Sie ist in 2D und 3D locker; lesen Sie die Unterschiede zwischen den Verfahren, nicht den Abstand.
3. **Gewinner und Regret:** Der Gewinner einer Zelle ist das Verfahren mit dem kleinsten Mittel an Behältern über der Schranke. Der **Regret** eines Verfahrens ist, wie viele Behälter es im Mittel mehr braucht als das instanzweise Beste des Bereichs. „Ein Verfahren für alles“ ist das mit dem kleinsten Regret über alle Zellen.
4. **Auswertungen:** Die Tausch-Suche in 2D probiert 200 Reihenfolgen, jedes andere Verfahren eine. Die Karte sagt nichts über Rechenzeit, nur über die Zahl der Auswertungen.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    bereich = st.selectbox("Bereich", list(C.BEREICHE), format_func=C.BEREICHE.get, key="bereich_select", help="Wovon die Karte handelt: Pakete mit einer Größe, Rechtecke oder Quader (ohne oder mit Mindest-Stützfläche).")
    bereich = int(bereich)

    def _quelle_name(q):
        return "Handbeispiel (zwölf Teile)" if q == 0 else "zufällig, " + C.VERTEILUNG_LANG[bereich][q - 1]

    quelle = st.selectbox("Instanz", list(C.QUELLEN), format_func=_quelle_name, key="quelle_select",
                          help="Das Handbeispiel hat zwölf feste Teile (mit bekanntem Optimum). Die vier anderen sind Zufallsinstanzen mit verschiedener Verteilung der Größen.")
    n_index = st.selectbox("Zahl der Teile (nur Zufallsinstanzen)", list(range(len(C.APP_N[bereich]))), format_func=lambda i: str(C.APP_N[bereich][i]), key="n_select",
                           help="Gilt nur für Zufallsinstanzen. Nur 20, 40, 80 (in 1D 20, 50, 100) sind Zellen der Karte; bei 12 ist die Empfehlung ein Verfahren für alles.")
    seed = st.number_input("Startzahl der Zufallsinstanz", *bounds("seed_input"), key="seed_input", step=1, help="Wirkt nur bei den Zufallsinstanzen (und bei der Startzahl der Tausch-Suche in 2D).")
    st.button("🎲 Neue Zufallsinstanz würfeln", width="stretch", on_click=randomize_seed)

sync_query_params({"bereich_select": bereich, "quelle_select": int(quelle), "n_select": int(n_index), "seed_input": int(seed)})

settings = Settings(bereich, int(quelle), int(n_index), int(seed))
a = _analysis(settings)
verf = C.VERFAHREN[bereich]

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Bestes Verfahren", " / ".join(verf[m] for m in a.beste), delta="Behälter: " + str(a.zaehlungen[a.beste[0]]), delta_color="off")
m2.metric("Schlechtestes", max(a.zaehlungen), delta=max(a.zaehlungen) - a.zaehlungen[a.beste[0]], delta_color="inverse", help="Behälter des schlechtesten Verfahrens; Delta: Unterschied zum besten.")
if a.optimum is not None:
    m3.metric("Optimum" + (" (ohne Stützbedingung)" if bereich == C.DREI_STUETZ else ""), a.optimum, delta="Referenz", delta_color="off")
else:
    m3.metric("Optimum", "nicht berechnet", delta="nur für das Handbeispiel", delta_color="off")
m4.metric("Untere Schranke", a.schranke, delta="locker in 2D und 3D" if bereich != C.EINS else "L2", delta_color="off")
st.caption(f"{a.inst.n} {C.TEIL[bereich]}, Behälter {a.inst.cap}" + (" (Mindest-Stützfläche 80 %)." if bereich == C.DREI_STUETZ else "."))
st.plotly_chart(build_instanz(bereich, a.zaehlungen, a.schranke, a.beste, a.empfehlung), width="stretch", key="main_chart")
st.caption("Die besten Verfahren dieser Instanz sind farbig, die anderen grau; ★ markiert die Empfehlung der Karte, die rote Linie ist die Schranke.")
kind, text = verdict_instanz(a)
getattr(st, kind)(text)

tab = ["| Verfahren | Behälter | über Schranke | Auswertungen |", "|---|---|---|---|"]
for m, name in enumerate(verf):
    fett = "**" if m in a.beste else ""
    tab.append(f"| {fett}{name}{' ★' if m in a.empfehlung else ''}{fett} | {fett}{a.zaehlungen[m]}{fett} | {a.zaehlungen[m] - a.schranke} | {C.AUSWERTUNGEN[bereich][m]} |")
st.markdown("\n".join(tab))
st.caption("Fett: das beste Verfahren dieser Instanz. ★: Empfehlung der Karte (" + ("für genau diese Zelle der Karte" if a.empfehlung_art == "Zelle" else "ein Verfahren für alles in diesem Bereich") + "). "
           + "; ".join(f"{verf[m]}: {C.VERFAHREN_LANG[bereich][m]}" for m in range(len(verf))) + ".")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experimente: Die Karte")
st.caption("Gemessen an festen Zufallsinstanzen (1D 200, sonst 100 je Zelle), ohne Drehung. Die Zahlen sind vorberechnet (`generate_precomputed.py`). Der Maßstab ist die Schranke; ein Optimum gibt es nur beim Handbeispiel.")
exp_b = int(st.selectbox("Bereich der Karte", list(C.BEREICHE), index=1, format_func=C.BEREICHE.get, key="exp_bereich"))
zellen = zellen_von(exp_b)
zeilen = [zeile(exp_b, v, ni) for v, ni in zellen]
namen = [f"{C.VERTEILUNG_KURZ[exp_b][z['verteilung']]}, n = {z['n']}" for z in zeilen]

st.markdown("### Experiment 1: Welches Verfahren gewinnt wo?")
st.plotly_chart(build_karte(exp_b, namen, [z["mittel"] for z in zeilen], [z["gewinner"] for z in zeilen]), width="stretch", key="karte_chart")
kopf = "| Zelle | " + " | ".join(C.VERFAHREN[exp_b]) + " |"
t1 = [kopf, "|---|" + "---|" * len(C.VERFAHREN[exp_b])]
for name, z in zip(namen, zeilen):
    t1.append(f"| {name} | " + " | ".join(f"{x:.2f}" + (" ★" if m in z["gewinner"] else "") for m, x in enumerate(z["mittel"])) + " |")
st.markdown("\n".join(t1))
st.caption("Mittlere Behälter über der Schranke je Zelle; ★ = Gewinner (kleinstes auf zwei Stellen gerundetes Mittel, Gleichstände gemeinsam).")
c1, c2 = st.columns(2)
vert = c1.selectbox("Verteilung", list(range(len(C.VERTEILUNGEN[exp_b]))), format_func=lambda i: C.VERTEILUNGEN[exp_b][i][1], key=f"exp_verteilung_{exp_b}")
nn = c2.selectbox("Zahl der Teile n", list(range(len(C.MESS_N[exp_b]))), format_func=lambda i: str(C.MESS_N[exp_b][i]), key=f"exp_n_{exp_b}")
zz = zeile(exp_b, int(vert), min(int(nn), len(C.MESS_N[exp_b]) - 1))
kind, text = verdict_karte(zz)
getattr(st, kind)(text)
st.caption("Anteil der Instanzen, in denen das Verfahren zu den besten gehört: " + ", ".join(f"{C.VERFAHREN[exp_b][m]} {zz['beste'][m]:.0f} %" for m in range(len(zz["beste"]))) + ".")

st.markdown("### Experiment 2: Ein Verfahren für alles?")
u = uebersicht(exp_b)
st.plotly_chart(build_regret(exp_b, u["regret"], u["beste"]), width="stretch", key="regret_chart")
t2 = ["| Verfahren | mittlerer Regret | Anteil bester Instanzen | Mittel über Schranke | Auswertungen |", "|---|---|---|---|---|"]
for m, name in enumerate(C.VERFAHREN[exp_b]):
    t2.append(f"| {name} | {u['regret'][m]:.2f} | {u['beste'][m]:.0f} % | {u['mittel'][m]:.2f} | {C.AUSWERTUNGEN[exp_b][m]} |")
st.markdown("\n".join(t2))
st.caption(f"Über alle {u['instanzen']} Instanzen des Bereichs. Regret: Behälter mehr als das instanzweise Beste der Verfahren dieses Bereichs. Die Prozentwerte sind gerundet; 100 % kann knapp darunter liegen.")
kind, text = verdict_regret(u)
getattr(st, kind)(text)

st.markdown("### Experiment 3: Wo dreht sich die Rangfolge?")
kind, text = verdict_wechsel(exp_b)
getattr(st, kind)(text)
t3 = ["| A | B | A besser | B besser | gleich |", "|---|---|---|---|---|"]
for a_, b_, ab, ba, gl in paar_zaehlung(exp_b):
    t3.append(f"| {C.VERFAHREN[exp_b][a_]} | {C.VERFAHREN[exp_b][b_]} | {ab} | {ba} | {gl} |")
st.markdown("\n".join(t3))
st.caption(f"Zahl der Zellen (von {len(zellen)}), in denen A beziehungsweise B im gerundeten Mittel besser ist. Eine Reihenfolge dreht sich, wenn beide Seiten mindestens eine Zelle haben.")

st.markdown("### Experiment 4: Ändert die Stützbedingung die Wahl? (3D)")
sz = stuetz_zeilen()
t4 = ["| Zelle | ohne Bedingung: Gewinner | mit 80 % Stützfläche: Gewinner | Mehrbedarf des Besten |", "|---|---|---|---|"]
for r in sz:
    ohne = " / ".join(C.VERFAHREN[C.DREI][m] for m in r["ohne"])
    mit = " / ".join(C.VERFAHREN[C.DREI_STUETZ][m] for m in r["mit"])
    t4.append(f"| {C.VERTEILUNG_KURZ[C.DREI][r['verteilung']]}, n = {r['n']} | {ohne} | {mit} | {r['mehr']:+.2f} |")
st.markdown("\n".join(t4))
st.caption("Je Zelle der 3D-Karten das Gewinnerverfahren ohne und mit Mindest-Stützfläche; Mehrbedarf = bestes Mittel über der Schranke mit Bedingung minus ohne. Die Verfahren der beiden Bereiche sind verschieden: dort Schichten, EP einfach, EP voll; hier drei Sortierschlüssel für EP voll auf eigenen Zufallsinstanzen (gleiche Verteilungen und Teilezahlen). Der Mehrbedarf ist die Differenz zweier getrennter Stichproben.")
kind, text = verdict_stuetz_wahl(sz)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist |
|---|---|
| **Nur diese Verfahren und Schlüssel** | Andere Regeln, andere Suchen und andere Sortierschlüssel sind nicht gemessen; die Karte vergleicht nur die hier aufgeführten. |
| **Die Teile sind zufällig verteilt** | Nur vier Verteilungen je Bereich mit festen Bereichen sind gemessen. Echte Aufträge können anders aussehen: Dann ist die Empfehlung eine Extrapolation. |
| **Die Schranke ist der Maßstab** | In 2D und 3D ist sie locker; ein Optimum gibt es nur beim Handbeispiel. Gelesen werden nur die Unterschiede zwischen den Verfahren. |
| **Auswertungen statt Zeit** | Die Karte zählt, wie oft eine Reihenfolge dekodiert wird, und macht keine Aussage zur Rechenzeit. |
| **Gelernte Platzierungsregeln** | Sie fehlen. Eine gelernte Regel ersetzt die feste Regel, nicht das Rückgrat „Reihenfolge und Regel“; ohne eigene Messung gibt es keine Zahl dazu. |
| **Alle Teile sind vor dem Packen bekannt** | Wer jedes Teil sofort einsortieren muss, kann nicht sortieren. Das ist Online-Packen. Mehr dazu: [Online](https://sebastianhanisch.net/konzepte-online-algorithmen.html). |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(C.ASSUMPTIONS_MARKDOWN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** *Gegeben:* eine Menge von Teilen (1D Größen $s_i$, 2D Rechtecke $(w_i, h_i)$, 3D Quader $(w_i, d_i, h_i)$) und Behälter der Kapazität $C$ beziehungsweise der Kantenlänge $C$; ein Verfahren $v$ aus einer endlichen Menge $V$ (je Bereich). *Gesucht:* für eine Mischung (Verteilung und Teilezahl) das Verfahren, das im Mittel am wenigsten Behälter braucht.

| Symbol | Bedeutung |
|---|---|
| $I$ | eine Instanz (ein Satz von Teilen) |
| $B_v(I)$ | Behälterzahl von Verfahren $v$ auf $I$ |
| $L(I)$ | untere Schranke (1D $L_2$, 2D Fläche und große Rechtecke, 3D Volumen und große Quader) |
| $\mathcal{I}_z$ | die Instanzen der Zelle $z$ (Verteilung und Teilezahl) |
| $\mathrm{OPT}(I)$ | kleinste mögliche Behälterzahl (nur beim Handbeispiel bekannt) |

**Mittel über der Schranke.** $m_v(z) = \dfrac{1}{|\mathcal{I}_z|} \sum_{I \in \mathcal{I}_z} \bigl(B_v(I) - L(I)\bigr)$. Der **Gewinner** der Zelle ist $\arg\min_v \mathrm{rund}_2(m_v(z))$; bei Gleichstand gewinnen alle Gleichauf-Verfahren.

**Instanzweises Bestes und Regret.** $B^\ast(I) = \min_{v \in V} B_v(I)$. Der Regret von $v$ in $z$ ist $r_v(z) = \dfrac{1}{|\mathcal{I}_z|} \sum_{I \in \mathcal{I}_z} \bigl(B_v(I) - B^\ast(I)\bigr)$, über alle Zellen des Bereichs $r_v = \dfrac{\sum_z \sum_{I \in \mathcal{I}_z} (B_v(I) - B^\ast(I))}{\sum_z |\mathcal{I}_z|}$. **Ein Verfahren für alles** ist $\arg\min_v \mathrm{rund}_2(r_v)$. Der Anteil bester Instanzen ist $\Pr_I[B_v(I) = B^\ast(I)]$.

**Drehende Paare.** Ein Paar $(a, b)$ dreht sich im Bereich, wenn es Zellen mit $\mathrm{rund}_2(m_a) < \mathrm{rund}_2(m_b)$ und Zellen mit $\mathrm{rund}_2(m_a) > \mathrm{rund}_2(m_b)$ gibt.

**Die Verfahren.** Alle haben dieselbe Bauart: eine Reihenfolge der Teile (ein Sortierschlüssel oder eine gesuchte Reihenfolge) und eine Regel, wohin das nächste Teil kommt. *1D:* Next Fit, First Fit, Best Fit, jeweils in Lieferreihenfolge oder nach fallender Größe (FFD, BFD). *2D:* Regal (erstes passendes Regal), Skyline (niedrigste Stelle), MaxRects mit der kleinsten kurzen Restkante (BSSF), MaxRects mit einer Tausch-Suche: Zwei zufällige Positionen der besten Reihenfolge werden vertauscht, die neue wird behalten, wenn (Behälterzahl, Fläche im leersten Behälter) lexikographisch nicht größer wird; 200 Auswertungen. *3D:* Schichten, Extreme Points mit und ohne Projektionen der Eckpunkte, im vierten Bereich mit der Mindest-Stützfläche $0{,}8$: ein Eckpunkt ist nur zulässig, wenn der Quader dort auf mindestens $80\,\%$ seiner Grundfläche aufliegt.

**Schranken.** 1D: $L_1 = \lceil \sum_i s_i / C \rceil$ und $L_2$ nach Martello und Toth (Pakete über der Hälfte brauchen je einen eigenen Behälter, die kleineren füllen deren Rest). 2D: $\lceil \sum_i w_i h_i / C^2 \rceil$ und die Zahl der Rechtecke mit $w_i, h_i > C/2$. 3D: $\lceil \sum_i w_i d_i h_i / C^3 \rceil$ und die Zahl der Quader mit $w_i, d_i, h_i > C/2$; jeweils das Größere.

**Literatur.** Keine Zahl und keine Aussage der Literatur ist in diese Demo übernommen; alle Zahlen sind selbst gemessen. Zu gelernten Platzierungsregeln ist nur bekannt, dass es Übersichten zum Maschinenlernen für mehrdimensionales Packen gibt (nur auf Abstract-Ebene, ungelesen).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
