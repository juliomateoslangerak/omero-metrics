import ast
import contextlib
import logging
import tempfile
from dataclasses import fields
from typing import Union

import pandas as pd
from linkml_runtime.dumpers import YAMLDumper
from microscopemetrics_schema.datamodel import (
    microscopemetrics_schema as mm_schema,
)
from omero.gateway import (
    BlitzGateway,
    DatasetWrapper,
    ImageWrapper,
    ProjectWrapper,
    ExperimenterGroupWrapper,
)

from OMERO_metrics.tools import omero_tools

logger = logging.getLogger(__name__)

SHAPE_TO_FUNCTION = {
    "Point": omero_tools.create_shape_point,
    "Line": omero_tools.create_shape_line,
    "Rectangle": omero_tools.create_shape_rectangle,
    "Ellipse": omero_tools.create_shape_ellipse,
    "Polygon": omero_tools.create_shape_polygon,
    "Mask": omero_tools.create_shape_mask,
}


def dump_microscope(
    conn: BlitzGateway,
    microscope: mm_schema.Microscope,
    target_group: ExperimenterGroupWrapper = None,
) -> ExperimenterGroupWrapper:
    """
    This function is dumping the microscope metadata into an existing Group in OMERO.
    :param conn:
    :param microscope:
    :param target_group:
    :return:
    """
    if target_group is None:
        if microscope.data_reference:
            omero_group = omero_tools.get_omero_obj_from_mm_obj(
                conn=conn, mm_obj=microscope
            )
        else:
            logger.error(
                f"Microscope {microscope.name}: a target group must be provided"
            )
            return None
    else:
        if not isinstance(target_group, ExperimenterGroupWrapper):
            logger.error(
                f"Microscope {microscope.name} must be linked to a group. {target_group} object provided is not a group."
            )
            return None
        if (
            microscope.data_reference
            and microscope.data_reference.omero_object_id
            != target_group.getId()
        ):
            logger.warning(
                f"Microscope {microscope.name} is going to be linked to a different OMERO group."
            )
        omero_group = target_group
        microscope.data_reference = omero_tools.get_ref_from_object(
            omero_group
        )

    omero_tools.create_key_value(
        conn=conn,
        annotation=microscope._as_dict,
        omero_object=omero_group,
        annotation_name=microscope.name,
        annotation_description=microscope.description,
        namespace=microscope.class_class_curie,
    )

    return omero_group


def dump_project(
    conn: BlitzGateway,
    project: mm_schema.MetricsDatasetCollection,
    target_project: ProjectWrapper = None,
    dump_input_images: bool = False,
    dump_analysis: bool = True,
    dump_as_project_file_annotation: bool = True,
    dump_as_dataset_file_annotation: bool = False,
) -> ProjectWrapper:
    if target_project is None:
        if project.data_reference:
            omero_project = omero_tools.get_omero_obj_from_mm_obj(
                conn=conn, mm_obj=project
            )
        else:
            omero_project = omero_tools.create_project(
                conn=conn, name=project.name, description=project.description
            )
            project.data_reference = omero_tools.get_ref_from_object(
                omero_project
            )
    else:
        if not isinstance(target_project, ProjectWrapper):
            logger.error(
                f"Project {project.name} must be linked to a project. {target_project} object provided is not a project."
            )
            return None
        if project.omero_object_id != target_project.getId():
            logger.warning(
                f"Project {project.name} is going to be linked to a different OMERO project."
            )
        omero_project = target_project
        project.data_reference = omero_tools.get_ref_from_object(omero_project)

    for dataset in project.datasets:
        dump_dataset(
            conn=conn,
            dataset=dataset,
            target_project=omero_project,
            dump_input_images=dump_input_images,
            dump_analysis=dump_analysis,
            dump_as_project_file_annotation=dump_as_project_file_annotation,
            dump_as_dataset_file_annotation=dump_as_dataset_file_annotation,
        )

    return omero_project


