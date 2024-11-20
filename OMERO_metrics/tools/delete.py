import contextlib
import dataclasses
import logging
import omero
from OMERO_metrics.tools import omero_tools
import microscopemetrics_schema.datamodel as mm_schema
from omero.gateway import BlitzGateway
from dataclasses import fields

logger = logging.getLogger(__name__)


def _empty_data_reference(reference: mm_schema.DataReference) -> None:
    reference.data_uri = None
    reference.omero_host = None
    reference.omero_port = None
    reference.omero_object_type = None
    reference.omero_object_id = None


def delete_data_references(mm_obj: mm_schema.MetricsObject) -> None:
    if isinstance(mm_obj, mm_schema.DataReference):
        _empty_data_reference(mm_obj)
    elif isinstance(mm_obj, mm_schema.MetricsObject):
        _empty_data_reference(mm_obj.data_reference)
    elif isinstance(mm_obj, list):
        return [delete_data_references(obj) for obj in mm_obj]
    else:
        raise ValueError(
            f"Input ({mm_obj}) should be a metrics object or a list of metrics objects"
        )


def delete_mm_obj_omero_refs(
    conn: BlitzGateway, mm_obj: mm_schema.MetricsObject
):
    object_types = (
        [
            "Annotation",
            "Roi",
            "Image/Pixels/Channel",
        ],
    )
    ids_to_del = [
        ref.omero_object_id for ref in omero_tools.get_refs_from_mm_obj(mm_obj)
    ]

    if not omero_tools.have_delete_permission(
        conn=conn,
        object_ids=ids_to_del,
        object_types=object_types,
    ):
        raise PermissionError(
            "You don't have the necessary permissions to delete the dataset output."
        )

    try:
        omero_tools.del_objects(
            conn=conn,
            object_types=object_types,
            object_ids=ids_to_del,
            delete_anns=True,
            delete_children=True,
            dry_run_first=True,
            wait=True,
        )

    except Exception as e:
        logger.error(f"Error deleting dataset {mm_obj.name} output: {e}")
        raise e


def delete_dataset_file_ann(
    conn: BlitzGateway, dataset: mm_schema.MetricsDataset
) -> bool:
    try:
        id_to_del = dataset.data_reference.omero_object_id
    except AttributeError as e:
        logger.error(
            f"No file annotation reference associated with dataset {dataset.name}. Unable to delete."
        )
        raise e

    omero_tools.del_object(
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


def delete_all_mm_analysis(conn, group_id):
    all_annotations = conn.getObjects("Annotation", opts={"group": group_id})
    rois = conn.getObjects("Roi", opts={"group": group_id})
    rois_ids = [roi.getId() for roi in rois if roi.canDelete()]
    obj_ids = []
    # TODO: Delete output images
    for ann in all_annotations:
        if ann.getNs() and ann.getNs().startswith("microscopemetrics"):
            obj_ids.append(ann.getId())
    try:
        if len(obj_ids) > 0:
            conn.deleteObjects(
                graph_spec="Annotation",
                obj_ids=obj_ids,
                deleteAnns=True,
                deleteChildren=True,
                wait=True,
            )
        if len(rois_ids) > 0:
            conn.deleteObjects(graph_spec="Roi", obj_ids=rois_ids, wait=True)
        return "All microscopemetrics analysis deleted", "green"
    except Exception as e:
        if isinstance(e, omero.CmdError):
            return (
                "You don't have the necessary permissions to delete the annotations.",
                "red",
            )
        else:
            return (
                "Something happened. Couldn't delete the annotations.",
                "red",
            )
