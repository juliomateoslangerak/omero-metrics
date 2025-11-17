from datetime import datetime
from typing import Union

import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from dash_iconify import DashIconify
from plotly.subplots import make_subplots

from omero_metrics.styles import (
    BUTTON_STYLE,
    COLORS_CHANNELS,
    HEADER_PAPER_STYLE,
    THEME,
)


def alert_handler(
    response_type,
    response_msg,
    response_details=None,
    with_close_button=None,
    duration=None,
):

    if response_type == "success":
        title = "Success!"
        icon = get_icon(icon="radix-icons:check")
        color = "green"
    elif response_type == "authorisation_error":
        title = "Authorisation Error!"
        icon = get_icon(icon="radix-icons:lock-closed")
        color = "red"
    elif response_type == "analysis_error":
        title = "Analysis Error!"
        icon = get_icon(icon="radix-icons:alert")
        color = "orange"
    elif response_type == "unidentified_error":
        title = "Error!"
        icon = get_icon(icon="radix-icons:alert")
        color = "red"

    children = [dmc.Text(response_msg, size="sm")]
    if response_details:
        children.append(dmc.Code(response_details, block=True))

    return [
        dmc.Alert(
            children=children,
            color=color,
            icon=icon,
            title=title,
            radius="md",
            withCloseButton=with_close_button,
            duration=duration,
        )
    ], False


def notification_handler(response_type, response_msg, opened):
    if response_type == "success":
        title = "Success!"
        icon = get_icon(icon="radix-icons:check")
        color = "green"
    elif response_type == "authorisation_error":
        title = "Authorisation Error!"
        icon = get_icon(icon="radix-icons:lock-closed")
        color = "red"
    elif response_type == "unidentified_error":
        title = "Error!"
        icon = get_icon(icon="radix-icons:alert")
        color = "red"

    notification = dmc.Notification(
        title=title,
        id="simple-notify",
        action="show",
        message=response_msg,
        icon=icon,
        color=color,
    )
    return opened, notification, False


def get_icon(icon, size=20, color=None):
    return DashIconify(icon=icon, height=size, color=color)


def make_control(text, action_id):
    return dmc.Flex(
        [
            dmc.AccordionControl(text),
            dmc.ActionIcon(
                children=get_icon(icon="lets-icons:check-fill"),
                color="green",
                variant="default",
                n_clicks=0,
                id={"index": action_id},
            ),
        ],
        justify="center",
        align="center",
    )


def fig_mip(mip_x, mip_y, mip_z):
    fig = make_subplots(
        rows=3,
        cols=3,
        # shared_xaxes=True,
        # shared_yaxes=True,
        # specs=[[{}, {}, {}], [{}, None]],
        # subplot_titles=("MIP X axis", "MIP Y axis", "MIP Z axis"),
    )

    fig.add_trace(
        go.Heatmap(
            z=mip_x,
            # zmin=mip_x.min(), zmax=mip_x.max(),
        ),
        row=2,
        col=3,
    )
    fig.add_trace(
        go.Heatmap(
            z=mip_y,
            # zmin=mip_y.min(), zmax=mip_y.max(),
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Heatmap(
            z=mip_z,
            # zmin=mip_z.min(), zmax=mip_z.max(),
        ),
        row=2,
        col=2,
    )
    fig.update_layout(
        coloraxis=dict(colorscale="hot"),
        autosize=False,
    )
    for r in range(1, 4):
        for c in range(1, 4):
            fig.update_yaxes(
                scaleanchor=f"x{ (r-1)*3 + c if (r,c)!=(1,1) else '' }",
                scaleratio=1,
                row=r,
                col=c,
            )

    fig.update_layout(
        {
            "xaxis": {
                "visible": False,
                "automargin": False,
                "rangemode": "nonnegative",
            },
            "xaxis2": {
                "visible": False,
                "automargin": False,
                "rangemode": "nonnegative",
            },
            "xaxis3": {
                "visible": False,
                "automargin": False,
                "rangemode": "nonnegative",
            },
            "yaxis": {
                "visible": False,
                "anchor": "x",
                "scaleanchor": "x",
                "autorange": "reversed",
                "automargin": False,
            },
            "yaxis2": {
                "visible": False,
                "anchor": "x2",
                "scaleanchor": "x2",
                "autorange": "reversed",
                "automargin": False,
            },
            "yaxis3": {
                "visible": False,
                "anchor": "x3",
                "scaleanchor": "x3",
                "autorange": "reversed",
                "automargin": False,
            },
        }
    )
    return fig


download_group = dmc.Group(
    [
        dmc.Menu(
            [
                dmc.MenuTarget(
                    dmc.Button(
                        id="activate_download",
                        children="Download",
                        leftSection=DashIconify(
                            icon="material-symbols:download", width=20
                        ),
                        rightSection=DashIconify(
                            icon="carbon:chevron-down", width=20
                        ),
                        color=THEME["primary"],
                        variant="outline",
                    )
                ),
                dmc.MenuDropdown(
                    [
                        dmc.MenuItem(
                            "YAML",
                            id="download-yaml",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-yaml", width=20
                            ),
                        ),
                        dmc.MenuItem(
                            "JSON",
                            id="download-json",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-json", width=20
                            ),
                        ),
                        dmc.MenuItem(
                            "Text",
                            id="download-text",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-text", width=20
                            ),
                        ),
                    ]
                ),
            ],
            trigger="click",
        ),
        dcc.Download(id="download"),
    ]
)


