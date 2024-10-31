import dash
import pandas as pd
from dash import dcc, html
from django_plotly_dash import DjangoDash
import plotly.express as px
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from skimage.exposure import rescale_intensity

# Theme Configuration
THEME = {
    "primary": "#189A35",
    "secondary": "#63aa47",
    "background": "#ffffff",
    "surface": "#f8f9fa",
    "border": "#e9ecef",
    "text": {
        "primary": "#2C3E50",
        "secondary": "#6c757d",
    },
}


def get_icon(icon, size=20, color=None):
    return DashIconify(icon=icon, height=size, color=color)


dashboard_name = "omero_dataset_metrics"
dash_app_dataset = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=dmc.styles.ALL,
)

dash_app_dataset.layout = dmc.MantineProvider(
    theme={
        "colorScheme": "light",
        "primaryColor": "green",
        "components": {
            "Card": {"styles": {"root": {"borderRadius": "8px"}}},
            "Select": {"styles": {"input": {"borderRadius": "8px"}}},
        },
    },
    children=[
        dmc.Container(
            [
                # Header Section
                dmc.Paper(
                    shadow="sm",
                    p="md",
                    radius="lg",
                    mb="md",
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
                                                    "Field of Illumination Analysis",
                                                    c=THEME["primary"],
                                                    size="h2",
                                                ),
                                                dmc.Text(
                                                    "Microscopy Image Analysis Dashboard",
                                                    c=THEME["text"][
                                                        "secondary"
                                                    ],
                                                    size="sm",
                                                ),
                                            ],
                                            gap="xs",
                                        ),
                                    ],
                                ),
                                dmc.Badge(
                                    "FOI Analysis",
                                    color="green",
                                    variant="dot",
                                    size="lg",
                                ),
                            ],
                            justify="space-between",
                        ),
                    ],
                ),
                # Main Content
                dmc.Grid(
                    gutter="md",
                    align="stretch",
                    children=[
                        # Left Column - Intensity Map
                        dmc.GridCol(
                            span=6,
                            children=[
                                dmc.Paper(
                                    h="100%",
                                    shadow="xs",
                                    p="md",
                                    radius="md",
                                    children=[
                                        dmc.Stack(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.Text(
                                                            "Intensity Map",
                                                            fw=500,
                                                            size="lg",
                                                        ),
                                                        dmc.Select(
                                                            id="channel_dropdown_foi",
                                                            clearable=False,
                                                            allowDeselect=False,
                                                            w="200",
                                                            value="0",
                                                            leftSection=get_icon(
                                                                "radix-icons:magnifying-glass"
                                                            ),
                                                            rightSection=get_icon(
                                                                "radix-icons:chevron-down"
                                                            ),
                                                            styles={
                                                                "label": {
                                                                    "fontWeight": 500
                                                                },
                                                                "input": {
                                                                    "borderColor": THEME[
                                                                        "primary"
                                                                    ]
                                                                },
                                                            },
                                                        ),
                                                    ],
                                                    justify="space-between",
                                                ),
                                                dcc.Graph(
                                                    id="intensity_map",
                                                    config={
                                                        "displayModeBar": True,
                                                        "scrollZoom": True,
                                                        "modeBarButtonsToRemove": [
                                                            "lasso2d",
                                                            "select2d",
                                                        ],
                                                    },
                                                    style={
                                                        "height": "250px",
                                                    },
                                                ),
                                            ],
                                            gap="md",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        # Right Column - Key Measurements
                        dmc.GridCol(
                            span=6,
                            children=[
                                dmc.Paper(
                                    h="100%",
                                    shadow="xs",
                                    p="md",
                                    radius="md",
                                    children=[
                                        dmc.Stack(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.Text(
                                                            "Key Measurements",
                                                            fw=500,
                                                            size="lg",
                                                        ),
                                                        dmc.Tooltip(
                                                            label="Statistical measurements for the selected channel",
                                                            children=[
                                                                get_icon(
                                                                    "material-symbols:info-outline",
                                                                    color=THEME[
                                                                        "primary"
                                                                    ],
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                    justify="space-between",
                                                ),
                                                dmc.ScrollArea(
                                                    h=250,
                                                    offsetScrollbars=True,
                                                    children=[
                                                        dmc.Table(
                                                            id="km_table",
                                                            striped=True,
                                                            highlightOnHover=True,
                                                            withTableBorder=True,
                                                            withColumnBorders=True,
                                                            fz="sm",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            gap="md",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                # Hidden element for callbacks
                html.Div(id="blank-input"),
                # Intensity Profiles Section
                dmc.Paper(
                    shadow="xs",
                    p="md",
                    radius="md",
                    mt="md",
                    children=[
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        dmc.Text(
                                            "Intensity Profiles",
                                            fw=500,
                                            size="lg",
                                        ),
                                        dmc.SegmentedControl(
                                            id="profile-type",
                                            data=[
                                                {
                                                    "value": "natural",
                                                    "label": "Smooth",
                                                },
                                                {
                                                    "value": "linear",
                                                    "label": "Linear",
                                                },
                                            ],
                                            value="natural",
                                            color="green",
                                        ),
                                    ],
                                    justify="space-between",
                                ),
                                dmc.LineChart(
                                    id="intensity_profile",
                                    h=250,
                                    dataKey="Pixel",
                                    data={},
                                    series=[
                                        {
                                            "name": "Diagonal (↘)",
                                            "color": "violet.9",
                                        },
                                        {
                                            "name": "Diagonal (↗)",
                                            "color": "blue.9",
                                        },
                                        {
                                            "name": "Horizontal (→)",
                                            "color": "pink.9",
                                        },
                                        {
                                            "name": "Vertical (↓)",
                                            "color": "teal.9",
                                        },
                                    ],
                                    xAxisLabel="Position (pixels)",
                                    yAxisLabel="Intensity",
                                    tickLine="y",
                                    gridAxis="xy",
                                    withXAxis=True,
                                    withYAxis=True,
                                    withLegend=True,
                                    strokeWidth=2,
                                    withDots=False,
                                    curveType="natural",
                                ),
                            ],
                            gap="xl",
                        ),
                    ],
                ),
            ],
            size="xl",
            p="md",
            style={"backgroundColor": THEME["surface"]},
        ),
    ],
)


@dash_app_dataset.expanded_callback(
    dash.dependencies.Output("channel_dropdown_foi", "data"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_dropdown_menu(*args, **kwargs):
    try:
        channel = kwargs["session_state"]["context"]["channel_names"]
        return [
            {"label": f"{name} (Channel {i})", "value": f"{i}"}
            for i, name in enumerate(channel)
        ]
    except Exception as e:
        return [{"label": "Error loading channels", "value": "0"}]


@dash_app_dataset.expanded_callback(
    dash.dependencies.Output("km_table", "data"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_km_table(*args, **kwargs):
    try:
        table = kwargs["session_state"]["context"]["key_values_df"]
        metrics_df = table[
            [
                "channel_name",
                "center_region_intensity_fraction",
                "center_region_area_fraction",
                "max_intensity",
            ]
        ].copy()

        # Improve column names for readability
        column_mapping = {
            "channel_name": "Channel",
            "center_region_intensity_fraction": "Center Intensity Ratio",
            "center_region_area_fraction": "Center Area Ratio",
            "max_intensity": "Peak Intensity",
        }

        metrics_df = metrics_df.round(3)
        metrics_df.columns = [
            column_mapping.get(col, col) for col in metrics_df.columns
        ]

        return {
            "head": metrics_df.columns.tolist(),
            "body": metrics_df.values.tolist(),
            "caption": "Statistical measurements across channels",
        }
    except Exception as e:
        return {
            "head": ["Error"],
            "body": [[str(e)]],
            "caption": "Error loading measurements",
        }


@dash_app_dataset.expanded_callback(
    dash.dependencies.Output("intensity_map", "figure"),
    dash.dependencies.Output("intensity_profile", "data"),
    [
        dash.dependencies.Input("channel_dropdown_foi", "value"),
        dash.dependencies.Input("profile-type", "value"),
    ],
)
def update_visualizations(*args, **kwargs):
    try:
        channel = int(args[0])
        curve_type = args[1]

        # Get data from context
        images = kwargs["session_state"]["context"]["image"]
        df_intensity_profiles = kwargs["session_state"]["context"][
            "intensity_profiles"
        ]
        print(df_intensity_profiles)
        # Process image data
        image = images[channel]
        image_channel = image[0, 0, :, :]
        image_channel = rescale_intensity(
            image_channel,
            in_range=(0, image_channel.max()),
            out_range=(0.0, 1.0),
        )

        # Create intensity map
        fig = px.imshow(
            image_channel,
            color_continuous_scale="hot",
            labels={"color": "Intensity"},
        )

        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
            plot_bgcolor=THEME["background"],
            paper_bgcolor=THEME["background"],
            xaxis_title="X Position (pixels)",
            yaxis_title="Y Position (pixels)",
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            xaxis_zeroline=False,
            yaxis_zeroline=False,
        )

        # Process profile data
        channel_regex = f"Ch0{channel}"
        df_profile = df_intensity_profiles[
            df_intensity_profiles.columns[
                df_intensity_profiles.columns.str.startswith(channel_regex)
            ]
        ].copy()

        df_profile.columns = df_profile.columns.str.replace(
            "Ch\d{2}_", "", regex=True
        )
        df_profile = restyle_dataframe(df_profile, "columns")
        df_profile = df_profile.reset_index()
        df_profile.columns = df_profile.columns.str.replace(
            "Lefttop To Rightbottom", "Diagonal (↘)"
        )
        df_profile.columns = df_profile.columns.str.replace(
            "Leftbottom To Righttop", "Diagonal (↗)"
        )
        df_profile.columns = df_profile.columns.str.replace(
            "Center Horizontal", "Horizontal (→)"
        )
        df_profile.columns = df_profile.columns.str.replace(
            "Center Vertical", "Vertical (↓)"
        )
        return fig, df_profile.to_dict("records")

    except Exception as e:
        # Return empty visualizations with error message
        fig = px.imshow([[0]])
        fig.add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig, []


def restyle_dataframe(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Improve column names for better readability."""
    value = getattr(df, col).str.replace("_", " ", regex=True).str.title()
    setattr(df, col, value)
    return df
