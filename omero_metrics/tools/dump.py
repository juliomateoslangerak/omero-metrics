import ast
import logging
import tempfile
from dataclasses import fields
from typing import Union

from linkml_runtime.dumpers import YAMLDumper
from microscopemetrics_schema.datamodel import (
    microscopemetrics_schema as mm_schema,
)
from omero.gateway import (
    BlitzGateway,
    DatasetWrapper,
    ExperimenterGroupWrapper,
    ImageWrapper,
    ProjectWrapper,
)

from omero_metrics.tools import omero_tools

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
    "points": omero_tools.create_shape_point,
    "lines": omero_tools.create_shape_line,
    "rectangles": omero_tools.create_shape_rectangle,
    "ellipses": omero_tools.create_shape_ellipse,
    "polygons": omero_tools.create_shape_polygon,
    "masks": omero_tools.create_shape_mask,
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
        namespace=microscope.class_model_uri,
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
    data_obj: Union[mm_schema.MetricsInput, mm_schema.MetricsOutput]
):
    def _remove(_attr):
        match _attr:
            case mm_schema.Image():
                _attr.array_data = None
            case mm_schema.Table():
                _attr.table_data = None
            case mm_schema.Roi():
                if _attr.masks:
                    [_remove(m.mask) for m in _attr.masks]

    try:
        for field in fields(data_obj):
            try:
                _attr = getattr(data_obj, field.name)
                if isinstance(_attr, list):
                    [_remove(i) for i in _attr]
                else:
                    _remove(_attr)
            except AttributeError:
                continue
    except TypeError:
        pass


