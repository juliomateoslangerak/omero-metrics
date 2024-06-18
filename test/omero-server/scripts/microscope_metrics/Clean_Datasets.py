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

This script deletes from a list of datasets the data produced by OMERO-metrics.

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

METRICS_GENERATED_TAG_ID = 1284
ALL_METRICS_GENERATED_TAG_IDs = [1284, 1281, 1280, 1283, 1282]


def clean_dataset(connection, dataset, namespace_like=None):
    logger.info(f"Cleaning measurements from Dataset: {dataset.getId()}")
    logger.info(f"Date and time: {datetime.now()}")

    # Clean Dataset annotations
    for (
        ann
    ) in (
        dataset.listAnnotations()
    ):
        if isinstance(
            ann,
            (
                gateway.MapAnnotationWrapper,
                gateway.FileAnnotationWrapper,
                gateway.CommentAnnotationWrapper,
            ),
        ):
            connection.deleteObjects("Annotation", [ann.getId()], wait=True)

    # Unlink Dataset tag annotations
    links = connection.getAnnotationLinks(
        parent_type="Dataset",
        parent_ids=[dataset.getId()],
        ann_ids=ALL_METRICS_GENERATED_TAG_IDs,
    )
    link_ids = [link.getId() for link in links]
    if len(link_ids) > 0:
        connection.deleteObjects("DatasetAnnotationLink", link_ids, wait=True)
    else:
        logger.warning("There were no dataset tags to unlink")

    # Clean new images tagged as metrics
    for image in dataset.listChildren():
        for ann in image.listAnnotations():
            if (
                type(ann) == gateway.TagAnnotationWrapper
                and ann.getId() == METRICS_GENERATED_TAG_ID
            ):
                connection.deleteObjects(
                    "Image",
                    [image.getId()],
                    deleteAnns=False,
                    deleteChildren=True,
                    wait=True,
                )

    # Clean File and map annotations on rest of images
    for image in dataset.listChildren():
        for ann in image.listAnnotations():
            if isinstance(
                ann,
                (gateway.MapAnnotationWrapper, gateway.FileAnnotationWrapper),
            ):
                connection.deleteObjects(
                    "Annotation", [ann.getId()], wait=True
                )

    # Delete all rois
    roi_service = connection.getRoiService()
    for image in dataset.listChildren():
        rois = roi_service.findByImage(image.getId(), None)
        rois_ids = [r.getId().getValue() for r in rois.rois]
        if len(rois_ids) > 1:
            connection.deleteObjects("Roi", rois_ids, wait=True)


def run_script_local():
    from credentials import GROUP, HOST, PASSWORD, PORT, USER

    conn = gateway.BlitzGateway(
        username=USER, passwd=PASSWORD, group=GROUP, port=PORT, host=HOST
    )

    script_params = {
        "IDs": [1],
        # 'IDs': [146, 145, 144, 143, 142, 141, 140, 139, 138, 137, 136, 135],
        # 'IDs': [154],
        "Confirm deletion": True,
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
            clean_dataset(connection=conn, dataset=dataset)
    finally:
        conn.close()


def run_script():
    client = scripts.client(
        "Clean_Datasets.py",
        """This script is deleting all measurements made by omero.metrics from the selected datasets.
        For more information check \n
        http://www.mri.cnrs.fr\n
        Copyright: Write here some copyright info""",
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
            "Confirm deletion",
            optional=False,
            grouping="1",
            default=False,
            description="Confirm that you want to delete metrics measurements.",
        ),
    )

    try:
        script_params = {}
        for key in client.getInputKeys():
            if client.getInput(key):
                script_params[key] = client.getInput(key, unwrap=True)

        if script_params["Confirm deletion"]:
            logger.info(
                f"Deletion started using parameters: \n{script_params}"
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
                logger.info(f"deleting data from Dataset: {dataset.getId()}")
                clean_dataset(connection=conn, dataset=dataset)
        else:
            logger.info("Deletion was not confirmed.")

        logger.info(f"End time: {datetime.now()}")

    finally:
        logger.info("Closing connection")
        client.closeSession()


if __name__ == "__main__":
    run_script()
    # run_script_local()
