import uuid
import random
from datetime import datetime
import pandas as pd
from django.core.cache import cache
from django.utils.translation import gettext, gettext_lazy
import dash
from dash import Dash, dcc, html, Input, Output, callback,dash_table
from dash.dependencies import MATCH, ALL
import plotly.graph_objs as go
import dpd_components as dpd
from dash.exceptions import PreventUpdate
from django_plotly_dash import DjangoDash
from django_plotly_dash.consumers import send_to_pipe_channel
import plotly.express as px
import dash_mantine_components as dmc


c1 = "#d8f3dc"
c2 = "#eceff1"
c3 = "#189A35"


df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

app = DjangoDash('FOI_Demo')

app.layout = dmc.Container([
      dmc.Center(
            dmc.Text(
                "Field Of Illumination Dashboard",
                color="#189A35",
                mb=30,
                style={"margin-top": "20px", "fontSize": 40},
            )
        ),
     
               dmc.Grid(
            [
                dmc.Col(
                    dmc.Stack(
                        [
                            dmc.Text("Microscope", size="sm", weight=700),
                            dcc.Dropdown(["Microscope L", "Microscope B", "Microscope G"]),
                            dmc.Text("Type of Analysis", size="sm", weight=700),
                            dcc.Dropdown(["Field Of Illumination"]),
                            dmc.Text("Analysis", size="sm", weight=700),
                            dcc.Dropdown(["L", "B", "G"]),
                        ]
                    ),
                    span=2,
                    style={
                        "background-color": c2,
                        "margin-right": "10px",
                        "border-radius": "0.5rem",
                    },
                ),
                dmc.Col(
                    [
                        dmc.Stack(
                            [
                                dmc.Grid(
                                    [
                                        dmc.Col(
                                            [
                                                html.H3("Select Category"),
                                                dcc.Dropdown(
                                                    ['ch1', 'ch2', 'ch3'], value="ch3", id="key_dpd"
                                                ),
                                            ],
                                            span="auto",
                                            style={"background-color": c2, "margin-right": "10px"},
                                        ),
                                        dmc.Col(
                                            [
                                                html.H3("Select Date"),
                                                dcc.DatePickerRange(
                                                    id="date_filter",
                                                    start_date_placeholder_text="Start Period",
                                                    end_date_placeholder_text="End Period",
                                                ),
                                            ],
                                            span="auto",
                                        ),
                                    ],
                                ),
                                dmc.Title(
                                    "Key Measurments for FOI", color="#189A35", size="h3", mb=10
                                ),
                                dash_table.DataTable(
                                    id="table",
                                    data=df.to_dict("records"),
                                    page_size=10,
                                    sort_action="native",
                                    sort_mode="multi",
                                    sort_as_null=["", "No"],
                                    sort_by=[{"column_id": "pop", "direction": "asc"}],
                                    editable=False,
                                    style_cell={
                                        "textAlign": "left",
                                        "fontSize": 10,
                                        "font-family": "sans-serif",
                                    },
                                    style_header={
                                        "backgroundColor": "#189A35",
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
                dmc.Col(
                    [
                        dmc.Title("Plot Over Time", color="#189A35", size="h3", mb=10),
                        dcc.Graph(id="graph_line", figure={}),
                    ],
                    span="auto",
                    style={"background-color": "#eceff1", "border-radius": "5px"},
                ),
            ],
            justify="space-between",
            align="stretch",
            gutter="xl",
            style={
                "margin-top": "20px",
            },
        ),
      
      
])