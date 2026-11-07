"""Presets: Vollständigkeit, gültige Werte, erstes Preset = Standardeinstellungen, jeder Hilfetext stimmt mit der Rechnung überein."""

import pvw_constants as C
import pvw_evaluation as ev
import pvw_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_widget_bounds():
    for name, preset in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            spec = P.SETTING_SPECS[state_key]
            assert spec.lo <= preset[key] <= spec.hi, (name, key)


def test_first_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_defaults_of_the_widgets_equal_the_default_settings():
    s = ev.Settings()
    assert [P.SETTING_SPECS[k].default for k in ("bereich_select", "quelle_select", "n_select", "seed_input")] == [s.bereich, s.quelle, s.n_index, s.seed]


def _a(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


def test_presets_behaupten_nur_was_stimmt():
    eins = _a("1D: das Handbeispiel")
    assert eins.zaehlungen == (7, 7, 7, 5, 5) and eins.optimum == 5 == eins.schranke and eins.beste == (3, 4) and eins.empfehlung == (3, 4)
    assert "sieben Behälter, größte zuerst (FFD und BFD) fünf, so viele wie das Optimum" in C.PRESET_HELP["1D: das Handbeispiel"] and "empfiehlt in 1D FFD oder BFD" in C.PRESET_HELP["1D: das Handbeispiel"]
    zwei = _a("2D: das Handbeispiel")
    assert zwei.zaehlungen == (4, 3, 3, 3) and zwei.optimum == 3 and zwei.empfehlung == (3,)
    assert "Das Regal braucht vier Behälter, Skyline, MaxRects und die Suche drei, das Optimum" in C.PRESET_HELP["2D: das Handbeispiel"]
    drei = _a("2D: mittlere Rechtecke, 40 Stück")
    assert drei.inst.n == 40 and drei.zaehlungen == (8, 8, 8, 7) and drei.schranke == 7 and drei.beste == (3,)
    assert "Regal, Skyline und MaxRects brauchen acht Behälter, MaxRects mit Tausch-Suche sieben (die Schranke)" in C.PRESET_HELP["2D: mittlere Rechtecke, 40 Stück"]
    vier = _a("3D: flache Quader, 20 Stück")
    assert vier.inst.n == 20 and vier.zaehlungen == (2, 3, 2) and vier.schranke == 1 and vier.beste == (0, 2)
    assert "Schichten brauchen zwei Behälter, Extreme Points ohne Projektionen drei, mit Projektionen zwei" in C.PRESET_HELP["3D: flache Quader, 20 Stück"]
    fuenf = _a("3D mit Stützfläche: flache Quader, 40 Stück")
    assert fuenf.inst.n == 40 and fuenf.zaehlungen == (8, 5, 9) and fuenf.schranke == 3 and fuenf.beste == (1,)
    assert "Mit der Grundfläche als Schlüssel fünf Behälter, mit dem Volumen acht, mit der Höhe neun" in C.PRESET_HELP["3D mit Stützfläche: flache Quader, 40 Stück"]
