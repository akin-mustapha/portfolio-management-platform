"""
tv_dropdown — themed dcc.Dropdown atom.
Adds the tv-dropdown class to every instance so global dropdown CSS applies.
"""
from dash import dcc


def tv_dropdown(
    id,
    options=None,
    value=None,
    placeholder="",
    multi=False,
    clearable=True,
    className="",
    style=None,
    **kwargs,
):
    extra = f" {className}" if className else ""
    return dcc.Dropdown(
        id=id,
        options=options or [],
        value=value,
        placeholder=placeholder,
        multi=multi,
        clearable=clearable,
        className=f"tv-dropdown{extra}",
        style=style,
        **kwargs,
    )
