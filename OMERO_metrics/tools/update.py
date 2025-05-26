from typing import Union
from OMERO_metrics.tools import omero_tools
import microscopemetrics_schema.datamodel as mm_schema
from omero.gateway import BlitzGateway, MapAnnotationWrapper


def update_key_measurements(
    conn: BlitzGateway,
    new_key_measurements: Union[dict, mm_schema.KeyMeasurements],
    target_key_measurements: Union[int, MapAnnotationWrapper],
    replace: bool,
    new_name: str = None,
    new_description: str = None,
    new_namespace: str = None,
):
    if isinstance(target_key_measurements, int):
        target_key_measurements = conn.getObject("MapAnnotation", target_key_measurements)

    omero_tools.update_key_measurements(
        annotation=target_key_measurements,
        updated_annotation=new_key_measurements,
        replace=replace,
        annotation_name=new_name,
        annotation_description=new_description,
        namespace=new_namespace,
    )
