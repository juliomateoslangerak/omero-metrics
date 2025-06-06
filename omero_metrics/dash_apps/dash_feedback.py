import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
import omero_metrics.dash_apps.dash_utils.omero_metrics_components as my_components


warning_app = DjangoDash("WarningApp")

warning_app.layout = dmc.MantineProvider(
    [
        my_components.header_component(
            "Omero Metrics Warnings",
            "This is a warning message",
            "Feedback",
            load_buttons=False,
        ),
        dmc.Container(
            [
                html.Div(id="input_void"),
                dmc.Alert(
                    title="Error!",
                    color="red",
                    icon=my_components.get_icon(icon="mdi:alert-circle"),
                    id="warning_msg",
                    style={"margin": "10px"},
                ),
            ]
        ),
    ]
)


@warning_app.expanded_callback(
    dash.dependencies.Output("warning_msg", "children"),
    [dash.dependencies.Input("input_void", "value")],
)
def callback_warning(*args, **kwargs):
    message = kwargs["session_state"]["context"]["message"]
    return [message]
