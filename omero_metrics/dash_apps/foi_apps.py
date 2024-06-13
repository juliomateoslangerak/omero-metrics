import dash
import dash_mantine_components as dmc

from dash import (
    dash_table,
    html,
)
from django_plotly_dash import (
    DjangoDash,
)

c1 = "#d8f3dc"
c2 = "#eceff1"
c3 = "#63aa47"


app = DjangoDash("FOI_Demo")

app.layout = dmc.MantineProvider(
    children=[
        dmc.Container(
            [
                html.Div(
                    id="blank-input",
                    children=[],
                ),
                dmc.Center(
                    dmc.Text(
                        "Field Of Illumination Dashboard",
                        mb=30,
                        style={
                            "margin-top": "20px",
                            "fontSize": 40,
                        },
                    )
                ),
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title(
                                            "Key Measurments for FOI",
                                            c="#63aa47",
                                            size="h3",
                                            mb=10,
                                        ),
                                        dash_table.DataTable(
                                            id="table",
                                            page_size=10,
                                            sort_action="native",
                                            sort_mode="multi",
                                            sort_as_null=[
                                                "",
                                                "No",
                                            ],
                                            sort_by=[
                                                {
                                                    "column_id": "pop",
                                                    "direction": "asc",
                                                }
                                            ],
                                            editable=False,
                                            style_cell={
                                                "textAlign": "left",
                                                "fontSize": 10,
                                                "font-family": "sans-serif",
                                            },
                                            style_header={
                                                "backgroundColor": "#5f7f53",
                                                "fontWeight": "bold",
                                                "fontSize": 15,
                                            },
                                        ),
                                    ]
                                )
                            ],
                            span="auto",
                            style={
                                "background-color": c2,
                                "margin-right": "10px",
                                "border-radius": "0.5rem",
                            },
                        ),
                    ],
                    justify="space-between",
                    align="stretch",
                    gutter="xl",
                    style={
                        "margin-top": "20px",
                    },
                ),
            ]
        )
    ]
)


@app.expanded_callback(
    dash.dependencies.Output(
        "table", "data"
    ),
    [
        dash.dependencies.Input(
            "blank-input", "children"
        ),
    ],
)
def keyvalue_callback(*args, **kwargs):
    data = kwargs["session_state"][
        "data"
    ]
    return data.to_dict("records")
