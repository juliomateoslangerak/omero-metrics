import plotly.graph_objs as go
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

PROFILES_COLORS = {
    "center_vertival": "red",
    "center_horizontal": "blue",
    "leftBottom_to_rightTop": "green",
    "leftTop_to_rightBottom": "yellow",
}


# This function is no longer needed
def get_intensity_profile(imaaa):
    imaaa = imaaa[0, 0, :, :, 0] / 255
    imaa_fliped = np.flip(imaaa, axis=1)
    rb = imaaa[:, -1]
    lb = imaaa[:, 0]
    dr = np.fliplr(imaaa).diagonal()
    dl = np.fliplr(imaa_fliped).diagonal()
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
            go.Scatter(x=data.x, y=data.y, mode="lines", name=str(row.ROI))
        )
    return fig


def add_line_rois(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
    for i, row in df.iterrows():
        fig.add_shape(
            go.layout.Shape(
                type="line",
                name=str(row.ROI),
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
    fig.add_trace(go.Scatter(x=df.X, y=df.Y, mode="markers"))
    return fig


def get_rois_omero(result):
    shapes_line = {}
    shapes_rectangle = {}
    shapes_point = {}
    for roi in result.rois:
        for s in roi.copyShapes():
            shape = {}
            shape["id"] = s.getId().getValue()
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


def get_dataset_ids_lists(conn, project):
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


def get_dataset_mapAnnotation(datasetWrapper):
    """
    Get the mapAnnotation for a dataset
    """

    try:
        for i in datasetWrapper.listAnnotations():
            if "FieldIlluminationKeyValues" in i.getNs():
                table = dict(i.getValue())
                df = pd.DataFrame(table.items(), columns=["Key", "Value"])
                break
            elif "PSFBeadsKeyValues" in i.getNs():
                table = dict(i.getValue())
                df = pd.DataFrame(table.items(), columns=["Key", "Value"])
                break
        return df
    except:
        return {}


def read_config_from_file_ann(file_annotation):
    return yaml.load(
        file_annotation.getFileInChunks().__next__().decode(),
        Loader=yaml.SafeLoader,
    )


def get_file_annotation_project(projectWrapper):
    study_config = None
    for ann in projectWrapper.listAnnotations():
        if (
            type(ann) == gateway.FileAnnotationWrapper
            and ann.getFile().getName() == "study_config.yaml"
        ):
            study_config = read_config_from_file_ann(ann)
    return study_config


def get_analysis_type(projectWrapper):
    study_config = get_file_annotation_project(projectWrapper)
    try:
        analysis_type = next(iter(study_config["analysis"]))
    except:
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


def get_table_originalFile_id(conn, file_id):
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


def getOriginalFile_id(dataset):
    id = None
    for ann in dataset.listAnnotations():
        if type(ann) == gateway.FileAnnotationWrapper:
            if type(ann.getFile()) == gateway.OriginalFileWrapper:
                id = ann.getFile().getId()
                break
    return id


def processed_data_project_view(processed_list):
    d1 = datetime.strptime("1/1/2000 1:30 PM", "%m/%d/%Y %I:%M %p")
    d2 = datetime.strptime("1/1/2024 4:50 AM", "%m/%d/%Y %I:%M %p")
    df = pd.DataFrame(
        [[random_date(d1, d2), i] for i in processed_list],
        columns=["Date", "Dataset_ID"],
    )
    return df


def get_originalFile_id_by_image_id(dataset):
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


def fig_mip(mip_X, mip_Y, mip_Z, title):
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=("MIP X axis", "MIP Y axis", "MIP Z axis"),
    )
    fig = fig.add_trace(mip_X.data[0], row=1, col=1)
    fig = fig.add_trace(mip_Y.data[0], row=1, col=2)
    fig = fig.add_trace(mip_Z.data[0], row=2, col=1)
    fig = fig.update_layout(title_text=title, coloraxis=dict(colorscale="hot"))
    return fig


def mip_graphs(
    x0: int, xf: int, y0: int, yf: int, z: int, stack: Union[np.array, list]
):
    image_bead = stack[:, y0:yf, x0:xf]
    z_ima = stack[z, y0:yf, x0:xf]
    image_x = np.max(image_bead, axis=2)
    image_y = np.max(image_bead, axis=1)
    image_x = image_x / image_x.max()
    image_y = image_y / image_y.max()
    image_z = z_ima / z_ima.max()
    mip_x = px.imshow(
        image_x,
        zmin=image_x.min(),
        zmax=image_x.max(),
        color_continuous_scale="hot",
    )
    mip_y = px.imshow(
        image_y,
        zmin=image_y.min(),
        zmax=image_y.max(),
        color_continuous_scale="hot",
    )
    mip_z = px.imshow(
        image_z,
        zmin=image_z.min(),
        zmax=image_z.max(),
        color_continuous_scale="hot",
    )
    return mip_x, mip_y, mip_z


def crop_bead_index(bead, min_dist, stack):
    x = bead["center_x"].values[0]
    y = bead["center_y"].values[0]
    z = bead["center_z"].values[0]
    x0 = max(0, x - min_dist)
    y0 = max(0, y - min_dist)
    xf = min(stack.shape[2], x + min_dist)
    yf = min(stack.shape[1], y + min_dist)
    return x0, xf, y0, yf, z


def image_3d_chart(image_bead):
    image_bead = image_bead / image_bead.max()
    lz, ly, lx = image_bead.shape
    Z, Y, X = np.mgrid[:lz, :ly, :lx]
    fig = go.Figure(
        data=go.Volume(
            x=Z.flatten(),
            y=Y.flatten(),
            z=X.flatten(),
            value=image_bead.flatten(),
            isomin=0,
            isomax=1,
            opacity=0.3,
            surface_count=25,
        )
    )
    fig = fig.update_layout(
        scene_xaxis_showticklabels=False,
        scene_yaxis_showticklabels=False,
        scene_zaxis_showticklabels=False,
    )
    return fig