def _remove_unsupported_types(
    data_obj: Union[
        mm_schema.MetricsInputData,
        mm_schema.MetricsInputParameters,
        mm_schema.MetricsOutput,
    ]
):
    def _remove(_attr):
        if isinstance(_attr, mm_schema.Image):
            _attr.array_data = None
        elif isinstance(_attr, mm_schema.Table):
            _attr.table_data = None
        elif isinstance(_attr, mm_schema.KeyMeasurements):
            _attr.table_data = None
        elif isinstance(_attr, mm_schema.Roi):
            if _attr.masks:
                for m in _attr.masks:
                    _remove(m.mask)

    with contextlib.suppress(TypeError):
        for field in fields(data_obj):
            try:
                _attr = getattr(data_obj, field.name)
                if isinstance(_attr, list):
                    [_remove(i) for i in _attr]
                else:
                    _remove(_attr)
            except AttributeError:
                continue


def _dump_mm_dataset_as_file_annotation(
    conn: BlitzGateway,
    mm_dataset: mm_schema.MetricsDataset,
    target_omero_obj: Union[
        ProjectWrapper,
        DatasetWrapper,
        list[Union[ProjectWrapper, DatasetWrapper]],
    ],
):
    # We need to remove the data on the numpy and pandas data objects as they cannot be serialized by linkml
    _remove_unsupported_types(mm_dataset.input_data)
    _remove_unsupported_types(mm_dataset.input_parameters)
    if mm_dataset.output:
        _remove_unsupported_types(mm_dataset.output)

    dumper = YAMLDumper()

    with tempfile.NamedTemporaryFile(
        prefix=f"{mm_dataset.class_name}_",
        suffix=".yaml",
        mode="w",
        delete=False,
    ) as f:
        f.write(dumper.dumps(mm_dataset))
        f.close()
        file_ann = omero_tools.create_file(
            conn=conn,
            file_path=f.name,
            omero_object=target_omero_obj,
            file_description=mm_dataset.description,
            namespace=mm_dataset.class_class_curie,
            mimetype="application/yaml",
        )

    return file_ann


def dump_dataset(
    conn: BlitzGateway,
    dataset: mm_schema.MetricsDataset,
    target_project: ProjectWrapper = None,
    dump_input_images: bool = False,
    dump_analysis: bool = True,
    dump_as_project_file_annotation: bool = True,
    dump_as_dataset_file_annotation: bool = False,
) -> DatasetWrapper:
    print(
        "-------------------------here 1--------------------------------------"
    )
    if dataset.data_reference:
        print(
            "-------------------------here 2--------------------------------------"
        )
        try:
            omero_dataset = omero_tools.get_omero_obj_from_mm_obj(
                conn=conn, mm_obj=dataset
            )
            logger.info(f"Retrieving dataset {dataset.name} from OMERO")
        except Exception as e:
            logger.error(
                f"Dataset {dataset.name} could not be retrieved from OMERO: {e}"
            )
            raise e
    else:
        print(
            "-------------------------here 3--------------------------------------"
        )
        if target_project is None:
            logger.warning(
                f"Creating new dataset {dataset.name} in OMERO"
                f"Do target project was provided and an orphan dataset will be created."
            )
        elif not isinstance(target_project, ProjectWrapper):
            logger.error(
                f"Dataset {dataset.name} must be linked to a project. {target_project} object provided is not a project."
            )
            return None
        else:
            logger.info(f"Creating new dataset {dataset.name} in OMERO")

        omero_dataset = omero_tools.create_dataset(
            conn=conn,
            dataset_name=dataset.name,
            description=dataset.description,
            project=target_project,
        )
        dataset.data_reference = omero_tools.get_ref_from_object(omero_dataset)

    if dump_input_images:
        for input_field in fields(dataset.input_data):
            input_element = getattr(dataset.input_data, input_field.name)
            if isinstance(input_element, mm_schema.Image):
                dump_image(
                    conn=conn,
                    image=input_element,
                    target_dataset=omero_dataset,
                )
            elif isinstance(input_element, list) and all(
                isinstance(i_e, mm_schema.Image) for i_e in input_element
            ):
                for image in input_element:
                    dump_image(
                        conn=conn,
                        image=image,
                        target_dataset=omero_dataset,
                    )
            else:
                continue

    if dump_analysis:
        print(
            "-------------------------here 4--------------------------------------"
        )
        if dataset.processed:
            if dataset.output is not None:
                print(
                    "-------------------------here 4.1--------------------------------------"
                )

                _dump_analysis_metadata(dataset, omero_dataset)

                print(
                    "-------------------------here 4.2--------------------------------------"
                )
                _dump_dataset_output(dataset.output, omero_dataset)
            else:
                print(
                    "-------------------------here 4.3--------------------------------------"
                )
                logger.error(
                    f"Dataset {dataset.name} is processed but has no output. Skipping dump."
                )
        else:
            print(
                "-------------------------here 4.4--------------------------------------"
            )
            logger.warning(
                f"Dataset {dataset.name} is not processed. Skipping output dump."
            )

    target_objs = []
    if dump_as_dataset_file_annotation:
        print(
            "-------------------------here 5--------------------------------------"
        )
        target_objs.append(omero_dataset)
    if dump_as_project_file_annotation:
        print(
            "-------------------------here 6--------------------------------------"
        )
        target_objs.append(target_project)
    if target_objs:
        print(
            "-------------------------here 7--------------------------------------"
        )
        _dump_mm_dataset_as_file_annotation(
            conn=conn, mm_dataset=dataset, target_omero_obj=target_objs
        )
    print(
        "-------------------------here 8--------------------------------------"
    )
    return omero_dataset


