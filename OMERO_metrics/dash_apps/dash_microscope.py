from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
import pandas as pd
from dash import html, dash_table

stylesheets = [
    "https://unpkg.com/@mantine/charts@7/styles.css",
]

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
)
data = [
    {"month": "January", "Smartphones": 1200, "Laptops": 900, "Tablets": 200},
    {
        "month": "February",
        "Smartphones": 1900,
        "Laptops": 1200,
        "Tablets": 400,
    },
    {"month": "March", "Smartphones": 400, "Laptops": 1000, "Tablets": 200},
    {"month": "April", "Smartphones": 1000, "Laptops": 200, "Tablets": 800},
    {"month": "May", "Smartphones": 800, "Laptops": 1400, "Tablets": 1200},
    {"month": "June", "Smartphones": 750, "Laptops": 600, "Tablets": 1000},
]
content = dmc.Card(
    children=[
        dmc.Group(
            [
                dmc.Text("Norway Fjord Adventures", fw=500),
            ],
            justify="space-between",
            mt="md",
            mb="xs",
        ),
        dmc.Text(
            "With Fjord Tours you can explore more of the magical fjord landscapes with tours and activities on and "
            "around the fjords of Norway",
            size="sm",
            c="dimmed",
        ),
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
    w="auto",
)

dashboard_name = "Microscope"
dash_app_microscope = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=stylesheets,
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
                            children=[content, content, content],
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
