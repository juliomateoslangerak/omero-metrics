import dash_mantine_components as dmc
from dash import dcc, html
import plotly.graph_objs as go
import numpy as np
import plotly.express as px


def layout_utility(channels, image, df, min_distance):
    fig = px.imshow(
        image,
        zmin=image.min(),
        zmax=image.max(),
        color_continuous_scale="hot",
    )
    # Add dropdowns
    fig.update_layout(
        height=image.shape[0] + 100,
        autosize=False,
        margin=dict(t=0, b=0, l=10, r=0),
        template="plotly_white",
    )
    color_map = {"Yes": "green", "No": "red"}
    df["considered_axial_edge"] = df["considered_axial_edge"].map(
        {0: "No", 1: "Yes"}
    )
    df["considered_valid"] = df["considered_valid"].map({0: "No", 1: "Yes"})
    df["considered_self_proximity"] = df["considered_self_proximity"].map(
        {0: "No", 1: "Yes"}
    )
    df["considered_lateral_edge"] = df["considered_lateral_edge"].map(
        {0: "No", 1: "Yes"}
    )
    df["considered_intensity_outlier"] = df[
        "considered_intensity_outlier"
    ].map({0: "No", 1: "Yes"})

    beads_location_plot = go.Scatter(
        y=df["center_y"],
        x=df["center_x"],
        mode="markers",
        name="Beads Locations",
        visible=True,
        marker=dict(
            size=10, opacity=0.3, color=df["considered_valid"].map(color_map)
        ),
        text=df["channel_nr"],
        customdata=np.stack(
            (
                df["bead_id"],
                df["considered_axial_edge"],
                df["considered_valid"],
                df["considered_self_proximity"],
                df["considered_lateral_edge"],
                df["considered_intensity_outlier"],
            ),
            axis=-1,
        ),
        hovertemplate="<b>Bead Number:</b>  %{customdata[0]} <br>"
        + "<b>Channel Number:</b>  %{text} <br>"
        + "<b>Considered valid:</b>  %{customdata[2]}<br>"
        + "<b>Considered self proximity:</b>  %{customdata[3]}<br>"
        + "<b>Considered lateral edge:</b>  %{customdata[4]}<br>"
        + "<b>Considered intensity outlier:</b>  %{customdata[5]}<br>"
        + "<b>Considered Axial Edge:</b> %{customdata[1]} <br><extra></extra>",
    )
    fig.add_trace(beads_location_plot)
    corners = [
        dict(
            type="rect",
            x0=row.center_x - min_distance,
            y0=row.center_y - min_distance,
            x1=row.center_x + min_distance,
            y1=row.center_y + min_distance,
            xref="x",
            yref="y",
            line=dict(
                color="RoyalBlue",
                width=3,
            ),
        )
        for i, row in df.iterrows()
    ]
    button_layer_1_height = 1.14
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=list(
                    [
                        dict(
                            args=["colorscale", "Hot"],
                            label="Hot",
                            method="restyle",
                        ),
                        dict(
                            args=["colorscale", "Viridis"],
                            label="Viridis",
                            method="restyle",
                        ),
                        dict(
                            args=["colorscale", "Cividis"],
                            label="Cividis",
                            method="restyle",
                        ),
                        dict(
                            args=["colorscale", "Blues"],
                            label="Blues",
                            method="restyle",
                        ),
                        dict(
                            args=["colorscale", "Greens"],
                            label="Greens",
                            method="restyle",
                        ),
                    ]
                ),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top",
            ),
            dict(
                buttons=list(
                    [
                        dict(
                            args=["reversescale", False],
                            label="False",
                            method="restyle",
                        ),
                        dict(
                            args=["reversescale", True],
                            label="True",
                            method="restyle",
                        ),
                    ]
                ),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.15,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top",
            ),

            dict(
                buttons=list(
                    [
                        dict(
                            label="Beads ROI",
                            method="relayout",
                            args=["shapes", corners],
                        ),
                        dict(
                            label="None",
                            method="relayout",
                            args=["shapes", []],
                        ),
                    ]
                ),
                direction="down",
                pad={
                    "r": 10,
                    "t": 10,
                },
                showactive=True,
                x=0.3,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top",
            ),

            dict(
                active=0,
                buttons=list(
                    [
                        dict(
                            label="Beads Location",
                            method="restyle",
                            args=[
                                {"visible": True},
                                {
                                    "title": "Beads Location On",
                                    "annotations": [],
                                },
                                [1],
                            ],
                        ),
                        dict(
                            label="None",
                            method="restyle",
                            args=[
                                {"visible": False},
                                {
                                    "title": "Beads Location Off",
                                    "annotations": [],
                                },
                                [1],
                            ],
                        ),
                    ]
                ),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.55,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top",
            ),
        ]
    )
    fig.update_layout(
        annotations=[
            dict(
                text="colorscale",
                x=0,
                xref="paper",
                y=1.05,
                yref="paper",
                align="left",
                showarrow=False,
            ),
            dict(
                text="Reverse Colorscale",
                x=0.15,
                xref="paper",
                y=1.05,
                yref="paper",
                showarrow=False,
            ),
            dict(
                text="Beads ROI",
                x=0.3,
                xref="paper",
                y=1.05,
                yref="paper",
                showarrow=False,
            ),
            dict(
                text="Beads Location",
                x=0.55,
                xref="paper",
                y=1.05,
                yref="paper",
                showarrow=False,
            ),


        ]
    )


    return fig
