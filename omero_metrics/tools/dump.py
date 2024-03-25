import ast
import logging
from dataclasses import fields
from typing import Union

from microscopemetrics_schema.datamodel import microscopemetrics_schema as mm_schema
from omero.gateway import BlitzGateway, DatasetWrapper, ImageWrapper, ProjectWrapper

import omero_tools

logger = logging.getLogger(__name__)

SHAPE_TO_FUNCTION = {
    "Point": omero_tools.create_shape_point,
    "Line": omero_tools.create_shape_line,
    "Rectangle": omero_tools.create_shape_rectangle,
    "Ellipse": omero_tools.create_shape_ellipse,
    "Polygon": omero_tools.create_shape_polygon,
    "Mask": omero_tools.create_shape_mask,
}

SHAPE_TYPE_TO_FUNCTION = {
    "point": omero_tools.create_shape_point,
    "line": omero_tools.create_shape_line,
    "rectangles": omero_tools.create_shape_rectangle,
    "ellipses": omero_tools.create_shape_ellipse,
    "polygons": omero_tools.create_shape_polygon,
    "masks": omero_tools.create_shape_mask,
}


def _append_reference(obj, ref):
    obj.data_uri = ref["data_uri"]
    obj.omero_host = ref["omero_host"],
    obj.omero_port = ref["omero_port"],
    obj.omero_object_type = ref["omero_object_type"],
    obj.omero_object_id = ref["omero_object_id"]


def dump_project(
    conn: BlitzGateway,
    project: mm_schema.MetricsDatasetCollection,
    demo_mode: bool = True,
) -> ProjectWrapper:
    omero_project = omero_tools.create_project(
        conn=conn,
        name=project.name,
        description=project.description
    )
    _append_reference(project, omero_tools.get_ref_from_object(omero_project))

    for dataset in project.datasets:
        dump_dataset(
            conn=conn,
            dataset=dataset,
            target_project=omero_project,
            demo_mode=demo_mode
        )

    return omero_project


def dump_dataset(
    conn: BlitzGateway,
    dataset: mm_schema.MetricsDataset,
    target_project: ProjectWrapper = None,
    append_to_existing: bool = False,
    as_table: bool = False,
    demo_mode: bool = True,
) -> DatasetWrapper:
    if append_to_existing or as_table:
        logger.error(
            f"Dataset {dataset.class_name} cannot be appended to existing or dumped as table. Skipping dump."
        )
    if target_project is None:
        try:
            target_project = omero_tools.get_omero_obj_from_ref(
                conn=conn,
                ref={
                    "omero_object_type": dataset.microscope.omero_object_type,
                    "omero_object_id": dataset.microscope.omero_object_id,
                }
            )
        except AttributeError:
            logger.error(
                f"Dataset {dataset.name} must be linked to a project/microscope. No project provided."
            )
            return None

    omero_dataset = omero_tools.create_dataset(
        conn=conn,
        dataset_name=dataset.name,
        description=dataset.description,
        project=target_project,
    )
    _append_reference(dataset, omero_tools.get_ref_from_object(omero_dataset))

    for input_field in fields(dataset.input):
        input_element = getattr(dataset.input, input_field.name)
        if isinstance(input_element, mm_schema.Image):
            dump_image(
                conn=conn,
                image=input_element,
                target_dataset=omero_dataset,
                append_to_existing=append_to_existing,
                as_table=as_table,
            )
        elif all(isinstance(i_e, mm_schema.Image) for i_e in input_element):
            for image in input_element:
                dump_image(
                    conn=conn,
                    image=image,
                    target_dataset=omero_dataset,
                    append_to_existing=append_to_existing,
                    as_table=as_table,
                )
        else:
            continue

    if demo_mode:
        # This mode is meant to load into OMERO only the input images
        # If this is the purpose, we can stop here
        return omero_dataset

    else:
        raise NotImplementedError("The function is not yet implemented for the full dataset dump")


def dump_image(
    conn: BlitzGateway,
    image: mm_schema.Image,
    target_dataset: DatasetWrapper,
    append_to_existing: bool = False,
    as_table: bool = False,
):
    if append_to_existing or as_table:
        logger.error(
            f"Image {image.class_name} cannot be appended to existing or dumped as table. Skipping dump."
        )
    if not isinstance(target_dataset, DatasetWrapper):
        logger.error(
            f"Image {image} must be linked to a dataset. {target_dataset} object provided is not a dataset."
        )
        return None
    if not isinstance(image, mm_schema.Image):
        logger.error(f"Invalid image object provided for {image}. Skipping dump.")
        return None
    source_image_id = None
    try:
        source_image_id = image.source_images.omero_object_id
    except AttributeError:
        logger.info(f"No source image id provided for {image.name}")

    omero_image = omero_tools.create_image_from_numpy_array(
        conn=conn,
        data=image.array_data,
        image_name=image.name,
        image_description=image.description,
        channel_labels=[ch.name for ch in image.channel_series.channels],
        dataset=target_dataset,
        source_image_id=source_image_id,
        channels_list=None,
        force_whole_planes=False,
    )
    _append_reference(image, omero_tools.get_ref_from_object(omero_image))

    return omero_image


