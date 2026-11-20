import plotly.graph_objects as go
import plotly.io as pio

def make_template(
    *, background, foreground, grid, colors,
    font="Arial, sans-serif", axis_lines=False,
):
    template = go.layout.Template(pio.templates["plotly_white"])
    template.layout.update(
        paper_bgcolor=background,
        plot_bgcolor=background,
        font=dict(family=font, size=14, color=foreground),
        title=dict(x=0.04, xanchor="left", font=dict(size=22)),
        colorway=colors,
        margin=dict(l=65, r=30, t=75, b=60),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=axis_lines,
            linecolor=foreground,
            automargin=True,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=grid,
            zeroline=False,
            showline=axis_lines,
            linecolor=foreground,
            automargin=True,
        ),
        hoverlabel=dict(bgcolor=background, font=dict(color=foreground)),
    )
    return template

PASTELL = make_template(
    background="#FFF9F3",
    foreground="#332C38",
    grid="#EADFD9",
    colors=["#547CB5", "#B65C78", "#468579", "#8A6AAE"],
)