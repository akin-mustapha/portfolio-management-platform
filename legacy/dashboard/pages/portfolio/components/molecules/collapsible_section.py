"""Molecule — collapsible section container used across portfolio tabs."""

import dash_bootstrap_components as dbc
from dash import html


def collapsible_section(
    section_id: str,
    title: str,
    children,
    is_open: bool = True,
    subheader=None,
) -> html.Div:
    """
    A titled, collapsible section container.

    Produces stable IDs from `section_id`:
      header:   {section_id}-section-header
      collapse: {section_id}-charts-collapse

    Parameters
    ----------
    section_id : str
        Base ID string — must be unique across the page.
    title : str
        Label shown in the clickable header row.
    children : list | dash component
        Content rendered inside the collapse body.
    is_open : bool
        Initial open/closed state (default True).
    subheader : dash component | None
        Optional content placed between the header and the collapse
        (e.g. a secondary KPI row).
    """
    inner = [
        html.Div(
            [title, html.Span("›", className="tv-chevron")],
            id=f"{section_id}-section-header",
            className="tv-section-header tv-section-header--section",
            n_clicks=0,
            style={"cursor": "pointer"},
        ),
    ]
    if subheader is not None:
        inner.append(subheader)
    inner.append(
        dbc.Collapse(
            id=f"{section_id}-charts-collapse",
            is_open=is_open,
            children=children,
        )
    )
    return html.Div(inner, className="tv-section-container")