def _dump_analysis_metadata(
    dataset: mm_schema.MetricsDataset,
    target_dataset: DatasetWrapper,
):
    logger.info(f"Dumping {dataset.class_name} to OMERO")
    if not isinstance(dataset, mm_schema.MetricsDataset):
        logger.error(
            f"Invalid dataset input object provided for {dataset}. Skipping dump."
        )
        return None

    input_metadata_data = _get_input_metadata(dataset.input_data)

    input_metadata_parameters = _get_input_metadata(dataset.input_parameters)

    output_metadata = _get_output_metadata(dataset.output)

    metadata = {
        **input_metadata_data,
        **input_metadata_parameters,
        **output_metadata,
    }

    omero_tools.create_key_value(
        conn=target_dataset._conn,
        annotation=metadata,
        omero_object=target_dataset,
        annotation_name=dataset.class_name,
        annotation_description=dataset.description,
        namespace=dataset.class_class_curie,
    )


def _get_input_metadata(
    input: Union[mm_schema.MetricsInputData, mm_schema.MetricsInputParameters],
) -> dict:
    metadata = {}
    for input_field in fields(input):
        input_element = getattr(input, input_field.name)
        if isinstance(input_element, mm_schema.Image):
            metadata[input_field.name] = input_element.name
        elif isinstance(input_element, list) and all(
            isinstance(i_e, mm_schema.Image) for i_e in input_element
        ):
            metadata[input_field.name] = [i_e.name for i_e in input_element]
        else:
            metadata[input_field.name] = str(input_element)

    return metadata


def dump_analysis_config():
    pass


def _get_output_metadata(
    dataset_output: mm_schema.MetricsOutput,
) -> dict:
    output_fields = {f.name for f in fields(mm_schema.MetricsOutput)}
    output_elements = {}
    for output_field in fields(dataset_output):
        if output_field.name not in output_fields:
            continue
        output_elements[output_field.name] = str(
            getattr(dataset_output, output_field.name)
        )

    return output_elements


