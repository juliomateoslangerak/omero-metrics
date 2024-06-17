from typing import Union

import microscopemetrics_schema.datamodel as mm_schema
from omero.gateway import BlitzGateway, MapAnnotationWrapper

from . import (
    omero_tools,
)


def update_key_value(
    conn: BlitzGateway,
    new_key_values: Union[dict, mm_schema.KeyValues],
    target_key_values: Union[int, MapAnnotationWrapper],
    replace: bool,
    new_name: str = None,
    new_description: str = None,
    new_namespace: str = None,
):
    if isinstance(target_key_values, int):
        target_key_values = conn.getObject(
            "MapAnnotation",
            target_key_values,
        )

    omero_tools.update_key_value(
        annotation=target_key_values,
        updated_annotation=new_key_values,
        replace=replace,
        annotation_name=new_name,
        annotation_description=new_description,
        namespace=new_namespace,
    )
