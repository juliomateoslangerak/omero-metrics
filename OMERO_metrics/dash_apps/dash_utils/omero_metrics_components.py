import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
from OMERO_metrics.styles import (
    THEME,
    HEADER_PAPER_STYLE,
    BUTTON_STYLE,
)

import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots
from typing import Union


def make_control(text, action_id):
    return dmc.Flex(
        [
            dmc.AccordionControl(text),
            dmc.ActionIcon(
                children=my_components.get_icon(icon="lets-icons:check-fill"),
                color="green",
                variant="default",
                n_clicks=0,
                id={"index": action_id},
            ),
        ],
        justify="center",
        align="center",
    )


def get_icon(icon, size=20, color=None):
    return DashIconify(icon=icon, height=size, color=color)


def fig_mip(mip_x, mip_y, mip_z):
    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[[{}, {}], [{"colspan": 2}, None]],
        subplot_titles=("MIP X axis", "MIP Y axis", "MIP Z axis"),
    )
    fig = fig.add_trace(mip_x.data[0], row=1, col=1)
    fig = fig.add_trace(mip_y.data[0], row=1, col=2)
    fig = fig.add_trace(mip_z.data[0], row=2, col=1)
    fig = fig.update_layout(
        coloraxis=dict(colorscale="hot"),
        autosize=False,
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


def mip_graphs(
    x0: int,
    xf: int,
    y0: int,
    yf: int,
    stack: Union[np.array, list],
    do_sqrt: bool = True,
):
    image_bead = stack[:, y0:yf, x0:xf]
    image_x = np.max(image_bead, axis=2)
    image_y = np.max(image_bead, axis=1)
    image_z = np.max(image_bead, axis=0)
    if do_sqrt:
        image_x = np.sqrt(image_x)
        image_y = np.sqrt(image_y)
        image_z = np.sqrt(image_z)
    image_x = image_x / image_x.max()
    image_y = image_y / image_y.max()
    image_z = image_z / image_z.max()

    mip_x = px.imshow(
        image_x,
        zmin=image_x.min(),
        zmax=image_x.max(),
    )
    mip_y = px.imshow(
        image_y,
        zmin=image_y.min(),
        zmax=image_y.max(),
    )
    mip_z = px.imshow(
        image_z,
        zmin=image_z.min(),
        zmax=image_z.max(),
    )
    return mip_x, mip_y, mip_z


def crop_bead_index(bead, min_dist, stack):
    x = bead["center_x"].values[0]
    y = bead["center_y"].values[0]
    x0 = max(0, x - min_dist)
    y0 = max(0, y - min_dist)
    xf = min(stack.shape[2], x + min_dist)
    yf = min(stack.shape[1], y + min_dist)
    return x0, xf, y0, yf


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
                        DashIconify(
                            icon="material-symbols:download", width=20
                        ),
                        color=THEME["primary"],
                    )
                ),
                dmc.MenuDropdown(
                    [
                        dmc.MenuItem(
                            "CSV",
                            id="table-download-csv",
                            leftSection=DashIconify(
                                icon="iwwa:file-csv", width=20
                            ),
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
                                src="/static/OMERO_metrics/images/metrics_logo.png",
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
