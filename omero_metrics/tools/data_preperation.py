import pandas as pd
import plotly.graph_objs as go
import numpy as np


def get_intensity_profile(imaaa):
    imaaa= imaaa[0, 0, :, :, 0] / 255
    imaa_fliped = np.flip(imaaa, axis=1)
    rb = imaaa[:,-1]
    lb= imaaa[:,0]
    dr = np.fliplr(imaaa).diagonal()
    dl = np.fliplr(imaa_fliped).diagonal()
    df = pd.DataFrame({"Right Bottom": rb, "Left Bottom": lb, "Diagonal Right": dr, "Diagonal Left": dl})
    return df

def add_rois(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
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


def add_profile_rois(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
    for i, row in df.iterrows():
        fig.add_shape(
            go.layout.Shape(
                type="line",
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



def get_rois_omero(result):
    shapes_line = {}
    shapes_rectangle = {}
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
            elif s.__class__.__name__ == "PolygonI":
                continue
    return shapes_rectangle, shapes_line


def get_info_roi_lines(shape_dict):
    data = [
        [key, value["x1"], value["y1"], value["x2"], value["y2"]]
        for key, value in shape_dict.items()
    ]
    df = pd.DataFrame(data, columns=["ROI", "X1", "Y1", "X2", "Y2"])
    return df


def get_info_roi_rectangles(shape_dict):
    data = [
        [key, value["x"], value["y"], value["w"], value["h"]] for key, value in shape_dict.items()
    ]
    df = pd.DataFrame(data, columns=["ROI", "X", "Y", "W", "H"])
    return df



def get_dataset_ids_lists(conn, project_id):
    """
    Get the processed and unprocessed dataset ids for a project
    """
    processed_datasets = []
    unprocessed_datasets = []
    project = conn.getObject("Project", project_id)
    for dataset in project.listChildren():
        try:
            dataset.getAnnotation().getNs()
            processed_datasets.append(dataset.getId())
        except AttributeError:
            unprocessed_datasets.append(dataset.getId())
    return processed_datasets, unprocessed_datasets



def get_dataset_mapAnnotation(conn, dataset_id):
    """
    Get the mapAnnotation for a dataset
    """
    dataset = conn.getObject("Dataset", dataset_id)
    try:
        for i in dataset.listAnnotations():
            if "FieldIlluminationKeyValues" in i.getNs():
                table = dict(i.getValue())
                df = pd.DataFrame(table.items(), columns=["Key", "Value"])
                break
        return df
    except:
        return {}