def _dump_dataset_output(
    dataset_output: mm_schema.MetricsOutput,
    target_dataset: DatasetWrapper,
):
    logger.info(f"Dumping {dataset_output.class_name} to OMERO")
    if not isinstance(target_dataset, DatasetWrapper):
        logger.error(
            f"Dataset {dataset_output} must be linked to a dataset. {target_dataset} object provided is not a dataset."
        )
        return None
    if not isinstance(dataset_output, mm_schema.MetricsOutput):
        logger.error(
            f"Invalid dataset output object provided for {dataset_output}. Skipping dump."
        )
        return None
    conn = target_dataset._conn
    print(conn)
    for output_field in fields(dataset_output):
        output_element = getattr(dataset_output, output_field.name)
        if isinstance(output_element, mm_schema.MetricsObject):
            _dump_output_element(
                conn=conn,
                output_element=output_element,
                target_dataset=target_dataset,
            )
        elif isinstance(output_element, list) and all(
            isinstance(i, mm_schema.MetricsObject) for i in output_element
        ):
            for element in output_element:
                _dump_output_element(
                    conn=conn,
                    output_element=element,
                    target_dataset=target_dataset,
                )
        else:
            continue


def _dump_output_element(
    conn: BlitzGateway,
    output_element: mm_schema.MetricsObject,
    target_dataset: DatasetWrapper,
):

    if isinstance(output_element, mm_schema.Image):
        return dump_image(
            conn=conn,
            image=output_element,
            target_dataset=target_dataset,
        )
    elif isinstance(output_element, mm_schema.KeyValues):
        if isinstance(output_element, mm_schema.KeyMeasurements):
            return dump_key_measurement(
                conn=conn,
                key_measurement=output_element,
                # KeyMeasurements are linked to the dataset and project
                target_object=[target_dataset, target_dataset.getParent()],
            )
        else:
            return dump_key_values(
                conn=conn,
                key_values=output_element,
                target_object=target_dataset,
            )
    elif isinstance(output_element, mm_schema.Tag):
        return dump_tag(
            conn=conn,
            tag=output_element,
            target_objects=target_dataset,
        )
    elif isinstance(output_element, mm_schema.Table):
        return dump_table(
            conn=conn,
            table=output_element,
            target_object=target_dataset,
        )
    elif isinstance(output_element, mm_schema.Roi):
        return dump_roi(
            conn=conn,
            roi=output_element,
        )
    elif isinstance(output_element, mm_schema.Comment):
        return dump_comment(
            conn=conn,
            comment=output_element,
            target_object=target_dataset,
        )
    else:
        logger.error(
            f"{output_element.name} output could not be dumped to OMERO"
        )

    return None


def dump_image(
    conn: BlitzGateway,
    image: mm_schema.Image,
    target_dataset: DatasetWrapper,
):
    if not isinstance(target_dataset, DatasetWrapper):
        logger.error(
            f"Image {image} must be linked to a dataset. {target_dataset} object provided is not a dataset."
        )
        return None
    if not isinstance(image, mm_schema.Image):
        logger.error(
            f"Invalid image object provided for {image}. Skipping dump."
        )
        return None

    source_image_id = None
    try:
        # source_images is a list of DataReference objects.
        # For the purpose of adding to OMERO we only use the first image
        source_image_id = image.source_images[0].omero_object_id
    except IndexError:
        logger.info(f"No source image id provided for {image.name}")

    omero_image = omero_tools.create_image_from_numpy_array(
        conn=conn,
        data=image.array_data.transpose(
            (1, 4, 0, 2, 3)
        ),  # microscope-metrics order TZYXC -> OMERO order zctyx
        image_name=image.name,
        image_description=image.description,
        channel_labels=[ch.name for ch in image.channel_series.channels],
        dataset=target_dataset,
        source_image_id=source_image_id,
        channels_list=None,
        acquisition_datetime=image.acquisition_datetime,
        force_whole_planes=False,
    )
    image.data_reference = omero_tools.get_ref_from_object(omero_image)

    return omero_image


