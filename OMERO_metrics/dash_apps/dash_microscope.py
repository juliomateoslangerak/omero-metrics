from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
import pandas as pd
from dash import html, dash_table


df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
)


dashboard_name = "top_iu_microscope"
dash_app_microscope = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=dmc.styles.ALL,
)

dash_app_microscope.layout = dmc.MantineProvider(
    [
        dmc.Container(
            [
                dmc.Stack(
                    [
                        dmc.Title(
                            "Microscope Dashboard",
                            size="h3",
                            c="#63aa47",
                            style={
                                "margin-top": "20px",
                                "text-align": "center",
                            },
                        ),
                        html.Hr(),
                        dmc.Flex(
                            direction={"base": "column", "sm": "row"},
                            gap={"base": "sm", "sm": "lg"},
                            justify={"sm": "flex-start"},
                            align={"sm": "center"},
                            style={
                                "margin-top": "20px",
                                "margin-bottom": "10px",
                            },
                        ),
                        dmc.Grid(
                            [
                                dmc.GridCol(
                                    [
                                        html.Div(
                                            [
                                                dmc.Slider(
                                                    id="drag-slider",
                                                    value=26,
                                                    updatemode="drag",
                                                    marks=[
                                                        {
                                                            "value": 20,
                                                            "label": "20%",
                                                        },
                                                        {
                                                            "value": 50,
                                                            "label": "50%",
                                                        },
                                                        {
                                                            "value": 80,
                                                            "label": "80%",
                                                        },
                                                    ],
                                                    mb=25,
                                                ),
                                            ],
                                            style={
                                                "background-color": "#3c652a",
                                                "padding": "10px",
                                                "border-radius": "0.5rem",
                                                "margin-bottom": "10px",
                                                "align": "center",
                                            },
                                        ),
                                        dmc.BarChart(
                                            h=300,
                                            dataKey="continent",
                                            data=df.to_dict(orient="records"),
                                            series=[
                                                {
                                                    "name": "pop",
                                                    "color": "violet.6",
                                                },
                                                {
                                                    "name": "lifeExp",
                                                    "color": "blue.6",
                                                },
                                                {
                                                    "name": "gdpPercap",
                                                    "color": "teal.6",
                                                },
                                            ],
                                            tickLine="y",
                                            gridAxis="y",
                                            withXAxis=True,
                                            withYAxis=True,
                                        ),
                                    ],
                                    span="auto",
                                ),
                                dmc.GridCol(
                                    [
                                        dash_table.DataTable(
                                            data=df.to_dict("records"),
                                            page_size=10,
                                        )
                                    ],
                                    span="auto",
                                ),
                            ],
                            justify="space-between",
                            align="stretch",
                        ),
                    ]
                )
            ],
            style={"background-color": "#e0e0e0"},
            fluid=True,
        ),
    ]
)