download_table = dmc.Group(
    [
        dmc.Menu(
            [
                dmc.MenuTarget(
                    dmc.ActionIcon(
                        DashIconify(icon="material-symbols:download", width=20),
                        color=THEME["primary"],
                    )
                ),
                dmc.MenuDropdown(
                    [
                        dmc.MenuItem(
                            "CSV",
                            id="table-download-csv",
                            leftSection=DashIconify(icon="iwwa:file-csv", width=20),
                        ),
                        dmc.MenuItem(
                            "Excel",
                            id="table-download-xlsx",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-excel", width=20
                            ),
                        ),
                        dmc.MenuItem(
                            "JSON",
                            id="table-download-json",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-json", width=20
                            ),
                        ),
                    ]
                ),
            ],
            trigger="click",
        ),
        dcc.Download(id="table-download"),
    ]
)


delete_button = dmc.Button(
    id="delete_data",
    children="Delete",
    color="red",
    variant="filled",
    leftSection=DashIconify(icon="ic:round-delete-forever"),
)


def header_component(title, description, tag, load_buttons=True):
    return dmc.Paper(
        children=[
            dmc.Group(
                [
                    dmc.Group(
                        [
                            html.Img(
                                src="/static/omero_metrics/images/metrics_logo.png",
                                style={
                                    "width": "120px",
                                    "height": "auto",
                                },
                            ),
                            dmc.Stack(
                                [
                                    dmc.Title(
                                        title,
                                        c=THEME["primary"],
                                        size="h2",
                                    ),
                                    dmc.Text(
                                        description,
                                        c=THEME["text"]["secondary"],
                                        size="sm",
                                    ),
                                ],
                                gap="xs",
                            ),
                        ],
                    ),
                    dmc.Group(
                        [
                            download_group,
                            delete_button,
                            dmc.Badge(
                                tag,
                                color=THEME["primary"],
                                variant="dot",
                                size="lg",
                            ),
                        ]
                        if load_buttons
                        else dmc.Badge(
                            tag,
                            color=THEME["primary"],
                            variant="dot",
                            size="lg",
                        )
                    ),
                ],
                justify="space-between",
            ),
        ],
        **HEADER_PAPER_STYLE,
    )


def thresholds_paper(Accordion_children):
    return [
        dmc.Accordion(
            id="accordion-compose-controls",
            chevron=DashIconify(icon="ant-design:plus-outlined"),
            disableChevronRotation=True,
            children=Accordion_children,
        ),
        dmc.Group(
            justify="flex-end",
            mt="xl",
            children=[
                dmc.Button(
                    "Update",
                    id="modal-submit-button",
                    style=BUTTON_STYLE,
                ),
            ],
        ),
        html.Div(id="notifications-container"),
    ]


def get_title_line_chart(project_id, value):
    title = dmc.Text(f"Project ID: {project_id}")
    dates = value["dates"]
    kkm = value["kkm"]
    dfs = value["key_measurements_list"]
    measurement = 0
    df = get_data_trends(kkm, measurement, dates, dfs)
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


def get_data_trends(kkm, measurement, dates, dfs):
    complete_df = pd.DataFrame()
    for i, df in enumerate(dfs):
        dfi = df.pivot_table(columns="channel_name", values=kkm).reset_index(
            names="Measurement"
        )
        dfi["dataset_index"] = i
        dfi["date"] = dates[i]
        complete_df = pd.concat([complete_df, dfi])
    complete_df = complete_df.reset_index(drop=True)
    complete_df = complete_df[complete_df["Measurement"] == kkm[measurement]]
    complete_df = complete_df.drop(columns="Measurement")
    return complete_df
