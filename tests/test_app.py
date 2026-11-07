"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, stellt jede Auswahl
auf jeden ihrer Werte und das Zahlenfeld an seine Grenzen und prüft, dass kein Python-Fehler auftritt (insbesondere `StreamlitDuplicateElementId`
bei mehreren Diagrammen ohne key= und `StreamlitAPIException` bei Auswahlen mit ungültigem Wert)."""

import os

from streamlit.testing.v1 import AppTest

import pvw_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
WUERFEL = "🎲 Neue Zufallsinstanz würfeln"


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texte(at):
    return [e.value for e in at.info] + [e.value for e in at.success] + [e.value for e in at.warning]


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_selectbox_value_does_not_raise():
    keys = [s.key for s in _fresh_app().selectbox]
    assert {"bereich_select", "quelle_select", "n_select", "exp_bereich"} <= set(keys)
    for bereich in C.BEREICHE:
        for quelle in C.QUELLEN:
            at = _fresh_app()
            at.selectbox(key="bereich_select").set_value(bereich).run(timeout=TIMEOUT)
            at.selectbox(key="quelle_select").set_value(quelle).run(timeout=TIMEOUT)
            assert not at.exception, (bereich, quelle, [str(e) for e in at.exception])
    for n in range(4):
        at = _fresh_app()
        at.selectbox(key="quelle_select").set_value(1).run(timeout=TIMEOUT)
        at.selectbox(key="n_select").set_value(n).run(timeout=TIMEOUT)
        assert not at.exception, (n, [str(e) for e in at.exception])


def test_der_bereich_der_karte_wechselt_ohne_fehler_auch_mit_gewaehltem_n():
    at = _fresh_app()
    for bereich in (0, 1, 2, 3, 0):
        at.selectbox(key="exp_bereich").set_value(bereich).run(timeout=TIMEOUT)
        assert not at.exception, (bereich, [str(e) for e in at.exception])
        at.selectbox(key=f"exp_n_{bereich}").set_value(len(C.MESS_N[bereich]) - 1).run(timeout=TIMEOUT)
        at.selectbox(key=f"exp_verteilung_{bereich}").set_value(3).run(timeout=TIMEOUT)
        assert not at.exception, (bereich, [str(e) for e in at.exception])


def test_zahlenfeld_an_seinen_grenzen_loest_keinen_fehler_aus():
    for bereich in C.BEREICHE:
        for wert in (0, C.SEED_MAX):
            at = _fresh_app()
            at.selectbox(key="bereich_select").set_value(bereich).run(timeout=TIMEOUT)
            at.selectbox(key="quelle_select").set_value(2).run(timeout=TIMEOUT)
            at.number_input(key="seed_input").set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (bereich, wert, [str(e) for e in at.exception])


def test_wuerfeln_wechselt_vom_handbeispiel_zu_einer_zufallsinstanz():
    at = _fresh_app()
    assert at.selectbox(key="quelle_select").value == 0
    at.button[[b.label for b in at.button].index(WUERFEL)].click().run(timeout=TIMEOUT)
    assert at.selectbox(key="quelle_select").value == 1 and not at.exception
    at.selectbox(key="quelle_select").set_value(3).run(timeout=TIMEOUT)
    seed_vorher = at.number_input(key="seed_input").value
    at.button[[b.label for b in at.button].index(WUERFEL)].click().run(timeout=TIMEOUT)
    assert at.selectbox(key="quelle_select").value == 3 and at.number_input(key="seed_input").value != seed_vorher


def test_standardansicht_zeigt_das_erwartete_verdikt():
    at = _fresh_app()
    assert any("Am wenigsten Behälter braucht FFD oder BFD (**5**), am meisten NF (7); die Schranke ist 5. Das Optimum des Handbeispiels ist 5." in t and "Das gehört hier zu den besten." in t for t in _texte(at))


def test_2d_handbeispiel_und_die_experimente_haben_ihre_verdikte():
    at = _fresh_app()
    at.selectbox(key="bereich_select").set_value(1).run(timeout=TIMEOUT)
    texte = _texte(at)
    assert any("Am wenigsten Behälter braucht Skyline oder MaxRects oder MaxRects + Suche (**3**), am meisten Regal (4); die Schranke ist 3." in t for t in texte)
    assert any(t.startswith("Wer in 2D nur ein Verfahren benutzt, fährt mit MaxRects + Suche am besten") for t in texte)
    assert any(t.startswith("In allen 12 Zellen von 2D gehört MaxRects + Suche zu den Gewinnern") for t in texte)


def test_experimente_stehen_unter_ihren_namen_und_expander_unter_ihren_titeln():
    at = _fresh_app()
    markdown = [m.value for m in at.markdown]
    for titel in ("### Experiment 1: Welches Verfahren gewinnt wo?", "### Experiment 2: Ein Verfahren für alles?", "### Experiment 3: Wo dreht sich die Rangfolge?",
                  "### Experiment 4: Ändert die Stützbedingung die Wahl? (3D)"):
        assert any(titel in m for m in markdown), titel
    labels = [e.label for e in at.expander]
    assert "📐 Mathematische Formulierung" in labels and "⚠️ Annahmen, Grenzen und bekannte Probleme" in labels
