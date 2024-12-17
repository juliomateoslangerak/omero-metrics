import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
import OMERO_metrics.dash_apps.dash_utils.omero_metrics_components as my_components
from OMERO_metrics.styles import CARD_STYLE1

omero_multiple_projects = DjangoDash(
    "omero_multiple_projects",
    serve_locally=True,
    external_stylesheets=dmc.styles.ALL,
)

omero_multiple_projects.layout = dmc.MantineProvider(
    [
        my_components.header_component(
            "Omero Metrics Projects",
            "This is a view for multiple projects",
            "Feedback",
            load_buttons=False,
        ),
        dmc.Container(
            children=[
                html.Div(id="input_void"),
                html.Div(id="chart_lines"),
            ]
        ),
    ]
)


@omero_multiple_projects.expanded_callback(
    dash.dependencies.Output("chart_lines", "children"),
    [dash.dependencies.Input("input_void", "value")],
)
def tables(*args, **kwargs):
    if kwargs["session_state"]["context"]:
        data = kwargs["session_state"]["context"]
        print(data)
        print(kwargs["session_state"]["context"])
        div_data = []
        for project_id in data:
            if data[project_id]:
                title, line = my_components.get_title_line_chart(
                    project_id, data[project_id]
                )
                div_data.append(dmc.Stack([dmc.Title(title), line]))
            else:
                div_data.append(
                    dmc.Stack(
                        [
                            dmc.Text(f"Project ID: {project_id}"),
                            dmc.Text(
                                f"No data available, please analyse project ID= {project_id}",
                                c="dimmed",
                                fw="bold",
                            ),
                        ]
                    )
                )
        return dmc.Paper(
            style={**CARD_STYLE1, "marginTop": "12px"}, children=div_data
        )
    else:
        return [
            dmc.Text(
                "No data available, please analyse at least one project",
                c="dimmed",
                fw="bold",
            )
        ]
