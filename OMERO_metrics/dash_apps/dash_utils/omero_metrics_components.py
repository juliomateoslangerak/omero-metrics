import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
from OMERO_metrics.styles import (
    THEME,
    HEADER_PAPER_STYLE,
    BUTTON_STYLE,
)

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
