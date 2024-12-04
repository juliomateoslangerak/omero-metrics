import dash_mantine_components as dmc
from dash import dcc
from dash_iconify import DashIconify
from OMERO_metrics.styles import THEME

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
