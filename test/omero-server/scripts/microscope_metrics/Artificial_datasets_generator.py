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

This script is generating a number of copies of a dataset introducing some noise and blur in the images.

@author Julio Mateos Langerak
<a href="mailto:julio.mateos-langerak@igh.cnrs.fr">julio.mateos-langerak@igh.cnrs.fr</a>
@version Alpha0.1
<small>
(<b>Internal version:</b> $Revision: $Date: $)
</small>
@since 3.0-Beta4.3
"""

# import logging
import logging
import random
from datetime import datetime
from itertools import product

import numpy as np

# import omero dependencies
# import omero.scripts as scripts
import omero.gateway as gateway
from metrics.interface import omero as ome

# import configuration parser
from metrics.utils.utils import MetricsConfig
from skimage import img_as_float
from skimage.filters import gaussian
from skimage.util import random_noise

# from omero.rtypes import rlong, rstring


def Run_script_locally():
    from credentials import GROUP, HOST, PASSWORD, PORT, USER

    conn = gateway.BlitzGateway(
        username=USER, passwd=PASSWORD, group=GROUP, port=PORT, host=HOST
    )

    script_params = {
        "DatasetID": 1,
        "nr of copies": 12,
        "Dates": [
            "2017-03-20_monthly",
            "2017-04-20_monthly",
            "2017-05-20_monthly",
            "2017-06-20_monthly",
            "2017-07-20_monthly",
            "2017-08-20_monthly",
            "2017-09-20_monthly",
            "2017-10-20_monthly",
            "2017-11-20_monthly",
            "2017-12-20_monthly",
            "2018-01-20_monthly",
            "2018-02-20_monthly",
        ],
    }

    if len(script_params["Dates"]) != script_params["nr of copies"]:
        raise ValueError("Not matching nr of copies and dates fields")

    try:
        conn.connect()

        source_dataset = conn.getObject("Dataset", script_params["DatasetID"])
        project = source_dataset.getParent()
        images = list(source_dataset.listChildren())
        images_data = [ome.get_image_intensities(i) for i in images]

        for n in range(script_params["nr of copies"]):
            new_dataset = ome.create_dataset(
                connection=conn,
                name=script_params["Dates"][n],
                description=f'copy of dataset ID:{script_params["DatasetID"]}\nRandom noise and sigma added',
                parent_project=project,
            )
            random_sigma = abs(random.gauss(0.6, 0.3))
            random_noise_level = random.gauss(0.1, 0.01)
            for image, image_data in zip(images, images_data):
                new_image_data = np.squeeze(np.copy(image_data))
                noise_image = np.ones_like(new_image_data, dtype="float64")
                for c in range(new_image_data.shape[1]):  # dimensions are zctxy
                    # adding gaussian blur
                    new_image_data[:, c, ...] = gaussian(
                        np.squeeze(new_image_data[:, c, ...]),
                        multichannel=False,
                        sigma=random_sigma,
                        preserve_range=True,
                    )
                    # adding noise
                    # noise_image[:, c, ...] = random_noise(np.squeeze(noise_image[:, c, ...]),
                    #                                       mode='poisson',
                    #                                       # var=random_noise_level,
                    #                                       clip=False)
                    # new_image_data[:, c, ...] = random_noise(np.squeeze(new_image_data[:, c, ...]),
                    #                                          var=random_noise_level,
                    #                                          clip=False)

                # noise_image = noise_image * random_noise_level
                # new_image_data = new_image_data * noise_image
                new_image_data = new_image_data.astype(np.int)
                new_image_data = new_image_data.astype(image_data.dtype)
                zct_list = list(
                    product(
                        range(new_image_data.shape[0]),
                        range(new_image_data.shape[1]),
                    )
                )
                zct_generator = (new_image_data[z, c, :, :] for z, c in zct_list)

                new_image = conn.createImageFromNumpySeq(
                    zctPlanes=zct_generator,
                    imageName=f"{script_params['Dates'][n][:4]}{script_params['Dates'][n][5:7]}{image.getName()[6:]}",
                    sizeZ=new_image_data.shape[0],
                    sizeC=new_image_data.shape[1],
                    sizeT=1,
                    dataset=new_dataset,
                    sourceImageId=image.getId(),
                )

    finally:
        conn.close()


if __name__ == "__main__":
    Run_script_locally()
