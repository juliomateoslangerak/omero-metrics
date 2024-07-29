import dash_mantine_components as dmc
from dash import dcc, html
import plotly.graph_objs as go
import numpy as np


# np.max(stack, axis=0)
# go.Heatmap(z=image.tolist(), colorscale="hot", hovertemplate=None)


global bool_list
def update_visibility(i, n):
    bool_list = [False] * n
    bool_list[i] = True
    return bool_list


def image_heatmap_setup(channels, image, df, min_distance):
    fig = go.Figure()
    # Add dropdowns
    for i, chan in enumerate(channels):
        ima_z = np.max(image[:, :, :, i], axis=0)
        fig.add_trace(
            go.Heatmap(
                z=ima_z.tolist(),
                colorscale="hot",
                name=chan,
            )
        )
    fig.update_layout(
        height=image[0, :, :, 0].shape[0] + 150,
        autosize=False,
        margin=dict(t=30, b=30, l=0, r=0),
    )

    color_map = {"Yes": "red", "No": "yellow"}
    sc = go.Scatter(
        y=df["center_y"],
        x=df["center_x"],
        mode="markers",
        name="Beads Locations",
        marker=dict(
            size=10,
            color="red",
            opacity=0.3,
        ),
        text=df["channel_nr"],
        customdata=np.stack(
            (
                df["bead_id"],
                df["considered_axial_edge"],
            ),
            axis=-1,
        ),
        hovertemplate="<b>Bead Number:</b>  %{customdata[0]} <br>"
        + "<b>Channel Number:</b>  %{text} <br>"
        + "<b>Considered Axial Edge:</b> %{customdata[1]} <br><extra></extra>",
    )
    fig.add_trace(sc)
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

    button_layer_1_height = 1.08
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
                x=0.1,
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
                x=0.30,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top",
            ),
            dict(
                buttons=list(
                    [
                        dict(
                            args=[
                                {
                                    "contours.showlines": False,
                                    "type": "contour",

                                },
                                [0, 1, 2, 3]
                            ],
                            label="Hide lines",
                            method="restyle",
                        ),
                        dict(
                            args=[
                                {
                                    "contours.showlines": True,
                                    "type": "contour",
                                    "contours.showlabels": True,
                                    "contours.labelfont.size": 12,
                                    "contours.labelfont.color": "white",
                                },
                                [0, 1, 2, 3]

                            ],
                            label="Show lines",
                            method="restyle",
                        ),
                        dict(
                            args=[{"type": "heatmap"}, [0, 1, 2, 3]],
                            label="Heatmap",
                            method="restyle",
                        ),
                    ]
                ),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.50,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top",
            ),
            dict(
                buttons=list(
                    [
                        dict(
                            label="None",
                            method="relayout",
                            args=["shapes", []],
                        ),
                        dict(
                            label="Corners",
                            method="relayout",
                            args=["shapes", corners],
                        ),
                    ]
                ),
                direction="down",
                pad={
                    "r": 10,
                    "t": 10,
                },
                showactive=True,
                x=0.70,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top",
            ),
            dict(
                active=0,
                buttons=list(
                    [
                        dict(
                            label=chan,
                            method="restyle",
                            args=[
                                {
                                    "visible": update_visibility(
                                        i, len(channels)
                                    ),
                                    "value_test": i,
                                },
                             [0, 1, 2, 3, 4]
                    ],
                        )
                        for i, chan in enumerate(channels)
                    ]
                ),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.87,
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
                                [4],
                            ],
                        ),
                        dict(
                            label="None",
                            method="restyle",
                            args=[
                                {"visible": False},
                                [4],
                            ],
                        ),
                    ]
                ),
            ),
        ]
    )
    fig.update_layout(
        annotations=[
            dict(
                text="colorscale",
                x=0,
                xref="paper",
                y=1.06,
                yref="paper",
                align="left",
                showarrow=False,
            ),
            dict(
                text="Reverse<br>Colorscale",
                x=0.23,
                xref="paper",
                y=1.07,
                yref="paper",
                showarrow=False,
            ),
            dict(
                text="Lines",
                x=0.46,
                xref="paper",
                y=1.06,
                yref="paper",
                showarrow=False,
            ),
            dict(
                text="Shapes",
                x=0.64,
                xref="paper",
                y=1.06,
                yref="paper",
                showarrow=False,
            ),
            dict(
                text="Type",
                x=0.85,
                xref="paper",
                y=1.06,
                yref="paper",
                showarrow=False,
            ),
        ]
    )

    return fig
