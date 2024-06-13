from omero_metrics.tools import (
    omero_tools,
)
from omero.gateway import BlitzGateway
import microscopemetrics_schema.datamodel as mm_schema
from dataclasses import fields
import logging

logger = logging.getLogger(__name__)


def _empty_data_reference(
    reference: mm_schema.DataReference,
) -> None:
    reference.data_uri = None
    reference.omero_host = None
    reference.omero_port = None
    reference.omero_object_type = None
    reference.omero_object_id = None


def delete_data_references(
    mm_obj: mm_schema.MetricsObject,
) -> None:
    if isinstance(mm_obj, mm_schema.DataReference):
        _empty_data_reference(mm_obj)
    elif isinstance(mm_obj, mm_schema.MetricsObject):
        _empty_data_reference(mm_obj.data_reference)
    elif isinstance(mm_obj, list):
        return [delete_data_references(obj) for obj in mm_obj]
    else:
        raise ValueError(
            "Input should be a metrics object or a list of metrics objects"
        )


def delete_dataset_output(
    conn: BlitzGateway,
    dataset: mm_schema.MetricsDataset,
):
    ids_to_del = []
    for field in fields(dataset.output):
        try:
            ids = omero_tools.get_omero_obj_id_from_mm_obj(
                getattr(
                    dataset.output,
                    field.name,
                )
            )
            ids_to_del.append(ids)
        except AttributeError:
            continue

    del_success = omero_tools.del_objects(
        conn=conn,
        object_ids=ids_to_del,
        object_types=[
            "Annotation",
            "Roi",
            "Image/Pixels/Channel",
        ],
        delete_anns=True,
        delete_children=True,
        dry_run_first=True,
    )

    if del_success:
        dataset.output = None
        dataset.validated = False
        dataset.processed = False
        return True

    else:
        logger.error(
            f"Error deleting dataset (id:{dataset.data_reference.omero_object_id}) output"
        )
        return False


def delete_dataset_file_ann(
    conn: BlitzGateway,
    dataset: mm_schema.MetricsDataset,
) -> bool:
    try:
        id_to_del = dataset.data_reference.omero_object_id
    except AttributeError:
        logger.error(
            "No file annotation reference associated with dataset. Unable to delete"
        )
        return False
    del_success = omero_tools.del_object(
        conn=conn,
        object_id=id_to_del,
        object_type="FileAnnotation",
        delete_anns=False,
        delete_children=False,
        dry_run_first=True,
    )

    if del_success:
        delete_data_references(dataset)
        return True
