#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------------------------------------------
  Copyright (C) 2020 CNRS. All rights reserved.

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License along
  with this program; if not, write to the Free Software Foundation, Inc.,
  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

------------------------------------------------------------------------------

This script validates the measurements from a list of datasets.

@author Julio Mateos Langerak
<a href="mailto:julio.mateos-langerak@igh.cnrs.fr">julio.mateos-langerak@igh.cnrs.fr</a>
@version Alpha0.1
<small>
(<b>Internal version:</b> $Revision: $Date: $)
</small>
@since 3.0-Beta4.3
"""

# Creating logging services
import logging
from datetime import datetime

import omero.gateway as gateway
# import omero dependencies
import omero.scripts as scripts
from omero.rtypes import rlong, robject, rstring

logger = logging.getLogger("metrics")
logger.setLevel(logging.DEBUG)

METRICS_GENERATED_TAG_ID = (
    1284  # This has to go into some installation configuration
)

UNVALIDATED_NAMESPACE_PREFIX = "metrics/analyzed"
VALIDATED_NAMESPACE_PREFIX = "metrics/validated"


def _replace_namespace(annotation, count):
    curr_namespace = annotation.getNs()
    new_namespace = curr_namespace.replace(
        UNVALIDATED_NAMESPACE_PREFIX, VALIDATED_NAMESPACE_PREFIX, 1
    )
    annotation.setNs(new_namespace)
    annotation.save()
    return count + 1


def validate_dataset(dataset):
    logger.info(f"Validating measurements from Dataset: {dataset.getId()}")
    logger.info(f"Date and time: {datetime.now()}")

    changes_count = 0

    # We are recursively looping through the annotations and images of the dataset, checking namespaces and changing them

    # Dataset power measurement map annotations.
    # This is a special case as they must be modifiable by the user we cannot assign a metrics namespace
    # Currently namespace is annotated in the description
    # TODO: Fix storing laser power measurements without namespace
    for ann in dataset.listAnnotations():
        if isinstance(
            ann, gateway.MapAnnotationWrapper
        ) and ann.getDescription().startswith(UNVALIDATED_NAMESPACE_PREFIX):
            namespace = ann.getDescription()
            ann.setNs(
                namespace.replace(
                    UNVALIDATED_NAMESPACE_PREFIX, VALIDATED_NAMESPACE_PREFIX, 1
                )
            )
            ann.setDescription("")
            changes_count += 1

    # Dataset annotations
    for ann in dataset.listAnnotations():
        if (
            isinstance(
                ann,
                (
                    gateway.TagAnnotationWrapper,
                    gateway.MapAnnotationWrapper,
                    gateway.FileAnnotationWrapper,
                    gateway.CommentAnnotationWrapper,
                ),
            )
            and ann.getNs() is not None
            and ann.getNs().startswith(UNVALIDATED_NAMESPACE_PREFIX)
        ):
            changes_count = _replace_namespace(ann, changes_count)

    # TODO: Decide if we are creating a validated tag
    # # Clean new images tagged as metrics
    # for image in dataset.listChildren():
    #     for ann in image.listAnnotations():
    #         if type(ann) == gateway.TagAnnotationWrapper and ann.getId() == METRICS_GENERATED_TAG_ID:
    #             conn.deleteObjects('Image', [image.getId()], deleteAnns=False, deleteChildren=True, wait=True)

    # File and map annotations on rest of images
    for image in dataset.listChildren():
        for ann in image.listAnnotations():
            if (
                isinstance(
                    ann,
                    (
                        gateway.TagAnnotationWrapper,
                        gateway.MapAnnotationWrapper,
                        gateway.FileAnnotationWrapper,
                    ),
                )
                and ann.getNs() is not None
                and ann.getNs().startswith(UNVALIDATED_NAMESPACE_PREFIX)
            ):
                changes_count = _replace_namespace(ann, changes_count)

    # TODO: Rois are not having a namespace. Is there another possibility to secure them?
    # # Delete all rois
    # roi_service = conn.getRoiService()
    # for image in dataset.listChildren():
    #     rois = roi_service.findByImage(image.getId(), None)
    #     rois_ids = [r.getId().getValue() for r in rois.rois]
    #     if len(rois_ids) > 1:
    #         conn.deleteObjects('Roi', rois_ids, wait=True)

    logger.info(f"Nr of validated annotations: {changes_count}")


def run_script_local():
    from credentials import GROUP, HOST, PASSWORD, PORT, USER

    conn = gateway.BlitzGateway(
        username=USER, passwd=PASSWORD, group=GROUP, port=PORT, host=HOST
    )

    script_params = {
        "IDs": [1],
        # 'IDs': [154],
        "Confirm validation": True,
    }

    try:
        conn.connect()
        # Verify user is part of metrics group by checking current group. If not, abort the script
        if conn.getGroupFromContext().getName() != "metrics":
            raise PermissionError(
                "You are not authorized to run this script in the current context."
            )

        logger.info(f"Connection success: {conn.isConnected()}")

        datasets = conn.getObjects(
            "Dataset", script_params["IDs"]
        )  # generator of datasets

        for dataset in datasets:
            validate_dataset(dataset=dataset)
    finally:
        conn.close()


def run_script():
    client = scripts.client(
        "Clean_Datasets.py",
        """This script is deleting all measurements made by omero.metrics from the selected datasets.
        For more information check \n
        http://www.mri.cnrs.fr\n
        Copyright: Write here some copyright info""",  # TODO: copyright info
        scripts.String(
            "Data_Type",
            optional=False,
            grouping="1",
            description="The data you want to work with.",
            values=[rstring("Dataset")],
            default="Dataset",
        ),
        scripts.List(
            "IDs",
            optional=False,
            grouping="1",
            description="List of Dataset IDs",
        ).ofType(rlong(0)),
        scripts.Bool(
            "Confirm validation",
            optional=False,
            grouping="1",
            default=False,
            description="Confirm that you want to validate metrics' measurements.",
        ),
    )

    try:
        script_params = {}
        for key in client.getInputKeys():
            if client.getInput(key):
                script_params[key] = client.getInput(key, unwrap=True)

        if script_params["Confirm validation"]:
            logger.info(
                f"Validation started using parameters: \n{script_params}"
            )

            conn = gateway.BlitzGateway(client_obj=client)

            # Verify user is part of metrics group by checking current group. If not, abort the script
            if conn.getGroupFromContext().getName() != "metrics":
                raise PermissionError(
                    "You are not authorized to run this script in the current context."
                )

            logger.info(f"Connection success: {conn.isConnected()}")

            datasets = conn.getObjects(
                "Dataset", script_params["IDs"]
            )  # generator of datasets

            for dataset in datasets:
                validate_dataset(dataset=dataset)
        else:
            logger.info("Validation was not confirmed.")

        logger.info(f"End time: {datetime.now()}")

    finally:
        logger.info("Closing connection")
        client.closeSession()


if __name__ == "__main__":
    # run_script()
    run_script_local()
