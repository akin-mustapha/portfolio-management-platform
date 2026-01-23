import plotly.express as px

def asset_chart(df,
    x='name',
    y='profit'):
  fig = px.histogram(df, x=x, y=y, histfunc='avg', )
  fig.update_layout(
      template="plotly_dark",
      hovermode="x unified",
      margin=dict(l=20, r=20, t=40, b=20),
      title=None,
  )
  # fig.update_traces(
  #     line=dict(width=3),
  #     # mode="lines",
  # )
  # fig.update_xaxes(showgrid=False)
  # fig.update_yaxes(showgrid=False)
  return fig

# def asset_chart(df,
#     x='name',
#     y='profit'):
#   fig = px.histogram(df, x=x, y=y, histfunc='avg', )
#   fig.update_layout(
#       template="plotly_dark",
#       hovermode="x unified",
#       margin=dict(l=20, r=20, t=40, b=20),
#       title=None,
#   )
#   # fig.update_traces(
#   #     line=dict(width=3),
#   #     # mode="lines",
#   # )
#   # fig.update_xaxes(showgrid=False)
#   # fig.update_yaxes(showgrid=False)
#   return fig