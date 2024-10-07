import dash
from dash import dcc, html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc


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
