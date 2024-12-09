import dash
from dash import html
from dash_iconify import DashIconify
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
import OMERO_metrics.dash_apps.dash_utils.omero_metrics_components as my_components


warning_app = DjangoDash("WarningApp")

warning_app.layout = dmc.MantineProvider(
    [   my_components.header_component("Omero Metrics Warnings", "This is a warning message", "Feedback", load_buttons=False),
        dmc.Container(
            [
                html.Div(id="input_void"),
                dmc.Alert(
                    title="Error!",
                    color="red",
                    icon=DashIconify(icon="mdi:alert-circle", height=20),
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