def _dump_mm_dataset_as_file_annotation(
    conn: BlitzGateway,
    mm_dataset: mm_schema.MetricsDataset,
    target_omero_obj: Union[ProjectWrapper, DatasetWrapper],
):
    # We need to remove the data on the numppy and pandas data objects as they cannot be serialized by linkml
    _remove_unsupported_types(mm_dataset.input)
    if mm_dataset.output:
        _remove_unsupported_types(mm_dataset.output)

    dumper = YAMLDumper()

    with tempfile.NamedTemporaryFile(
        prefix=f"{mm_dataset.class_name}_", mode="w", delete=False
    ) as f:
        f.write(dumper.dumps(mm_dataset))
        f.close()
        file_path = f.name
        ns = mm_dataset.class_class_curie
        description = mm_dataset.description
        mimetype = "application/yaml"
        file_ann = conn.createFileAnnfromLocalFile(
            file_path, mimetype=mimetype, ns=ns, desc=description
        )
        target_omero_obj.linkAnnotation(file_ann)

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
    if dataset.data_reference:
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
        for input_field in fields(dataset.input):
            input_element = getattr(dataset.input, input_field.name)
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
        if dataset.processed:
            if dataset.output is not None:
                _dump_analysis_metadata(dataset, omero_dataset)
                _dump_dataset_output(dataset.output, omero_dataset)
            else:
                logger.error(
                    f"Dataset {dataset.name} is processed but has no output. Skipping dump."
                )
        else:
            logger.warning(
                f"Dataset {dataset.name} is not processed. Skipping output dump."
            )

    if dump_as_dataset_file_annotation:
        _dump_mm_dataset_as_file_annotation(
            conn=conn, mm_dataset=dataset, target_omero_obj=omero_dataset
        )

    if dump_as_project_file_annotation:
        _dump_mm_dataset_as_file_annotation(
            conn=conn, mm_dataset=dataset, target_omero_obj=target_project
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

    input_metadata = _get_input_metadata(dataset.input)

    output_metadata = _get_output_metadata(dataset.output)

    metadata = {**input_metadata, **output_metadata}

    omero_tools.create_key_value(
        conn=target_dataset._conn,
        annotation=metadata,
        omero_object=target_dataset,
        annotation_name=dataset.class_name,
        annotation_description=dataset.description,
        namespace=dataset.class_model_uri,
    )


def _get_input_metadata(
    input: mm_schema.MetricsInput,
) -> dict:
    metadata = {}
    for input_field in fields(input):
        input_element = getattr(input, input_field.name)
        if isinstance(input_element, mm_schema.Image):
            continue
        elif isinstance(input_element, list) and all(
            isinstance(i_e, mm_schema.Image) for i_e in input_element
        ):
            continue
        else:
            metadata[input_field.name] = str(input_element)

    return metadata


def dump_analysis_config():
    pass


def _get_output_metadata(
    dataset_output: mm_schema.MetricsOutput,
) -> dict:
    output_elements = {}
    for output_field in fields(dataset_output):
        output_element = getattr(dataset_output, output_field.name)
        if isinstance(output_element, mm_schema.MetricsObject):
            continue
        if isinstance(output_element, list) and any(
            isinstance(i, mm_schema.MetricsObject) for i in output_element
        ):
            continue
        output_elements[output_field.name] = str(output_element)

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
    output_element,
    target_dataset: DatasetWrapper,
):
    match output_element:
        case mm_schema.Image():
            dump_image(
                conn=conn,
                image=output_element,
                target_dataset=target_dataset,
            )
        case mm_schema.Roi():
            dump_roi(
                conn=conn,
                roi=output_element,
            )
        case mm_schema.Tag():
            dump_tag(
                conn=conn,
                tag=output_element,
            )
        case mm_schema.KeyValues():
            dump_key_value(
                conn=conn,
                key_values=output_element,
                target_object=target_dataset,
            )
        case mm_schema.Table():
            dump_table(
                conn=conn,
                table=output_element,
                target_object=target_dataset,
            )
        # case mm_schema.Comment():
        #     dump_comment(
        #         conn=conn,
        #         comment=output_element,
        #         target_object=target_dataset,
        #     )
        case _:
            try:
                logger.error(
                    f"{output_element.name} output could not be dumped to OMERO"
                )
            except AttributeError:
                logger.error(
                    f"{output_element} output could not be dumped to OMERO"
                )


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

    if len(target_images) == 0:
        logger.error(
            f"ROI {roi.name} must be linked to an image. {target_images} object provided is not an image."
        )
        return None
    shapes = []
    for shape_field in fields(roi):
        if shape_field.name in SHAPE_TYPE_TO_FUNCTION:
            shapes += [
                SHAPE_TYPE_TO_FUNCTION[shape_field.name](shape)
                for shape in getattr(roi, shape_field.name)
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
                f"ROI {tag.name} must be linked to at least one image. No image provided."
            )
            return None

    if tag.data_reference is not None:
        logger.info(f"Tag {tag.name} already exists in OMERO.")
        omero_tag = omero_tools.get_omero_obj_from_mm_obj(
            conn=conn, mm_obj=tag
        )
        # TODO: link to objects here
    else:
        logger.info(f"Creating new tag {tag.name} in OMERO.")
        omero_tag = omero_tools.create_tag(
            conn=conn,
            tag_name=tag.name,
            tag_description=tag.description,
            omero_objects=target_objects,
        )
        tag.data_reference = omero_tools.get_ref_from_object(omero_tag)

    tag.linked_references = [omero_tools.get_ref_from_object(target_objects)]

    return omero_tag


def dump_key_value(
    conn: BlitzGateway,
    key_values: mm_schema.KeyValues,
    target_object: Union[ImageWrapper, DatasetWrapper, ProjectWrapper] = None,
):
    if target_object is None:
        try:
            target_object = omero_tools.get_omero_obj_from_mm_obj(
                conn=conn, mm_obj=key_values.linked_references
            )
        except AttributeError:
            logger.error(
                f"ROI {key_values.name} must be linked to an image. No image provided."
            )
            return None

    omero_key_value = omero_tools.create_key_value(
        conn=conn,
        annotation=key_values._as_dict,
        omero_object=target_object,
        annotation_name=key_values.name,
        annotation_description=key_values.description,
        namespace=key_values.class_model_uri,
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
                f"ROI {table.name} must be linked to an image. No image provided."
            )
            return None

    omero_table = omero_tools.create_table(
        conn=conn,
        table=table.table_data,
        table_name=table.name,
        omero_object=target_object,
        table_description=table.description,
        namespace=table.class_model_uri,
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
                f"ROI {comment.name} must be linked to an image. No image provided."
            )
            return None

    return omero_tools.create_comment(
        conn=conn,
        comment_text=comment.text,
        omero_object=target_object,
        namespace=comment.class_model_uri,
    )
