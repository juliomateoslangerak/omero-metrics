import dash
import dash_mantine_components as dmc
import pandas as pd
from dash import html
from django_plotly_dash import DjangoDash

import omero_metrics.dash_apps.utils.omero_metrics_components as my_components
from omero_metrics.styles import CARD_STYLE1, COLORS_CHANNELS
from omero_metrics.tools.serializers import deserialize

# Initialize the Dash app
dashboard_name = "omero_multiple_projects"
omero_multiple_projects = DjangoDash(
    dashboard_name,
    serve_locally=True,
)

omero_multiple_projects.layout = dmc.MantineProvider(
    [
        my_components.header_component(
            title="Omero Metrics Projects",
            description="This is a view for multiple projects",
            tag="Feedback",
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


def get_title_line_chart(project_id, value):
    title = dmc.Text(f"Project ID: {project_id}")
    context = deserialize(value)
    dates = context["dates"]
    kkm_config = context["assay_config"].kkm_configuration
    dfs = context["key_measurements_list"]
    measurement = next(iter(kkm_config))
    df = get_data_trends(kkm_config, measurement, dates, dfs)
    channels = [c for c in df.columns if c not in ["dataset_index", "date"]]
    series = [
        {
            "name": channel,
            "color": COLORS_CHANNELS[i % len(COLORS_CHANNELS)],
        }
        for i, channel in enumerate(channels)
    ]
    line_chart = dmc.LineChart(
        id=f"line-chart-{project_id}",
        h=300,
        dataKey="date",
        withLegend=True,
        legendProps={
            "horizontalAlign": "top",
            "left": 50,
        },
        data=df.to_dict("records"),
        series=series,
        curveType="linear",
        style={"padding": 20},
        xAxisLabel="Processed Date",
        connectNulls=True,
    )
    return title, line_chart


def get_data_trends(kkm_config, measurement, dates, dfs):
    """Trend of one key measurement, ``measurement`` naming it as ``kkm_config`` keys it."""
    kkm_values = list(kkm_config)
    complete_df = pd.DataFrame()
    for i, df in enumerate(dfs):
        dfi = df.pivot_table(columns="channel_name", values=kkm_values).reset_index(
            names="Measurement"
        )
        dfi["dataset_index"] = i
        dfi["date"] = dates[i]
        complete_df = pd.concat([complete_df, dfi])
    complete_df = complete_df.reset_index(drop=True)
    complete_df = complete_df[complete_df["Measurement"] == measurement]
    complete_df = complete_df.drop(columns="Measurement")
    return complete_df


@omero_multiple_projects.expanded_callback(
    dash.dependencies.Output("chart_lines", "children"),
    [dash.dependencies.Input("input_void", "value")],
)
def kkm_tables_projects(_input_void, *, session_state):
    data = session_state["context"]
    if data:
        print(data)
        div_data = []
        for project_id in data:
            if data[project_id]:
                title, line = get_title_line_chart(project_id, data[project_id])
                div_data.append(dmc.Stack([dmc.Title(title), line]))
            else:
                div_data.append(
                    dmc.Stack(
                        [
                            dmc.Text(f"Project ID: {project_id}"),
                            dmc.Text(
                                children=f"No data available for project ID: {project_id}, please analyse it first.",
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
                children="No data available. Please analyse at least one project",
                c="dimmed",
                fw="bold",
            )
        ]
