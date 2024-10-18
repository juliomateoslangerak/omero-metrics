import dash
from dash import dcc, html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc

dashboard_name = "omero_group_dash"
dash_app_group = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)

dash_app_group.layout = dmc.MantineProvider(
    [
        dmc.Container(
            [
                dmc.Card(
                    children=[
                        dmc.Group(
                            [
                                html.Img(
                                    src="./assets/images/microscope.png",
                                    style={"width": "100px"},
                                ),
                                dmc.Title(
                                    "Microscope Health Dashboard",
                                    c="#189A35",
                                    size="h3",
                                    mb=10,
                                    mt=5,
                                ),
                            ],
                            justify="space-between",
                            align="center",
                            mt="md",
                            mb="xs",
                        ),
                        dmc.Divider(mb="sm"),
                        html.Div(id="microscope_info"),
                    ],
                    withBorder=True,
                    shadow="sm",
                    radius="md",
                    style={
                        "width": "100%",
                        "maxWidth": "600px",
                        "margin": "auto",
                    },
                ),
                html.Div(id="blank-input"),
            ],
            style={"padding": "20px"},
        )
    ]
)


@dash_app_group.expanded_callback(
    dash.dependencies.Output("microscope_info", "children"),
    dash.dependencies.Input("blank-input", "children"),
)
def render_content(*args, **kwargs):
    group_name = kwargs["session_state"]["context"]["group_name"]
    group_id = kwargs["session_state"]["context"]["group_id"]
    group_description = kwargs["session_state"]["context"]["group_description"]
    result = dmc.Stack(
        [
            dmc.Text("Microscope Information", c="#189A35", size="xl"),
            dmc.Text(f"Group Name: {group_name}", size="xs"),
            dmc.Text(f"Group ID: {group_id}", size="xs"),
            dmc.Text(f"Group Description: {group_description}", size="xs"),
        ],
        align="flex-start",
        gap="xs",
    )
    return result
