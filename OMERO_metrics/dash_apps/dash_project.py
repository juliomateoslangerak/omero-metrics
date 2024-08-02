import dash
from dash import dcc, html, dash_table
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from dash_iconify import DashIconify
from datetime import date
import json
from datetime import datetime, date, timedelta

primary_color = "#008080"

external_scripts = [

    # add the tailwind cdn url hosting the files with the utility classes
    {'src': 'https://cdn.tailwindcss.com'}

]
stylesheets = [
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css", "./assets/omero_metrics.css",

]
dashboard_name = "omero_project_dash"
dash_app_project = DjangoDash(
    name=dashboard_name, serve_locally=True, external_stylesheets=stylesheets,
    external_scripts=external_scripts,
)

dash_app_project.layout = dmc.MantineProvider(
    [
        dmc.Container(
            [dmc.Center(
                [
                    dmc.Text(
                        id="title",
                        c=primary_color,
                        style={"fontSize": 30},
                    ),
                    dmc.Group(
                        [
                            html.Img(
                                src="./assets/images/logo.png",
                                style={"width": "100px"},
                            ),
                            dmc.Text(
                                "OMERO Metrics Dashboard",
                                c=primary_color,
                                style={"fontSize": 15},
                            ),
                        ]
                    ),
                ]
            ),
                dmc.Divider(variant="solid", style={"marginBottom": 20}),
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Text("Select Measurement", style={"fontSize": 14},
                                         ),
                                dcc.Dropdown(id="project-dropdown",
                                             value="0", clearable=False,
                                             style={"width": "250px"})
                            ],
                            span="auto",
                            style={"margin-right": "10px"},
                        ),
                        dmc.GridCol(
                            [
                                dmc.DatePicker(
                                    id="date-picker",
                                    label="Select Date",
                                    value=datetime.now().date(),
                                    leftSection=DashIconify(icon="clarity:date-line"),
                                    w="250"
                                ),
                            ],
                            span="auto",
                        ),
                    ],
                    justify="center",
                    align='center',
                    style={"marginBottom": "20px"},
                ),
                html.Div(
                    id="graph-project",
                    style={"background-color": "white"},
                ),

                html.Div(id="blank-input"),
                html.Div(id="blank-output"),
                html.Div(id='clickdata'),
                html.Div(id='dates_test')
            ],
            fluid=True,
            style={
                "background-color": "#eceff1",
                "margin": "20px",
                "border-radius": "0.5rem",
                "padding": "10px",
            },
        ),

    ]
)

@dash_app_project.expanded_callback(
    dash.dependencies.Output("project-dropdown", "options"),
    dash.dependencies.Output("date-picker", "minDate"),
    dash.dependencies.Output("date-picker", "maxDate"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_dropdown(*args, **kwargs):
    kkm = kwargs["session_state"]["context"]["kkm"]
    kkm = [k.replace('_', ' ').title() for k in kkm]
    dates = kwargs["session_state"]["context"]["dates"]
    options = [{"label": f"{k}", "value": f"{i}"} for i, k in enumerate(kkm)]
    min_date = min(dates)
    max_date = max(dates)
    return options, min_date, max_date


@dash_app_project.expanded_callback(
    dash.dependencies.Output("graph-project", "children"),
    [dash.dependencies.Input("project-dropdown", "value")],
)
def update_table(*args, **kwargs):
    df_list = kwargs["session_state"]["context"]["key_measurements_list"]
    kkm = kwargs["session_state"]["context"]["kkm"]
    measurement = int(args[0])
    dates = kwargs["session_state"]["context"]["dates"]
    kkm = [k.replace('_', ' ').title() for k in kkm]
    data = [
        {"Date": dates[i], "Name": f"Dataset {i}"}
        | df[kkm]
        .copy()
        .mean()
        .reset_index(name="Mean")
        .rename(columns={"index": "Measurement"})
        .pivot_table(columns="Measurement")
        .to_dict("records")[0]
        for i, df in enumerate(df_list)
    ]
    line = dmc.LineChart(
        id='line-chart',
        h=300,
        dataKey="Date",
        data=data,
        withLegend=True,
        legendProps={"horizontalAlign": "top", "height": 50},
        series=[{"name": k, "color": "indigo.6"} for k in kkm],
        curveType="natural",
    )

    return line


@dash_app_project.expanded_callback(
    dash.dependencies.Output("clickdata", "children"),
    [dash.dependencies.Input("line-chart", "clickData")],
    prevent_initial_call=True, )
def update_project_view(*args, **kwargs):
    if args[0]:
        table = kwargs["session_state"]["context"]["key_measurements_list"]
        dates = kwargs["session_state"]["context"]["dates"]
        kkm = kwargs["session_state"]["context"]["kkm"]
        kkm = kkm.insert(0, "channel_name")
        selected_dataset = int(args[0]['Name'].split(' ')[-1])
        df_selected = table[selected_dataset]
        table_kkm = df_selected[kkm].copy()
        table_kkm = table_kkm.round(3)
        table_kkm.columns = table_kkm.columns.str.replace("_", " ").str.title()
        date = dates[selected_dataset]

        grid = dmc.Stack([dmc.Center([dmc.Text(["Key Measurements for Dataset processed at" + str(selected_dataset),
                                               "Date: " + str(date)],
                                               size="md",
                                               c="#2A65B1",
                                               style={"margin-bottom": "20px", 'margin-top': '20px'})
                                      ]),
                          dmc.Table(
                              striped=True,
                              data={
                                  "head": table_kkm.columns.tolist(),
                                  "body": table_kkm.values.tolist(),
                                  "caption": "Key Measurements for the selected dataset"},
                              highlightOnHover=True,
                          )])
        return [grid]
    else:
        return dash.no_update
