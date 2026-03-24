from typing import Union

import microscopemetrics_schema.datamodel as mm_schema
from omero.gateway import BlitzGateway, MapAnnotationWrapper

from omero_metrics.tools import omero_tools


def update_map_annotation(
    conn: BlitzGateway,
    new_map_annotation: Union[dict, MapAnnotationWrapper],
    target_map_annotation: Union[int, MapAnnotationWrapper],
    replace: bool,
    new_name: str = None,
    new_description: str = None,
    new_namespace: str = None,
):
    if isinstance(target_map_annotation, int):
        target_map_annotation = conn.getObject(
            "MapAnnotation", target_map_annotation
        )

    omero_tools.update_map_annotation(
        annotation=target_map_annotation,
        updated_annotation=new_map_annotation,
        replace=replace,
        annotation_name=new_name,
        annotation_description=new_description,
        namespace=new_namespace,
    )
