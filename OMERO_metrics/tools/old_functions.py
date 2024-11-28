# from OMERO_metrics.tools.data_preperation import (
#     get_table_original_file_id,
# )
# import collections
# import pandas as pd
# import omero
#
#
# def get_key_values(var: FieldIlluminationDataset.output) -> pd.DataFrame:
#     data_dict = var.key_measurements.__dict__
#     col = var.key_measurements.channel_name
#     data_dict = [
#         [key] + value
#         for key, value in data_dict.items()
#         if isinstance(value, list)
#         and key
#         not in [
#             "name",
#             "description",
#             "data_reference",
#             "linked_references",
#             "channel_name",
#         ]
#     ]
#     df = pd.DataFrame(data_dict, columns=["Measurements"] + col)
#     return df
#
# def _load_image_intensities(image: ImageWrapper) -> np.ndarray:
#     return omero_tools.get_image_intensities(image).transpose((2, 0, 3, 4, 1))
#
#
# def get_project_data(
#     collections: mm_schema.MetricsDatasetCollection,
# ) -> pd.DataFrame:
#     data = []
#     for dataset in collections.datasets:
#         data.append(
#             [
#                 dataset.__class__.__name__,
#                 dataset.data_reference.omero_object_type,
#                 dataset.data_reference.omero_object_id,
#                 dataset.processed,
#                 dataset.acquisition_datetime,
#             ]
#         )
#     df = pd.DataFrame(
#         data,
#         columns=[
#             "Analysis_type",
#             "Omero_object_type",
#             "Omero_object_id",
#             "Processed",
#             "Acquisition_datetime",
#         ],
#     )
#     return df
#
#
# def get_dataset_by_id(
#     collections: mm_schema.MetricsDatasetCollection, dataset_id
# ) -> mm_schema.MetricsDataset:
#     try:
#         dataset = [
#             i
#             for i in collections.datasets
#             if i.data_reference.omero_object_id == dataset_id
#         ][0]
#         return dataset
#     except IndexError:
#         return None
#
#
# def get_images_intensity_profiles(
#     dataset: mm_schema.MetricsDataset,
# ) -> pd.DataFrame:
#     data = []
#     for i, j in zip(
#         dataset.input_data["field_illumination_image"],
#         dataset.output["intensity_profiles"],
#     ):
#         data.append(
#             [
#                 i["data_reference"]["omero_object_id"],
#                 j["data_reference"]["omero_object_id"],
#                 i["shape_c"],
#             ]
#         )
#     df = pd.DataFrame(
#         data,
#         columns=["Field_illumination_image", "Intensity_profiles", "Channel"],
#     )
#     return df
#
#
# def get_all_intensity_profiles(conn, data_df):
#     df_01 = pd.DataFrame()
#     for i, row in data_df.iterrows():
#         file_id = (
#             conn.getObject("FileAnnotation", row.Intensity_profiles)
#             .getFile()
#             .getId()
#         )
#         data = get_table_original_file_id(conn, str(file_id))
#         for j in range(row.Channel):
#             regx_find = f"ch0{j}"
#             ch = i + j
#             regx_repl = f"Ch0{ch}"
#             data.columns = data.columns.str.replace(regx_find, regx_repl)
#         df_01 = pd.concat([df_01, data], axis=1)
#     return df_01
#
#
# def get_table_file_id(conn, file_annotation_id):
#     file_id = (
#         conn.getObject("FileAnnotation", file_annotation_id).getFile().getId()
#     )
#     ctx = conn.createServiceOptsDict()
#     ctx.setOmeroGroup("-1")
#     r = conn.getSharedResources()
#     t = r.openTable(omero.model.OriginalFileI(file_id), ctx)
#     data_buffer = collections.defaultdict(list)
#     heads = t.getHeaders()
#     target_cols = range(len(heads))
#     index_buffer = []
#     num_rows = t.getNumberOfRows()
#     for start in range(0, num_rows):
#         data = t.read(target_cols, start, start)
#         for col in data.columns:
#             data_buffer[col.name] += col.values
#         index_buffer += data.rowNumbers
#     df = pd.DataFrame.from_dict(data_buffer)
#     df.index = index_buffer[0 : len(df)]
#     return df
#
# import yaml
# import omero.gateway as gateway
# from datetime import datetime, timedelta
# from random import randrange
# import collections
# import omero
# import plotly.express as px
# import numpy as np
# from plotly.subplots import make_subplots
# import plotly.graph_objects as go
# import pandas as pd
# from typing import Union
#
# PROFILES_COLORS = {
#     "center_vertical": "red",
#     "center_horizontal": "blue",
#     "leftBottom_to_rightTop": "green",
#     "leftTop_to_rightBottom": "yellow",
# }
#
#
# # This function is no longer needed
# def get_intensity_profile(image):
#     image = image[0, 0, :, :, 0] / 255
#     image_flipped = np.flip(image, axis=1)
#     rb = image[:, -1]
#     lb = image[:, 0]
#     dr = np.fliplr(image).diagonal()
#     dl = np.fliplr(image_flipped).diagonal()
#     df = pd.DataFrame(
#         {
#             "Right Bottom": rb,
#             "Left Bottom": lb,
#             "Diagonal Right": dr,
#             "Diagonal Left": dl,
#         }
#     )
#     return df
#
#
# def add_rect_rois(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
#     for i, row in df.iterrows():
#         fig.add_shape(
#             go.layout.Shape(
#                 type="rect",
#                 x0=row.X,
#                 y0=row.Y,
#                 x1=row.X + row.W,
#                 y1=row.Y + row.H,
#                 xref="x",
#                 yref="y",
#                 line=dict(
#                     color="RoyalBlue",
#                     width=3,
#                 ),
#             )
#         )
#     return fig
#
#
# def add_line_rois_trace(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
#     for i, row in df.iterrows():
#         data = pd.DataFrame(
#             dict(
#                 x=np.array(range(int(row.X1), int(row.X2))),
#                 y=np.array(range(int(row.Y1), int(row.Y2))),
#             )
#         )
#         fig.add_trace(
#             go.Scatter(x=data.x, y=data.y, mode="lines", name=str(row.NAME))
#         )
#     return fig
#
#
# def add_line_rois(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
#     for i, row in df.iterrows():
#         fig.add_shape(
#             go.layout.Shape(
#                 type="line",
#                 name=str(row.NAME),
#                 showlegend=True,
#                 editable=True,
#                 x0=row.X1,
#                 y0=row.Y1,
#                 x1=row.X2,
#                 y1=row.Y2,
#                 xref="x",
#                 yref="y",
#                 line=dict(
#                     color="Green",
#                     width=1,
#                     dash="dot",
#                 ),
#             )
#         )
#     return fig
#
#
# def add_point_rois(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
#     fig.add_trace(
#         go.Scatter(
#             x=df.X,
#             y=df.Y,
#             mode="markers",
#             customdata=df.ROI_NAME,
#             hovertemplate="%{customdata}",
#         )
#     )
#     return fig
#
#
# def get_rois_omero(result):
#     shapes_line = {}
#     shapes_rectangle = {}
#     shapes_point = {}
#     for roi in result.rois:
#         for s in roi.copyShapes():
#             shape = {"id": s.getId().getValue()}
#             # shape["theT"] = s.getTheT().getValue()
#             # shape["theZ"] = s.getTheZ().getValue()
#             if s.getTextValue():
#                 shape["textValue"] = s.getTextValue().getValue()
#             if s.__class__.__name__ == "RectangleI":
#                 shape["type"] = "Rectangle"
#                 shape["x"] = s.getX().getValue()
#                 shape["y"] = s.getY().getValue()
#                 shape["w"] = s.getWidth().getValue()
#                 shape["h"] = s.getHeight().getValue()
#                 shapes_rectangle[s.getId().getValue()] = shape
#             elif s.__class__.__name__ == "LineI":
#                 shape["type"] = "Line"
#                 shape["x1"] = s.getX1().getValue()
#                 shape["x2"] = s.getX2().getValue()
#                 shape["y1"] = s.getY1().getValue()
#                 shape["y2"] = s.getY2().getValue()
#
#                 shapes_line[s.getId().getValue()] = shape
#             elif s.__class__.__name__ == "PointI":
#                 shape["type"] = "Point"
#                 shape["x"] = s.getX().getValue()
#                 shape["y"] = s.getY().getValue()
#                 # shape['z'] = s.getZ().getValue()
#                 shape["channel"] = s.getTheC().getValue()
#                 shapes_point[s.getId().getValue()] = shape
#             elif s.__class__.__name__ == "PolygonI":
#                 continue
#     return shapes_rectangle, shapes_line, shapes_point
#
#
# def add_colors_intensity_profile(df: pd.DataFrame) -> pd.DataFrame:
#     df.loc[:, "color"] = [PROFILES_COLORS[i] for i in df.NAME]
#     return df
#
#
# def get_info_roi_points(shape_dict):
#     data = [
#         [key, int(value["x"]), int(value["y"]), int(value["channel"])]
#         for key, value in shape_dict.items()
#     ]
#     df = pd.DataFrame(data, columns=["ROI", "X", "Y", "C"])
#     return df
#
#
# def get_info_roi_lines(shape_dict):
#     data = [
#         [
#             key,
#             value["x1"],
#             value["y1"],
#             value["x2"],
#             value["y2"],
#             value["textValue"],
#         ]
#         for key, value in shape_dict.items()
#     ]
#     df = pd.DataFrame(data, columns=["ROI", "X1", "Y1", "X2", "Y2", "NAME"])
#     return df
#
#
# def get_info_roi_rectangles(shape_dict):
#     data = [
#         [
#             key,
#             value["x"],
#             value["y"],
#             value["w"],
#             value["h"],
#             value["textValue"],
#         ]
#         for key, value in shape_dict.items()
#     ]
#     df = pd.DataFrame(data, columns=["ROI", "X", "Y", "W", "H", "NAME"])
#     return df
#
#
# def get_dataset_ids_lists(project):
#     """
#     Get the processed and unprocessed dataset ids for a project
#     """
#     processed_datasets = []
#     unprocessed_datasets = []
#     for dataset in project.listChildren():
#         try:
#             dataset.getAnnotation().getNs()
#             processed_datasets.append(dataset.getId())
#         except AttributeError:
#             unprocessed_datasets.append(dataset.getId())
#     return processed_datasets, unprocessed_datasets
#
#
# def get_image_list_by_dataset_id(conn, dataset_id):
#     """
#     Get the list of images for a dataset
#     """
#     dataset = conn.getObject("Dataset", dataset_id)
#     images = []
#     for image in dataset.listChildren():
#         images.append(image.getId())
#     return images
#
#
# def get_dataset_map_annotation(dataset_wrapper):
#     """
#     Get the mapAnnotation for a dataset
#     """
#     df = {}
#     try:
#         for i in dataset_wrapper.listAnnotations():
#             if "FieldIlluminationKeyValues" in i.getNs():
#                 table = dict(i.getValue())
#                 df = pd.DataFrame(table.items(), columns=["Key", "Value"])
#                 break
#             elif "PSFBeadsKeyValues" in i.getNs():
#                 table = dict(i.getValue())
#                 df = pd.DataFrame(table.items(), columns=["Key", "Value"])
#                 break
#         return df
#     except AttributeError:
#         return df
#
#
# def read_config_from_file_ann(file_annotation):
#     return yaml.load(
#         file_annotation.getFileInChunks().__next__().decode(),
#         Loader=yaml.SafeLoader,
#     )
#
#
# def get_file_annotation_project(project_wrapper):
#     study_config = None
#     for ann in project_wrapper.listAnnotations():
#         if (
#             type(ann) == gateway.FileAnnotationWrapper
#             and ann.getFile().getName() == "study_config.yaml"
#         ):
#             study_config = read_config_from_file_ann(ann)
#     return study_config
#
#
# def get_analysis_type(project_wrapper):
#     study_config = get_file_annotation_project(project_wrapper)
#     try:
#         analysis_type = next(iter(study_config["analysis"]))
#     except KeyError:
#         analysis_type = None
#     return analysis_type
#
#
# def random_date(start, end):
#     """
#     This function will return a random datetime between two datetime
#     objects.
#     """
#     delta = end - start
#     int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
#     random_second = randrange(int_delta)
#     return start + timedelta(seconds=random_second)
#
#
# def get_table_original_file_id(conn, file_id):
#     ctx = conn.createServiceOptsDict()
#     ctx.setOmeroGroup("-1")
#     r = conn.getSharedResources()
#     t = r.openTable(omero.model.OriginalFileI(file_id), ctx)
#     data_buffer = collections.defaultdict(list)
#     heads = t.getHeaders()
#     target_cols = range(len(heads))
#     index_buffer = []
#     num_rows = t.getNumberOfRows()
#     for start in range(0, num_rows):
#         data = t.read(target_cols, start, start)
#         for col in data.columns:
#             data_buffer[col.name] += col.values
#         index_buffer += data.rowNumbers
#     df = pd.DataFrame.from_dict(data_buffer)
#     df.index = index_buffer[0 : len(df)]
#     return df
#
#
# def get_original_file_id(dataset):
#     dataset_id = None
#     for ann in dataset.listAnnotations():
#         if type(ann) == gateway.FileAnnotationWrapper:
#             if type(ann.getFile()) == gateway.OriginalFileWrapper:
#                 dataset_id = ann.getFile().getId()
#                 break
#     return dataset_id
#
#
# def processed_data_project_view(processed_list):
#     d1 = datetime.strptime("1/1/2000 1:30 PM", "%m/%d/%Y %I:%M %p")
#     d2 = datetime.strptime("1/1/2024 4:50 AM", "%m/%d/%Y %I:%M %p")
#     df = pd.DataFrame(
#         [[random_date(d1, d2), i] for i in processed_list],
#         columns=["Date", "Dataset_ID"],
#     )
#     return df
#
#
# def get_original_file_id_by_image_id(dataset):
#     list_file = []
#     for ann in dataset.listAnnotations():
#         if type(ann) == gateway.FileAnnotationWrapper:
#             if type(ann.getFile()) == gateway.OriginalFileWrapper:
#                 list_file.append(
#                     [ann.getFile().getId(), ann.getFile().getName()]
#                 )
#     return list_file
#
#
# def get_intensity_map_image(image_name, list_file):
#     for file_id, name in list_file:
#         if image_name in name:
#             return file_id
#         else:
#             return None
#
# def image_3d_chart(image_bead):
#     image_bead = image_bead / image_bead.max()
#     lz, ly, lx = image_bead.shape
#     z, y, x = np.mgrid[:lz, :ly, :lx]
#     fig = go.Figure(
#         data=go.Volume(
#             x=z.flatten(),
#             y=y.flatten(),
#             z=x.flatten(),
#             value=image_bead.flatten(),
#             isomin=0,
#             isomax=1,
#             opacity=0.3,
#             # surface_count=25,
#         )
#     )
#     fig = fig.update_layout(
#         scene_xaxis_showticklabels=False,
#         scene_yaxis_showticklabels=False,
#         scene_zaxis_showticklabels=False,
#     )
#     return fig
