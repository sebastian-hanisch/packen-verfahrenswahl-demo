"""Plotly-Abbildungen: Balken je Verfahren für eine Instanz und die Karte als Wärmebild. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import pvw_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def build_instanz(bereich, zaehlungen, schranke, beste, empfehlung):
    """Behälter je Verfahren für die Instanz: die besten Verfahren in der Farbe des Bereichs, die anderen blass; die Schranke als waagerechte Linie; die Empfehlung der Karte mit einem Stern im Namen."""
    namen = [C.VERFAHREN[bereich][m] + (" ★" if m in empfehlung else "") for m in range(len(zaehlungen))]
    farben = [C.VERFAHREN_FARBEN[m] if m in beste else "rgba(150,150,150,0.55)" for m in range(len(zaehlungen))]
    fig = go.Figure(go.Bar(x=namen, y=list(zaehlungen), marker_color=farben, text=list(zaehlungen), textposition="outside", hovertemplate="%{x}: %{y} Behälter<extra></extra>"))
    fig.add_hline(y=schranke, line=dict(color=C.COLOR_LINE, width=2, dash="dash"), annotation_text="Schranke", annotation_position="top left")
    fig.update_yaxes(title_text="Behälter", range=[0, max(max(zaehlungen), schranke) + 1.5], dtick=1)
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    return lock_axes(fig)


def build_karte(bereich, zeilennamen, mittel, gewinner):
    """Die Karte als Wärmebild: je Zelle (Zeile) und Verfahren (Spalte) die mittleren Behälter über der Schranke; die Gewinner jeder Zeile sind mit einem Stern markiert. `mittel[zeile][verfahren]`,
    `gewinner[zeile]` = Verfahren mit dem kleinsten Mittel."""
    text = [[f"{x:.2f}" + (" ★" if m in gewinner[r] else "") for m, x in enumerate(zeile)] for r, zeile in enumerate(mittel)]
    fig = go.Figure(go.Heatmap(z=mittel, x=list(C.VERFAHREN[bereich]), y=zeilennamen, text=text, texttemplate="%{text}", colorscale="YlOrRd", hovertemplate="%{y}, %{x}: %{z:.2f}<extra></extra>",
                               colorbar=dict(title="über Schranke")))
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=max(260, 26 * len(zeilennamen) + 90), margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_regret(bereich, regret, beste):
    """Gruppierte Balken je Verfahren: mittlerer Regret gegen das instanzweise Beste (links) und Anteil der Instanzen, in denen das Verfahren zu den besten gehört (rechts, in Prozent)."""
    namen = list(C.VERFAHREN[bereich])
    fig = go.Figure()
    fig.add_trace(go.Bar(name="mittlerer Regret (Behälter)", x=namen, y=list(regret), marker_color=C.COLOR_LINE, hovertemplate="%{x}: %{y:.2f}<extra>Regret</extra>"))
    fig.add_trace(go.Bar(name="Anteil bester Instanzen (%)", x=namen, y=list(beste), marker_color="#2F6B65", yaxis="y2", hovertemplate="%{x}: %{y:.0f} %<extra>beste</extra>"))
    fig.update_layout(barmode="group", height=320, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)",
                      yaxis=dict(title_text="Regret (Behälter)", rangemode="tozero"), yaxis2=dict(overlaying="y", side="right", title_text="beste Instanzen (%)", range=[0, 105], showgrid=False))
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig
