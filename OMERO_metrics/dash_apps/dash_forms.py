import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
import pandas as pd
from dash_iconify import DashIconify
from datetime import datetime
from microscopemetrics_schema import datamodel as mm_schema
from dataclasses import fields

primary_color = "#008080"

external_scripts = [
    # add the tailwind cdn url hosting the files with the utility classes
    {"src": "https://cdn.tailwindcss.com"}
]
stylesheets = [
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css",
    "./assets/omero_metrics.css",
]
dashboard_name = "omero_project_config_form"
dash_form_project = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=stylesheets,
    external_scripts=external_scripts,
)

analysis_type = [
    {"label": field.name, "value": f"{i}"}
    for i, field in enumerate(
        fields(mm_schema.FieldIlluminationInputParameters)
    )
]


dash_form_project.layout = dmc.MantineProvider(
    [
        dmc.Container(
            [
                dmc.Center(
                    [
                        dmc.Text(
                            id="title",
                            c=primary_color,
                            style={"fontSize": 30},
                        ),
                        dmc.Group(
                            [
                                html.Img(
                                    src="./assets/images/logo.png",
                                    style={"width": "100px"},
                                ),
                                dmc.Text(
                                    "OMERO Metrics Dashboard",
                                    c=primary_color,
                                    style={"fontSize": 15},
                                ),
                            ]
                        ),
                    ]
                ),
                dmc.Divider(variant="solid", style={"marginBottom": 20}),
                dmc.Stack(
                    [
                        dmc.Text(
                            "Project Configuration",
                            style={"fontSize": 20},
                        ),
                        dmc.Text(
                            "Configure the project to be analyzed",
                            style={"fontSize": 15},
                        ),
                        dmc.Divider(variant="solid"),
                        dmc.Select(
                            id="my-dropdown2",
                            label="Select Analysis Type",
                            data=analysis_type,
                            w="300",
                            value="1",
                            clearable=False,
                            leftSection=DashIconify(
                                icon="radix-icons:ruler-horizontal"
                            ),
                            rightSection=DashIconify(
                                icon="radix-icons:chevron-down"
                            ),
                        ),
                    ],
                    gap="xs",
                ),
            ],
            fluid=True,
            style={
                "background-color": "#eceff1",
                "margin": "20px",
                "border-radius": "0.5rem",
                "padding": "10px",
            },
        ),
    ]
)