def dump_roi(
    conn: BlitzGateway,
    roi: mm_schema.Roi,
    target_images: Union[ImageWrapper, list[ImageWrapper]] = None,
):
    if target_images is None:
        try:
            target_images = [
                omero_tools.get_omero_obj_from_mm_obj(conn=conn, mm_obj=ref)
                for ref in roi.linked_references
                if isinstance(ref, mm_schema.DataReference)
            ]
        except AttributeError:
            logger.error(
                f"ROI {roi.name} must be linked to an image. No image provided."
            )
            return None

    if not target_images or not all(
        isinstance(i, ImageWrapper) for i in target_images
    ):
        logger.error(
            f"ROI {roi.name} must be linked to an image. {target_images} object provided is not an image."
        )
        return None

    handler = {
        "points": lambda shape: omero_tools.create_shape_point(shape),
        "lines": lambda shape: omero_tools.create_shape_line(shape),
        "rectangles": lambda shape: omero_tools.create_shape_rectangle(shape),
        "ellipses": lambda shape: omero_tools.create_shape_ellipse(shape),
        "polygons": lambda shape: omero_tools.create_shape_polygon(shape),
        "masks": lambda shape: omero_tools.create_shape_mask(shape),
    }

    shapes = []
    for shape_field in fields(roi):
        if shape_field.name not in handler:
            continue
        shape_handler = handler.get(
            shape_field.name,
            lambda shape: logger.error(
                f"Shape {shape} could not be dumped to OMERO"
            ),
        )
        shapes += [
            shape_handler(shape) for shape in getattr(roi, shape_field.name)
        ]

    omero_rois = []
    for target_image in target_images:
        omero_roi = omero_tools.create_roi(
            conn=conn,
            image=target_image,
            shapes=shapes,
            name=roi.name,
            description=roi.description,
        )
        omero_rois.append(omero_roi)

    roi.linked_references = [
        omero_tools.get_ref_from_object(r) for r in omero_rois
    ]

    return omero_rois


def dump_tag(
    conn: BlitzGateway,
    tag: mm_schema.Tag,
    target_objects: list[
        Union[ImageWrapper, DatasetWrapper, ProjectWrapper]
    ] = None,
):
    if target_objects is None:
        try:
            target_objects = omero_tools.get_omero_obj_from_mm_obj(
                conn=conn, mm_obj=tag.linked_references
            )
        except AttributeError:
            logger.error(
                f"Tag {tag.name} must be linked to an OMERO object. No object provided"
            )
            return None

    if tag.data_reference is not None:
        logger.info(f"Tag {tag.name} already exists in OMERO.")
        omero_tag = omero_tools.get_omero_obj_from_mm_obj(
            conn=conn, mm_obj=tag
        )
    else:
        logger.info(f"Creating new tag {tag.name} in OMERO.")
        omero_tag = omero_tools.create_tag(
            conn=conn,
            tag_name=tag.name,
            tag_description=tag.description,
            omero_object=target_objects,
        )
        tag.data_reference = omero_tools.get_ref_from_object(omero_tag)

    tag.linked_references = [omero_tools.get_ref_from_object(target_objects)]

    return omero_tag


def dump_key_measurement(
    conn: BlitzGateway,
    key_measurement: mm_schema.KeyMeasurements,
    target_object: Union[
        DatasetWrapper,
        ProjectWrapper,
        list[Union[DatasetWrapper, ProjectWrapper]],
    ],
):
    if not isinstance(key_measurement, mm_schema.KeyMeasurements):
        logger.error(
            f"Unsupported key measurement type for {key_measurement.name}: {key_measurement.class_name}"
        )
        return None

    if target_object is None:
        try:
            target_object = omero_tools.get_omero_obj_from_mm_obj(
                conn=conn, mm_obj=key_measurement.linked_references
            )
        except AttributeError:
            logger.error(
                f"Key-measurements {key_measurement.name} must be linked to an OMERO object. No object provided."
            )
            return None

    if key_measurement.table_data is None:
        logger.error(
            f"Key-measurements {key_measurement.name} has no data. Skipping dump."
        )
        return None

    omero_table = omero_tools.create_table(
        conn=conn,
        table=key_measurement.table_data,
        table_name=key_measurement.name,
        omero_object=target_object,
        table_description=key_measurement.description,
        namespace=key_measurement.class_class_curie,
    )
    key_measurement.data_reference = omero_tools.get_ref_from_object(
        omero_table
    )

    return omero_table


