
import pandas as pd
import dash
from dash import dcc, html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv"
)

warning_app = DjangoDash("WarningApp")

warning_app.layout = dmc.MantineProvider(
    [
        dmc.Container(
            [
                html.Div(id="input_void"),
                dmc.Alert(
                    title="Warning!",
                    color="yellow",
                    id="warning_msg",
                    style={"margin": "10px"},
                ),
            ]
        )
    ]
)


@warning_app.expanded_callback(
    dash.dependencies.Output("warning_msg", "children"),
    [dash.dependencies.Input("input_void", "value")],
)
def callback_warning(*args, **kwargs):
    message = kwargs["session_state"]["context"]["message"]
    return [message]


app = DjangoDash("SimpleExample")

app.layout = html.Div(
    [
        html.Div(id="blank-output"),
        dcc.Tabs(
            id="tabs-example",
            value="tab-1",
            children=[
                dcc.Tab(label="Tab one", value="tab-1"),
                dcc.Tab(label="Tab two", value="tab-2"),
            ],
        ),
    ]
)

app.clientside_callback(
    """
    function(tab_value) {
        if (tab_value === 'tab-1') {
            document.title = 'Tab 1'
        } else if (tab_value === 'tab-2') {
            document.title = 'Tab 2'
        }
    }
    """,
    dash.dependencies.Output("blank-output", "children"),
    [dash.dependencies.Input("tabs-example", "value")],
)
