import dash
from dash import dcc, html, dash_table
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px

primary_color = "#008080"

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
)
stylesheets = [
    "https://unpkg.com/@mantine/charts@7/styles.css",
]
dashboard_name = "omero_project_dash"
dash_app_project = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=stylesheets
)

dash_app_project.layout = dmc.MantineProvider(
    [
        dmc.Container(
            [
                html.Div(id="blank-input"),
                html.Div(id="blank-output"),
                dcc.Dropdown(id="project-dropdown", value="0"),
                dcc.Graph(
                    id="graph-project",
                ),
            ]
        )
    ]
)


@dash_app_project.expanded_callback(
    dash.dependencies.Output("blank-output", "children"),
    dash.dependencies.Output("graph-project", "figure"),
    dash.dependencies.Output("project-dropdown", "options"),
    [dash.dependencies.Input("project-dropdown", "value")],
)
def update_table(*args, **kwargs):
    df_list = kwargs["session_state"]["context"]["key_measurements_list"]
    kkm = kwargs["session_state"]["context"]["kkm"]
    measurement = int(args[0])
    dates = kwargs["session_state"]["context"]["dates"]
    grid = dmc.SimpleGrid(
        cols=len(df_list),
        children=[
            dmc.Card(
                children=[
                    dmc.Text("Key Measurements", size="h3"),
                    dash_table.DataTable(
                        id="table",
                        data=df.to_dict("records"),
                        page_size=10,
                        sort_action="native",
                        sort_mode="multi",
                        sort_as_null=["", "No"],
                        editable=False,
                        style_cell={
                            "textAlign": "left",
                            "fontSize": 14,
                            "font-family": "sans-serif",
                        },
                        style_header={
                            "backgroundColor": primary_color,
                            "fontWeight": "bold",
                            "fontSize": 18,
                            "textAlign": "center",
                        },
                        style_table={
                            "overflowX": "auto",
                            "border-radius": "0.5rem",
                        },
                    ),
                ]
            )
            for df in df_list
        ],
    )
    options = [
        {"label": f"Measurement {k}", "value": f"{i}"}
        for i, k in enumerate(kkm)
    ]
    data = [{"Date": dates[i], "Name": f"Dataset {i}"} | df[[kkm]].copy().mean() for i, df in enumerate(df_list)]
    line = dmc.LineChart(
        h=300,
        dataKey="Date",
        data=data,

        withLegend=True,
        legendProps={'verticalAlign': 'bottom', 'height': 50},
        series=[
            {"name": k, 'color': 'indigo.6'} for k in kkm
        ],
    )

    return [grid], line, options