def dump_key_values(
    conn: BlitzGateway,
    key_values: mm_schema.KeyValues,
    target_object: Union[ImageWrapper, DatasetWrapper, ProjectWrapper] = None,
):
    if not isinstance(key_values, mm_schema.KeyValues):
        logger.error(
            f"Unsupported key values type for {key_values.name}: {key_values.class_name}"
        )
        return None

    if target_object is None:
        try:
            target_object = omero_tools.get_omero_obj_from_mm_obj(
                conn=conn, mm_obj=key_values.linked_references
            )
        except AttributeError:
            logger.error(
                f"Key-values {key_values.name} must be linked to an OMERO object. No object provided."
            )
            return None

    omero_key_value = omero_tools.create_key_value(
        conn=conn,
        annotation=key_values._as_dict,
        omero_object=target_object,
        annotation_name=key_values.name,
        annotation_description=key_values.description,
        namespace=key_values.class_class_curie,
    )
    key_values.data_reference = omero_tools.get_ref_from_object(
        omero_key_value
    )

    return omero_key_value


def _eval(s):
    try:
        return ast.literal_eval(s)
    except ValueError:
        corrected = f"'{s}'"
        return ast.literal_eval(corrected)


def _eval_types(table: mm_schema.Table):
    for column in table.columns.values():
        breakpoint()
        column.values = [_eval(v) for v in column.values]
    return table


def dump_table(
    conn: BlitzGateway,
    table: mm_schema.Table,
    target_object: Union[ImageWrapper, DatasetWrapper, ProjectWrapper] = None,
):
    if not isinstance(table, mm_schema.Table):
        logger.error(
            f"Unsupported table type for {table.name}: {table.class_name}"
        )
        return None

    if target_object is None:
        try:
            target_object = omero_tools.get_omero_obj_from_mm_obj(
                conn=conn, mm_obj=table.linked_references
            )
        except AttributeError:
            logger.error(
                f"Table {table.name} must be linked to an OMERO object. No object provided."
            )
            return None

    omero_table = omero_tools.create_table(
        conn=conn,
        table=table.table_data,
        table_name=table.name,
        omero_object=target_object,
        table_description=table.description,
        namespace=table.class_class_curie,
    )
    table.data_reference = omero_tools.get_ref_from_object(omero_table)

    return omero_table


def dump_comment(
    conn: BlitzGateway,
    comment: mm_schema.Comment,
    target_object: Union[ImageWrapper, DatasetWrapper, ProjectWrapper],
):
    if target_object is None:
        try:
            target_object = omero_tools.get_omero_obj_from_mm_obj(
                conn=conn, mm_obj=comment.linked_references
            )
        except AttributeError:
            logger.error(
                f"Comment {comment.name} must be linked to an OMERO object. No object provided."
            )
            return None

    return omero_tools.create_comment(
        conn=conn,
        comment_text=comment.text,
        omero_object=target_object,
        namespace=comment.class_class_curie,
    )


def dump_config_input_parameters(
    conn: BlitzGateway,
    input_parameters: mm_schema.MetricsInputParameters,
    target_omero_obj: ProjectWrapper,
):
    dumper = YAMLDumper()
    with tempfile.NamedTemporaryFile(
        prefix=f"study_config_{input_parameters.class_name}_",
        suffix=".yaml",
        mode="w",
        delete=False,
    ) as f:
        f.write(
            dumper.dumps(
                {
                    "analyse_type": input_parameters.class_name,
                    "input_parameters": input_parameters,
                }
            )
        )
        f.close()
        file_ann = omero_tools.create_file(
            conn=conn,
            file_path=f.name,
            omero_object=target_omero_obj,
            file_description="Configuration file",
            namespace=input_parameters.class_class_curie,
            mimetype="application/yaml",
        )

    return file_ann
