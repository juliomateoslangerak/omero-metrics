import logging
import omero
from OMERO_metrics.tools import omero_tools
import microscopemetrics_schema.datamodel as mm_schema
from omero.gateway import BlitzGateway, FileAnnotationWrapper, DatasetWrapper
from OMERO_metrics.tools.data_type import DATASET_TYPES

logger = logging.getLogger(__name__)


def _empty_data_reference(reference: mm_schema.DataReference) -> None:
    reference.data_uri = None
    reference.omero_host = None
    reference.omero_port = None
    reference.omero_object_type = None
    reference.omero_object_id = None


def delete_data_references(mm_obj: mm_schema.MetricsObject) -> list:
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
    refs_to_del = omero_tools.get_refs_from_mm_obj(mm_obj)
    refs_to_del = [
        (ref.omero_object_type.code.text, ref.omero_object_id)
        for ref in refs_to_del
        if all([ref, ref.omero_object_type, ref.omero_object_id])
    ]

    if not omero_tools.have_delete_permission(
        conn=conn, object_refs=refs_to_del
    ):
        raise PermissionError(
            "You don't have the necessary permissions to delete the dataset output."
        )

    try:
        omero_tools.del_objects(
            conn=conn,
            object_refs=refs_to_del,
            delete_anns=True,
            delete_children=True,
            dry_run_first=True,
            wait=True,
        )

    except Exception as e:
        logger.error(f"Error deleting object {mm_obj}: {e}")
        raise e


def delete_dataset_file_ann(conn: BlitzGateway, dataset: DatasetWrapper):
    logger.info(f"Deleting file annotations for dataset {dataset.getId()}")
    for ann in dataset.listAnnotations():
        if isinstance(ann, FileAnnotationWrapper):
            ns = ann.getNs()
            if ns.startswith("microscopemetrics_schema:analyses"):
                ds_type = ns.split("/")[-1]
                logger.info(
                    f"Deleting {ds_type} file annotation {ann.getId()}"
                )
                if ds_type in DATASET_TYPES:
                    omero_tools.del_object(
                        conn=conn,
                        object_ref=("Annotation", ann.getId()),
                        delete_anns=True,
                        delete_children=True,
                        dry_run_first=True,
                    )


def delete_all_annotations(conn, group_id):
    all_annotations = conn.getObjects("Annotation", opts={"group": group_id})
    obj_ids = []
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
