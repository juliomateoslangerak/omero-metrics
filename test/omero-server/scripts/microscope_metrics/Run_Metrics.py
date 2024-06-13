#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------------------------------------------
  Copyright (C) 2023 CNRS. All rights reserved.

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

This script runs microscope-metrics on the selected dataset.

@author Julio Mateos Langerak
<a href="mailto:julio.mateos-langerak@igh.cnrs.fr">julio.mateos-langerak@igh.cnrs.fr</a>
@version Alpha0.1
<small>
(<b>Internal version:</b> $Revision: $Date: $)
</small>
@since 3.0-Beta4.3
"""

# import logging utilities
import logging
from io import StringIO

import omero.gateway as gateway

# import omero dependencies
import omero.scripts as scripts

# import configuration parser
import yaml
from omero.rtypes import rlong, rstring

# import metrics
import omero_metrics.tools.process as process

# Creating logging services
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create a log string to return warnings in the web interface
log_string = StringIO()
string_hdl = logging.StreamHandler(log_string)
string_hdl.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s: %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
string_hdl.setFormatter(formatter)

# create console handler with a higher log level
console_hdl = logging.StreamHandler()
console_hdl.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_hdl.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(console_hdl)
logger.addHandler(string_hdl)


def _read_config_from_file_ann(file_annotation):
    return yaml.load(
        file_annotation.getFileInChunks().__next__().decode(),
        Loader=yaml.SafeLoader,
    )


def run_script():
    try:
        with open("/etc/microscopemetrics_omero/main_config.yaml", "r") as f:
            main_config = yaml.load(f, Loader=yaml.SafeLoader)
    except FileNotFoundError:
        logger.error(
            "No main configuration file found: Contact your administrator."
        )
        return

    client = scripts.client(
        "Run_Metrics.py",
        """This is the main script of microscope-metrics-omero. It will run the analyses on the selected 
        dataset. For more information check \n
        http://www.mri.cnrs.fr\n  
        Copyright: Write here some copyright info""",  # TODO: copyright info and documentation
        scripts.String(
            "Data_Type",
            optional=False,
            grouping="1",
            description="The dataset you want to work with.",
            values=[rstring("Dataset")],
            default="Dataset",
        ),
        scripts.List(
            "IDs",
            optional=False,
            grouping="1",
            description="List of Dataset IDs",
        ).ofType(rlong(0)),
        scripts.String(
            "Comment",
            optional=True,
            grouping="2",
            description="Add here any eventuality that you want to add to the analysis",
        ),
    )

    try:
        script_params = {}
        for key in client.getInputKeys():
            if client.getInput(key):
                script_params[key] = client.getInput(key, unwrap=True)

        logger.debug(f"Metrics started using parameters: {script_params}")

        conn = gateway.BlitzGateway(client_obj=client)
        logger.info(f"Connection success: {conn.isConnected()}")

        datasets = conn.getObjects("Dataset", script_params["IDs"])

        for dataset in datasets:
            microscope_prj = (
                dataset.getParent()
            )  # We assume one project per dataset

            if microscope_prj is None:
                logger.error(
                    f"No parent project found for dataset {dataset.getName()}: "
                    f"Every dataset must be part of a project and only one project."
                )
                continue

            study_conf_file_name = main_config["study_conf_file_name"]
            study_config = None
            for ann in microscope_prj.listAnnotations():
                if (
                    type(ann) == gateway.FileAnnotationWrapper
                    and ann.getFileName() == study_conf_file_name
                ):
                    study_config = _read_config_from_file_ann(ann)

            if not study_config:
                logger.error(
                    f"No study configuration {study_conf_file_name} found for dataset {dataset.getName()}: "
                    f"Please contact your administrator"
                )
                continue

            config = {
                "script_parameters": script_params,
                "main_config": main_config,
                "study_config": study_config,
            }

            process.process_dataset(dataset=dataset, config=config)

        logger.info("Metrics analysis finished")

    finally:
        logger.info("Closing connection")

        client.setOutput("Message", rstring(log_string.getvalue()))
        client.closeSession()


if __name__ == "__main__":
    run_script()
