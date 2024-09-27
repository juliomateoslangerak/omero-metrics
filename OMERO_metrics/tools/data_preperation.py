import yaml
import omero.gateway as gateway
from datetime import datetime, timedelta
from random import randrange
import collections
import omero
import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from typing import Union
from microscopemetrics_schema import datamodel as mm_schema

PROFILES_COLORS = {
    "center_vertical": "red",
    "center_horizontal": "blue",
    "leftBottom_to_rightTop": "green",
    "leftTop_to_rightBottom": "yellow",
}


# This function is no longer needed
def get_intensity_profile(image):
    image = image[0, 0, :, :, 0] / 255
    image_flipped = np.flip(image, axis=1)
    rb = image[:, -1]
    lb = image[:, 0]
    dr = np.fliplr(image).diagonal()
    dl = np.fliplr(image_flipped).diagonal()
    df = pd.DataFrame(
        {
            "Right Bottom": rb,
            "Left Bottom": lb,
            "Diagonal Right": dr,
            "Diagonal Left": dl,
        }
    )
    return df


def add_rect_rois(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
    for i, row in df.iterrows():
        fig.add_shape(
            go.layout.Shape(
                type="rect",
                x0=row.X,
                y0=row.Y,
                x1=row.X + row.W,
                y1=row.Y + row.H,
                xref="x",
                yref="y",
                line=dict(
                    color="RoyalBlue",
                    width=3,
                ),
            )
        )
    return fig


def add_line_rois_trace(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
    for i, row in df.iterrows():
        data = pd.DataFrame(
            dict(
                x=np.array(range(int(row.X1), int(row.X2))),
                y=np.array(range(int(row.Y1), int(row.Y2))),
            )
        )
        fig.add_trace(
            go.Scatter(x=data.x, y=data.y, mode="lines", name=str(row.NAME))
        )
    return fig


def add_line_rois(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
    for i, row in df.iterrows():
        fig.add_shape(
            go.layout.Shape(
                type="line",
                name=str(row.NAME),
                showlegend=True,
                editable=True,
                x0=row.X1,
                y0=row.Y1,
                x1=row.X2,
                y1=row.Y2,
                xref="x",
                yref="y",
                line=dict(
                    color="Green",
                    width=1,
                    dash="dot",
                ),
            )
        )
    return fig


def add_point_rois(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
    fig.add_trace(
        go.Scatter(
            x=df.X,
            y=df.Y,
            mode="markers",
            customdata=df.ROI_NAME,
            hovertemplate="%{customdata}",
        )
    )
    return fig


def get_rois_omero(result):
    shapes_line = {}
    shapes_rectangle = {}
    shapes_point = {}
    for roi in result.rois:
        for s in roi.copyShapes():
            shape = {"id": s.getId().getValue()}
            # shape["theT"] = s.getTheT().getValue()
            # shape["theZ"] = s.getTheZ().getValue()
            if s.getTextValue():
                shape["textValue"] = s.getTextValue().getValue()
            if s.__class__.__name__ == "RectangleI":
                shape["type"] = "Rectangle"
                shape["x"] = s.getX().getValue()
                shape["y"] = s.getY().getValue()
                shape["w"] = s.getWidth().getValue()
                shape["h"] = s.getHeight().getValue()
                shapes_rectangle[s.getId().getValue()] = shape
            elif s.__class__.__name__ == "LineI":
                shape["type"] = "Line"
                shape["x1"] = s.getX1().getValue()
                shape["x2"] = s.getX2().getValue()
                shape["y1"] = s.getY1().getValue()
                shape["y2"] = s.getY2().getValue()

                shapes_line[s.getId().getValue()] = shape
            elif s.__class__.__name__ == "PointI":
                shape["type"] = "Point"
                shape["x"] = s.getX().getValue()
                shape["y"] = s.getY().getValue()
                # shape['z'] = s.getZ().getValue()
                shape["channel"] = s.getTheC().getValue()
                shapes_point[s.getId().getValue()] = shape
            elif s.__class__.__name__ == "PolygonI":
                continue
    return shapes_rectangle, shapes_line, shapes_point


def add_colors_intensity_profile(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[:, "color"] = [PROFILES_COLORS[i] for i in df.NAME]
    return df


def get_info_roi_points(shape_dict):
    data = [
        [key, int(value["x"]), int(value["y"]), int(value["channel"])]
        for key, value in shape_dict.items()
    ]
    df = pd.DataFrame(data, columns=["ROI", "X", "Y", "C"])
    return df


def get_info_roi_lines(shape_dict):
    data = [
        [
            key,
            value["x1"],
            value["y1"],
            value["x2"],
            value["y2"],
            value["textValue"],
        ]
        for key, value in shape_dict.items()
    ]
    df = pd.DataFrame(data, columns=["ROI", "X1", "Y1", "X2", "Y2", "NAME"])
    return df


def get_info_roi_rectangles(shape_dict):
    data = [
        [
            key,
            value["x"],
            value["y"],
            value["w"],
            value["h"],
            value["textValue"],
        ]
        for key, value in shape_dict.items()
    ]
    df = pd.DataFrame(data, columns=["ROI", "X", "Y", "W", "H", "NAME"])
    return df


def get_dataset_ids_lists(project):
    """
    Get the processed and unprocessed dataset ids for a project
    """
    processed_datasets = []
    unprocessed_datasets = []
    for dataset in project.listChildren():
        try:
            dataset.getAnnotation().getNs()
            processed_datasets.append(dataset.getId())
        except AttributeError:
            unprocessed_datasets.append(dataset.getId())
    return processed_datasets, unprocessed_datasets


def get_image_list_by_dataset_id(conn, dataset_id):
    """
    Get the list of images for a dataset
    """
    dataset = conn.getObject("Dataset", dataset_id)
    images = []
    for image in dataset.listChildren():
        images.append(image.getId())
    return images


def get_dataset_map_annotation(dataset_wrapper):
    """
    Get the mapAnnotation for a dataset
    """
    df = {}
    try:
        for i in dataset_wrapper.listAnnotations():
            if "FieldIlluminationKeyValues" in i.getNs():
                table = dict(i.getValue())
                df = pd.DataFrame(table.items(), columns=["Key", "Value"])
                break
            elif "PSFBeadsKeyValues" in i.getNs():
                table = dict(i.getValue())
                df = pd.DataFrame(table.items(), columns=["Key", "Value"])
                break
        return df
    except AttributeError:
        return df


def read_config_from_file_ann(file_annotation):
    return yaml.load(
        file_annotation.getFileInChunks().__next__().decode(),
        Loader=yaml.SafeLoader,
    )


def get_file_annotation_project(project_wrapper):
    study_config = None
    for ann in project_wrapper.listAnnotations():
        if (
            type(ann) == gateway.FileAnnotationWrapper
            and ann.getFile().getName() == "study_config.yaml"
        ):
            study_config = read_config_from_file_ann(ann)
    return study_config


def get_analysis_type(project_wrapper):
    study_config = get_file_annotation_project(project_wrapper)
    try:
        analysis_type = next(iter(study_config["analysis"]))
    except KeyError:
        analysis_type = None
    return analysis_type


def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


def get_table_original_file_id(conn, file_id):
    ctx = conn.createServiceOptsDict()
    ctx.setOmeroGroup("-1")
    r = conn.getSharedResources()
    t = r.openTable(omero.model.OriginalFileI(file_id), ctx)
    data_buffer = collections.defaultdict(list)
    heads = t.getHeaders()
    target_cols = range(len(heads))
    index_buffer = []
    num_rows = t.getNumberOfRows()
    for start in range(0, num_rows):
        data = t.read(target_cols, start, start)
        for col in data.columns:
            data_buffer[col.name] += col.values
        index_buffer += data.rowNumbers
    df = pd.DataFrame.from_dict(data_buffer)
    df.index = index_buffer[0 : len(df)]
    return df


def get_original_file_id(dataset):
    dataset_id = None
    for ann in dataset.listAnnotations():
        if type(ann) == gateway.FileAnnotationWrapper:
            if type(ann.getFile()) == gateway.OriginalFileWrapper:
                dataset_id = ann.getFile().getId()
                break
    return dataset_id


def processed_data_project_view(processed_list):
    d1 = datetime.strptime("1/1/2000 1:30 PM", "%m/%d/%Y %I:%M %p")
    d2 = datetime.strptime("1/1/2024 4:50 AM", "%m/%d/%Y %I:%M %p")
    df = pd.DataFrame(
        [[random_date(d1, d2), i] for i in processed_list],
        columns=["Date", "Dataset_ID"],
    )
    return df


def get_original_file_id_by_image_id(dataset):
    list_file = []
    for ann in dataset.listAnnotations():
        if type(ann) == gateway.FileAnnotationWrapper:
            if type(ann.getFile()) == gateway.OriginalFileWrapper:
                list_file.append(
                    [ann.getFile().getId(), ann.getFile().getName()]
                )
    return list_file


def get_intensity_map_image(image_name, list_file):
    for file_id, name in list_file:
        if image_name in name:
            return file_id
        else:
            return None


# ---------------------------------------dash_functions--------------------------------------------------


def fig_mip(mip_x, mip_y, mip_z, title):
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
        title_text=title,
        coloraxis=dict(colorscale="hot"),
        autosize=False,
    )
    fig.update_layout(
        {  # "margin": {"l": 10, "r": 10, "t": 10, "b": 10},
            "xaxis": {
                "automargin": False,
                "rangemode": "nonnegative",
                "range": [0, mip_x.data[0].z.max()],
            },
            "xaxis2": {"automargin": False, "rangemode": "nonnegative"},
            "xaxis3": {"automargin": False, "rangemode": "nonnegative"},
            "yaxis": {
                "anchor": "x",
                "scaleanchor": "x",
                "autorange": "reversed",
                "automargin": False,
            },
            "yaxis2": {
                "anchor": "x2",
                "scaleanchor": "x2",
                "autorange": "reversed",
                "automargin": False,
            },
            "yaxis3": {
                "anchor": "x3",
                "scaleanchor": "x3",
                "autorange": "reversed",
                "automargin": False,
            },
        }
    )
    # fig = fig.update_yaxes(automargin=False)
    # fig = fig.update_xaxes(automargin=False)

    return fig


def mip_graphs(
    x0: int, xf: int, y0: int, yf: int, stack: Union[np.array, list]
):
    image_bead = stack[:, y0:yf, x0:xf]
    image_x = np.max(image_bead, axis=2)
    image_y = np.max(image_bead, axis=1)
    image_z = np.max(image_bead, axis=0)
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
    # z = bead["center_z"].values[0]
    x0 = max(0, x - min_dist)
    y0 = max(0, y - min_dist)
    xf = min(stack.shape[2], x + min_dist)
    yf = min(stack.shape[1], y + min_dist)
    return x0, xf, y0, yf


def image_3d_chart(image_bead):
    image_bead = image_bead / image_bead.max()
    lz, ly, lx = image_bead.shape
    z, y, x = np.mgrid[:lz, :ly, :lx]
    fig = go.Figure(
        data=go.Volume(
            x=z.flatten(),
            y=y.flatten(),
            z=x.flatten(),
            value=image_bead.flatten(),
            isomin=0,
            isomax=1,
            opacity=0.3,
            # surface_count=25,
        )
    )
    fig = fig.update_layout(
        scene_xaxis_showticklabels=False,
        scene_yaxis_showticklabels=False,
        scene_zaxis_showticklabels=False,
    )
    return fig


# ---------------------------------------READING FROM MM_DATASET--------------------------------------------------