def dump_roi(
    conn: BlitzGateway,
    roi: mm_schema.Roi,
    target_image: ImageWrapper,
    append_to_existing: bool = False,
    as_table: bool = False,
):
    if append_to_existing or as_table:
        logger.error(
            f"ROI {roi.class_name} cannot be appended to existing or dumped as table. Skipping dump."
        )
    if not isinstance(target_image, ImageWrapper):
        logger.error(
            f"ROI {roi.label} must be linked to an image. {target_image} object provided is not an image."
        )
        return None
    shapes = []
    for shape_field in fields(roi):
        if shape_field.name in SHAPE_TYPE_TO_FUNCTION:
            shapes += [SHAPE_TYPE_TO_FUNCTION[shape_field.name](shape)
                       for shape in getattr(roi, shape_field.name)]

    omero_roi = omero_tools.create_roi(
        conn=conn,
        image=target_image,
        shapes=shapes,
        name=roi.label,
        description=roi.description,
    )
    _append_reference(roi, omero_tools.get_ref_from_object(omero_roi))


def dump_tag(
    conn: BlitzGateway,
    tag: mm_schema.Tag,
    target_object: Union[ImageWrapper, DatasetWrapper, ProjectWrapper],
    append_to_existing: bool = False,
    as_table: bool = False,
):
    if append_to_existing or as_table:
        logger.error(
            f"Tag {tag.class_name} cannot be appended to existing or dumped as table. Skipping dump."
        )

    omero_tag = omero_tools.create_tag(
        conn=conn,
        tag_name=tag.name,
        tag_description=tag.description,
        omero_object=target_object,
    )
    _append_reference(tag, omero_tools.get_ref_from_object(omero_tag))

    return omero_tag


def dump_key_value(
    conn: BlitzGateway,
    key_values: mm_schema.KeyValues,
    target_object: Union[ImageWrapper, DatasetWrapper, ProjectWrapper],
    append_to_existing: bool = False,
    as_table: bool = False,
):
    if append_to_existing or as_table:
        logger.error(
            f"KeyValues {key_values.class_name} cannot yet be appended to existing or dumped as table. Skipping dump."
        )
    omero_key_value = omero_tools.create_key_value(
        conn=conn,
        annotation=key_values._as_dict,
        omero_object=target_object,
        annotation_name=key_values.name,
        annotation_description=key_values.description,
        namespace=key_values.class_model_uri,
    )
    _append_reference(key_values, omero_tools.get_ref_from_object(omero_key_value))

    return key_values


def _eval(s):
    try:
        ev = ast.literal_eval(s)
        return ev
    except ValueError:
        corrected = "'" + s + "'"
        ev = ast.literal_eval(corrected)
        return ev


def _eval_types(table: mm_schema.TableAsDict):
    for column in table.columns.values():
        breakpoint()
        column.values = [_eval(v) for v in column.values]
    return table


def dump_table(
    conn: BlitzGateway,
    table: mm_schema.Table,
    omero_object: Union[ImageWrapper, DatasetWrapper, ProjectWrapper],
    append_to_existing: bool = False,
    as_table: bool = False,
):
    if isinstance(table, mm_schema.TableAsDict):
        # linkML if casting everything as a string and we have to evaluate it back
        columns = {c.name: [_eval(v) for v in c.values] for c in table.columns.values()}
        return omero_tools.create_table(
            conn=conn,
            table=columns,
            table_name=table.name,
            omero_object=omero_object,
            table_description=table.description,
            namespace=table.class_model_uri,
        )
    elif isinstance(table, mm_schema.TableAsPandasDF):
        return omero_tools.create_table(
            conn=conn,
            table=table.df,
            table_name=table.name,
            omero_object=omero_object,
            table_description=table.description,
            namespace=table.class_model_uri,
        )
    else:
        logger.error(f"Unsupported table type for {table.name}: {table.class_name}")
        return None


def dump_comment(
    conn: BlitzGateway,
    comment: mm_schema.Comment,
    omero_object: Union[ImageWrapper, DatasetWrapper, ProjectWrapper],
    append_to_existing: bool = False,
    as_table: bool = False,
):
    # TODO: we should dump details on the comments. Like authors, date, etc.
    if append_to_existing or as_table:
        logger.error(
            f"Comment {comment.class_name} cannot be appended to existing or dumped as table. Skipping dump."
        )
    return omero_tools.create_comment(
        conn=conn,
        comment_text=comment.text,
        omero_object=omero_object,
        namespace=comment.class_model_uri,
    )
