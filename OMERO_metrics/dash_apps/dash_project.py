import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
import pandas as pd
from dash_iconify import DashIconify
from datetime import datetime

primary_color = "#008080"

external_scripts = [
    # add the tailwind cdn url hosting the files with the utility classes
    {"src": "https://cdn.tailwindcss.com"}
]
stylesheets = [
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css",
    "./assets/omero_metrics.css",
]
dashboard_name = "omero_project_dash"
dash_app_project = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=stylesheets,
    external_scripts=external_scripts,
)

dash_app_project.layout = dmc.MantineProvider(
    [
        dmc.Container(
            [
                dmc.Center(
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
                                dmc.Select(
                                    id="project-dropdown",
                                    label="Select Measurement",
                                    w="300",
                                    value="0",
                                    clearable=False,
                                    leftSection=DashIconify(
                                        icon="radix-icons:magnifying-glass"
                                    ),
                                    rightSection=DashIconify(
                                        icon="radix-icons:chevron-down"
                                    ),
                                )
                            ],
                            span="content",
                        ),
                        dmc.GridCol(
                            [
                                dmc.DatePicker(
                                    id="date-picker",
                                    label="Select Date",
                                    leftSection=DashIconify(
                                        icon="clarity:date-line"
                                    ),
                                    type="range",
                                    w="300",
                                ),
                            ],
                            span="content",
                        ),
                    ],
                    justify="space-between",
                    style={"marginBottom": "20px"},
                ),
                html.Div(
                    id="graph-project",
                    style={"background-color": "white"},
                ),
                html.Div(id="blank-input"),
                html.Div(id="blank-output"),
                html.Div(id="clickdata"),
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
    dash.dependencies.Output("project-dropdown", "data"),
    dash.dependencies.Output("date-picker", "minDate"),
    dash.dependencies.Output("date-picker", "maxDate"),
    dash.dependencies.Output("date-picker", "value"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_dropdown(*args, **kwargs):
    kkm = kwargs["session_state"]["context"]["kkm"]
    kkm = [k.replace("_", " ").title() for k in kkm]
    dates = kwargs["session_state"]["context"]["dates"]
    options = [{"value": f"{i}", "label": f"{k}"} for i, k in enumerate(kkm)]
    min_date = min(dates)
    max_date = max(dates)
    data = options
    value_date = [min_date, max_date]
    return data, min_date, max_date, value_date


@dash_app_project.expanded_callback(
    dash.dependencies.Output("graph-project", "children"),
    [
        dash.dependencies.Input("project-dropdown", "value"),
        dash.dependencies.Input("date-picker", "value"),
    ],
)
def update_table(*args, **kwargs):
    df_list = kwargs["session_state"]["context"]["key_measurements_list"]
    kkm = kwargs["session_state"]["context"]["kkm"]
    measurement = int(args[0])
    dates_range = args[1]
    dates = kwargs["session_state"]["context"]["dates"]
    df_filtering = pd.DataFrame(dates, columns=["Date"])
    df_dates = df_filtering[
        (
            df_filtering["Date"]
            >= datetime.strptime(dates_range[0], "%Y-%m-%d").date()
        )
        & (
            df_filtering["Date"]
            <= datetime.strptime(dates_range[1], "%Y-%m-%d").date()
        )
    ].index.to_list()
    # kkm = [k.replace("_", " ").title() for k in kkm]
    df_list_filtered = [df_list[i] for i in df_dates]
    data = [
        {"Date": dates[i], "Name": f"Dataset {i}"}
        | df[[kkm[measurement]]]
        .copy()
        .mean()
        .reset_index(name="Mean")
        .rename(columns={"index": "Measurement"})
        .pivot_table(columns="Measurement")
        .to_dict("records")[0]
        for i, df in enumerate(df_list_filtered)
    ]
    line = dmc.LineChart(
        id="line-chart",
        h=300,
        dataKey="Date",
        data=data,
        withLegend=True,
        legendProps={"horizontalAlign": "top", "height": 50},
        series=[{"name": kkm[measurement], "color": "green.7"}],
        curveType="natural",
        style={"padding": 20},
        xAxisLabel="Processed Date",
        # yAxisLabel=str(kkm[measurement]).replace("_", " ").title(),
    )

    return line


@dash_app_project.expanded_callback(
    dash.dependencies.Output("clickdata", "children"),
    [dash.dependencies.Input("line-chart", "clickData")],
    prevent_initial_call=True,
)
def update_project_view(*args, **kwargs):
    if args[0]:
        table = kwargs["session_state"]["context"]["key_measurements_list"]
        dates = kwargs["session_state"]["context"]["dates"]
        kkm = kwargs["session_state"]["context"]["kkm"]
        selected_dataset = int(args[0]["Name"].split(" ")[-1])
        df_selected = table[selected_dataset]
        table_kkm = df_selected[kkm].copy()
        table_kkm = table_kkm.round(3)
        table_kkm.columns = table_kkm.columns.str.replace("_", " ").str.title()
        date = dates[selected_dataset]
        grid = dmc.Stack(
            [
                dmc.Divider(
                    variant="solid",
                    style={"marginTop": 50, "marginBottom": 20},
                ),
                dmc.Center(
                    [
                        dmc.Text(
                            [
                                "Key Measurements for Dataset Number: "
                                + str(selected_dataset),
                                " processed at Date: " + str(date),
                            ],
                            c="#189A35",
                            size="md",
                        )
                    ]
                ),
                dmc.Table(
                    striped=True,
                    data={
                        "head": table_kkm.columns.tolist(),
                        "body": table_kkm.values.tolist(),
                        "caption": "Key Measurements for the selected dataset",
                    },
                    highlightOnHover=True,
                    style={
                        "background-color": "white",
                    },
                ),
            ]
        )
        return [grid]
    else:
        return dash.no_update
