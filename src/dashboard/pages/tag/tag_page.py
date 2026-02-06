from dash import dcc, html, callback, Input, Output, State, dash
import dash_bootstrap_components as dbc
from src.dashboard.components.cards import card
from src.services.portfolio.tagging_service_builder import build_portfolio_service
from src.dashboard.services.asset_service import AssetService
from src.dashboard.services.local_asset_service import LocalAssetService
from src.dashboard.styles.style import TAB_CONTENT_STYLE
from src.dashboard.components.tables.table import create_table
from src.dashboard.components.select import create_select
import pandas as pd

def create_table_from_df(df, table_name: str):
  return create_table(table_name, df.columns, df.to_dict("records"))

create_dropdown_item_from_list = lambda ls: html.Div([dbc.DropdownMenuItem(item, className="sm") for item in ls])


portfolio_serivce = build_portfolio_service()
asset_service = AssetService
tag_df = pd.DataFrame(LocalAssetService.get_all_tag())
asset_df = pd.DataFrame(LocalAssetService.get_all_asset())
tags_df = pd.DataFrame(portfolio_serivce.get_all_tags())

tags_table = lambda df: html.Div([
  card("tag", create_table_from_df(df, "tag-table"))
])
# @callback(
#     Output("tag-create-status", "value"),
#     Output("tag-table", "data"),
#     Input("btn-create-tag-name", "n_clicks"),
#     State("input-tag-name", "value"),
#     prevent_initial_call=True
# )
# def create_new_tag(n_clicks, value):
#     if not value:
#         return "⚠️ Tag name cannot be empty"
#     portfolio_serivce.create_tag(value)

#     tag_df = pd.DataFrame(asset_service.get_all_tag())
#     return (
#         f"✅ Tag '{value}' created",
#         tag_df.to_dict("records")
#     )
@callback(
    Output("tag-item-status", "children"),
    Output("tag-item-table", "data"),
    Input("btn-assign-tag", "n_clicks"),
    State("asset-select", "value"),
    State("tag-select", "value"),
    prevent_initial_call=True,
)
def assign_tag_to_item(n_clicks, asset_id, tag_id):
    if not asset_id or not tag_id:
      return "Please select both an asset and a tag", dash.no_update

    payload = {
      "item_id": asset_id,
      "tag_id": tag_id,
    }

    portfolio_serivce.tag_item(payload)

    # re-fetch fresh truth from the source of truth
    updated_tags = pd.DataFrame(portfolio_serivce.get_all_tags())

    return (
      f"✅ Tag {tag_id} assigned to asset {asset_id}",
      updated_tags.to_dict("records"),
    )

def create_tag_card():
    return card(
      "Create Tag",
      dbc.Stack(
        [
          dbc.Input(id="input-tag-name", placeholder="Tag name"),
          dbc.Select(
              id="tag-type-select",
              options=[
                  {"label": t, "value": t}
                  for t in ["Region", "Country", "Sector", "Industry"]
              ],
          ),
          dbc.Button("Create Tag", id="btn-create-tag-name", color="primary"),
          html.Div(id="tag-create-status")
        ],
        gap=2
      )
    )
def view_tag_card(df):
    return card(
        "View Tag",
        dbc.Stack(
            [
              card("Tags", create_table_from_df(df, "tag-table"))
            ],
            gap=2
        )
    )
def view_tag_item_card(df):
    return card(
        "View Tag",
        dbc.Stack(
            [
              card("Asset Item", create_table_from_df(df, "tag-item-table"))
            ],
            gap=2
        )
    )
def assign_tag_card(asset_df, tags_df):
    return card(
        "Assign Tag",
        dbc.Stack(
            [
                create_select(asset_df, select_id="asset-select"),
                create_select(
                    tags_df,
                    select_id="tag-select",
                    label="tag_name",
                    value="tag_id",
                ),
                dbc.Button(
                    "Assign Tag",
                    id="btn-assign-tag",
                    color="primary",
                ),
                html.Div(id="tag-item-status"),
            ],
            gap=2,
        ),
    )

def tag_layout():
  return html.Div(
    [
       
      dcc.Location(id="tag_page_location"),
      dbc.Row(
        [
          dbc.Col(
                dbc.Row(
                [
                  dbc.Col(assign_tag_card(asset_df, tag_df), md="auto"),
                  dbc.Col(create_tag_card(), md="auto"),
                ],
              className="mt-4"
            ),
          md=4),
          dbc.Col(view_tag_card(tag_df), md="8"),
          ],
          className="mt-4"
      ),
      dbc.Row(
        [
          dbc.Col(view_tag_item_card(tags_df), md="max"),
        ],
        className="mt-4"
      )
    ]
  )
