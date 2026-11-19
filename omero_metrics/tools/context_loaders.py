import logging
import os

import numpy as np

from omero_metrics.tools import (
    chromagnon_correction,
    idx_to_rgb,
    load,
    omero_tools,
    wavelength_to_rgb,
)
from omero_metrics.tools.serializers import serialize

logger = logging.getLogger(__name__)


def concatenate_images(images: list):
    list_images = []
    list_channels = []
    for mm_image in images:
        image = mm_image.array_data
        result = [image[:, :, :, :, i] for i in range(image.shape[4])]
        channels = [c.name for c in mm_image.channel_series.channels]
        list_images.extend(result)
        list_channels.extend(channels)
    return list_images, list_channels


## Image context loaders
def FieldIlluminationDataset_input_data_Image(im):
    im.mm_image = load.load_image(im.omero_image, load_array=True)
    context = {
        "image_index": im.image_index,
        "mm_image": im.mm_image,
        "mm_dataset": im.dataset_manager.mm_dataset,
        "assay_config": im.dataset_manager.assay_configuration,
    }
    im.context = serialize(context)


def PSFBeadsDataset_input_data_Image(im):
    im.mm_image = load.load_image(im.omero_image, load_array=True)
    mip_z = np.max(im.mm_image.array_data[0, ...], axis=0)
    bead_properties = load.load_table_mm_metrics(
        im.dataset_manager.mm_dataset.output["bead_properties"]
    )
    image_bead_properties = bead_properties.loc[
        bead_properties["image_id"] == im.omero_image.getId()
    ]
    min_lateral_distance_px = int(
        im.dataset_manager.mm_dataset.input_parameters.min_lateral_distance_px
    )
    min_axial_distance_px = int(
        im.dataset_manager.mm_dataset.input_parameters.min_axial_distance_px
    )

    if not image_bead_properties.empty:
        beads_array = np.zeros(
            (
                image_bead_properties.bead_id.max() + 1,
                min_axial_distance_px * 2 + 1,
                min_lateral_distance_px * 2 + 1,
                min_lateral_distance_px * 2 + 1,
                im.mm_image.shape_c,
            )
        )
        for _, row in image_bead_properties.iterrows():
            z_top = int(row.center_z) - min_axial_distance_px
            z_bottom = int(row.center_z) + min_axial_distance_px + 1
            y_left = int(row.center_y) - min_lateral_distance_px
            y_right = int(row.center_y) + min_lateral_distance_px + 1
            x_left = int(row.center_x) - min_lateral_distance_px
            x_right = int(row.center_x) + min_lateral_distance_px + 1
            bead_array = im.mm_image.array_data[
                0,  # time 0
                max(0, z_top) : min(
                    im.mm_image.array_data.shape[1], z_bottom
                ),  # z-dimension
                max(0, y_left) : min(
                    im.mm_image.array_data.shape[2], y_right
                ),  # y-dimension
                max(0, x_left) : min(
                    im.mm_image.array_data.shape[3], x_right
                ),  # x-dimension
                :,  # channel
            ]
            if bead_array.shape == beads_array[row.bead_id].shape:
                beads_array[row.bead_id] = bead_array
            else:
                # The bead was close to the edge of the image, so we need to blow it to size
                z_padding = (
                    abs(z_top) if z_top < 0 else 0,
                    (
                        abs(z_bottom - im.mm_image.array_data.shape[1])
                        if z_bottom > im.mm_image.array_data.shape[1]
                        else 0
                    ),
                )
                y_padding = (
                    abs(y_left) if y_left < 0 else 0,
                    (
                        abs(y_right - im.mm_image.array_data.shape[2])
                        if y_right > im.mm_image.array_data.shape[2]
                        else 0
                    ),
                )
                x_padding = (
                    abs(x_left) if x_left < 0 else 0,
                    (
                        abs(x_right - im.mm_image.array_data.shape[3])
                        if x_right > im.mm_image.array_data.shape[3]
                        else 0
                    ),
                )
                beads_array[row.bead_id] = np.pad(
                    bead_array, (z_padding, y_padding, x_padding, (0, 0))
                )
    else:
        beads_array = None

    im.mm_image.array_data = None
    context = {
        "image_index": im.image_index,
        "mm_image": im.mm_image,
        "mm_dataset": im.dataset_manager.mm_dataset,
        "min_lateral_distance_px": min_lateral_distance_px,
        "min_axial_distance_px": min_axial_distance_px,
        "mip_z": mip_z,
        "beads_properties": image_bead_properties,
        "beads_array": beads_array,
        "assay_config": im.dataset_manager.assay_configuration,
    }
    im.context = serialize(context)


def PSFBeadsDataset_output_AveragePSF(im):
    im.mm_image = load.load_image(im.omero_image, load_array=True)
    min_lateral_distance_px = int(
        im.dataset_manager.mm_dataset.input_parameters.min_lateral_distance_px
    )

    mips = {
        "x": np.transpose(np.max(im.mm_image.array_data[0, ...], axis=2), (1, 0, 2)),
        "y": np.max(im.mm_image.array_data[0, ...], axis=1),
        "z": np.max(im.mm_image.array_data[0, ...], axis=0),
    }

    context = {
        "image_index": im.image_index,
        "mm_image": im.mm_image,
        "mm_dataset": im.dataset_manager.mm_dataset,
        "min_lateral_distance_px": min_lateral_distance_px,
        "mips": mips,
        "assay_config": im.dataset_manager.assay_configuration,
    }
    im.context = serialize(context)


def CoRegistrationDataset_input_data_Image(im):
    im.mm_image = load.load_image(im.omero_image, load_array=True)
    mip_z = np.max(im.mm_image.array_data[0, ...], axis=0)
    bead_properties = load.load_table_mm_metrics(
        im.dataset_manager.mm_dataset.output["bead_properties"]
    )
    image_bead_properties = bead_properties.loc[
        bead_properties["image_id"] == im.omero_image.getId()
    ]
    min_lateral_distance_px = int(
        im.dataset_manager.mm_dataset.input_parameters.min_lateral_distance_px
    )
    min_axial_distance_px = int(
        im.dataset_manager.mm_dataset.input_parameters.min_axial_distance_px
    )

    beads_array = np.zeros(
        (
            image_bead_properties.bead_id.max() + 1,
            min_axial_distance_px * 2 + 1,
            min_lateral_distance_px * 2 + 1,
            min_lateral_distance_px * 2 + 1,
            im.mm_image.shape_c,
        )
    )
    for _, row in image_bead_properties.iterrows():
        z_top = int(row.center_z) - min_axial_distance_px
        z_bottom = int(row.center_z) + min_axial_distance_px + 1
        y_left = int(row.center_y) - min_lateral_distance_px
        y_right = int(row.center_y) + min_lateral_distance_px + 1
        x_left = int(row.center_x) - min_lateral_distance_px
        x_right = int(row.center_x) + min_lateral_distance_px + 1
        bead_array = im.mm_image.array_data[
            0,  # time 0
            max(0, z_top) : min(
                im.mm_image.array_data.shape[1], z_bottom
            ),  # z-dimension
            max(0, y_left) : min(
                im.mm_image.array_data.shape[2], y_right
            ),  # y-dimension
            max(0, x_left) : min(
                im.mm_image.array_data.shape[3], x_right
            ),  # x-dimension
            :,  # channel
        ]
        if bead_array.shape == beads_array[row.bead_id].shape:
            beads_array[row.bead_id] = bead_array
        else:
            # The bead was close to the edge of the image, so we need to blow it to size
            z_padding = (
                abs(z_top) if z_top < 0 else 0,
                (
                    abs(z_bottom - im.mm_image.array_data.shape[1])
                    if z_bottom > im.mm_image.array_data.shape[1]
                    else 0
                ),
            )
            y_padding = (
                abs(y_left) if y_left < 0 else 0,
                (
                    abs(y_right - im.mm_image.array_data.shape[2])
                    if y_right > im.mm_image.array_data.shape[2]
                    else 0
                ),
            )
            x_padding = (
                abs(x_left) if x_left < 0 else 0,
                (
                    abs(x_right - im.mm_image.array_data.shape[3])
                    if x_right > im.mm_image.array_data.shape[3]
                    else 0
                ),
            )
            beads_array[row.bead_id] = np.pad(
                bead_array, (z_padding, y_padding, x_padding, (0, 0))
            )

    im.mm_image.array_data = None
    context = {
        "image_index": im.image_index,
        "mm_image": im.mm_image,
        "mm_dataset": im.dataset_manager.mm_dataset,
        "min_lateral_distance_px": min_lateral_distance_px,
        "min_axial_distance_px": min_axial_distance_px,
        "mip_z": mip_z,
        "beads_properties": image_bead_properties,
        "beads_array": beads_array,
        "assay_config": im.dataset_manager.assay_configuration,
    }
    im.context = serialize(context)


def StageDriftDataset_input_data_Image(im):
    im.mm_image = load.load_image(im.omero_image, load_array=False)
    image_properties = load.load_table_mm_metrics(
        im.dataset_manager.mm_dataset.output["image_properties"]
    )
    image_properties = image_properties.loc[
        image_properties["image_id"] == im.omero_image.getId()
    ]

    context = {
        "image_index": im.image_index,
        "mm_image": im.mm_image,
        "mm_dataset": im.dataset_manager.mm_dataset,
        "image_properties": image_properties,
        "assay_config": im.dataset_manager.assay_configuration,
    }
    im.context = serialize(context)


## Dataset context loaders
def FieldIlluminationDataset(dm):
    dm.load_data(load_images=True, force_reload=True)
    list_images, list_channels = concatenate_images(
        dm.mm_dataset.input_data.field_illumination_images
    )
    context = {
        "mm_dataset": dm.mm_dataset,
        "image_data": list_images,
        "channel_names": list_channels,
        "assay_config": dm.assay_configuration,
    }
    dm.context = serialize(context)


def PSFBeadsDataset(dm):
    dm.load_data(load_images=False, force_reload=True)
    channel_names = list(
        dict.fromkeys(
            [
                c.name
                for mm_image in dm.mm_dataset.input_data.psf_beads_images
                for c in mm_image.channel_series.channels
            ]
        )
    )
    bead_properties = {
        col.name: col.values for col in dm.mm_dataset.output.bead_properties.columns
    }
    min_lateral_distance_px = int(
        dm.mm_dataset.input_parameters.min_lateral_distance_px
    )

    context = {
        "mm_dataset": dm.mm_dataset,
        "channel_names": channel_names,
        "bead_properties": bead_properties,
        "min_lateral_distance_px": min_lateral_distance_px,
        "assay_config": dm.assay_configuration,
    }
    dm.context = serialize(context)


def CoRegistrationDataset(dm):
    dm.load_data(load_images=False, force_reload=True)
    channel_names = list(
        dict.fromkeys(
            [
                c.name
                for mm_image in dm.mm_dataset.input_data.multiwavelength_beads_images
                for c in mm_image.channel_series.channels
            ]
        )
    )
    bead_properties = {
        col.name: col.values for col in dm.mm_dataset.output.bead_properties.columns
    }
    min_lateral_distance_px = int(
        dm.mm_dataset.input_parameters.min_lateral_distance_px
    )

    context = {
        "mm_dataset": dm.mm_dataset,
        "channel_names": channel_names,
        "bead_properties": bead_properties,
        "min_lateral_distance_px": min_lateral_distance_px,
        "assay_config": dm.assay_configuration,
    }
    dm.context = serialize(context)


def StageDriftDataset(dm):
    dm.load_data(load_images=False, force_reload=True)
    image_properties = {
        col.name: col.values for col in dm.mm_dataset.output.image_properties.columns
    }
    mean_square_displacements = {
        col.name: col.values
        for col in dm.mm_dataset.output.mean_square_displacements.columns
    }

    context = {
        "mm_dataset": dm.mm_dataset,
        "image_properties": image_properties,
        "mean_square_displacements": mean_square_displacements,
        "assay_config": dm.assay_configuration,
    }
    dm.context = serialize(context)


def ChromaticShiftDataset(dm):
    dm.load_data(load_images=False, force_reload=True)
    context = {
        "mm_dataset": dm.mm_dataset,
        "assay_config": dm.assay_configuration,
    }
    dm.context = serialize(context)


def _display_uint8(arr):
    """Per-channel min-max normalised uint8 copy (last axis = channel)."""
    arr = np.asarray(arr)
    out = np.zeros(arr.shape, dtype=np.uint8)
    for c in range(arr.shape[-1]):
        ch = arr[..., c].astype(np.float32)
        mn, mx = float(ch.min()), float(ch.max())
        if mx > mn:
            out[..., c] = np.clip((ch - mn) / (mx - mn) * 255.0, 0, 255).astype(
                np.uint8
            )
    return out


def _omero_mip(image) -> np.ndarray:
    """Maximum-intensity projection over Z of an OMERO image (t=0), as (y, x, c).

    Reads one plane at a time, so the whole stack is never in memory.
    """
    pixels = image.getPrimaryPixels()
    nz, nc = image.getSizeZ(), image.getSizeC()
    mip = np.zeros((image.getSizeY(), image.getSizeX(), nc), dtype=np.float32)
    for c in range(nc):
        planes = pixels.getPlanes([(z, c, 0) for z in range(nz)])
        for z, plane in enumerate(planes):
            if z == 0:
                mip[..., c] = plane
            else:
                np.maximum(mip[..., c], plane, out=mip[..., c])
    return mip


def _find_corrected_image(im):
    """The OMERO image of the chromatic-shift-corrected version of ``im``."""
    image_id = im.omero_image.getId()
    output = getattr(im.dataset_manager.mm_dataset, "output", None)
    corrected_images = getattr(output, "corrected_images", None) or []

    target = None
    for ci in corrected_images:
        for src in ci.source_images or []:
            if getattr(src, "omero_object_id", None) == image_id:
                target = ci
                break
        if target is not None:
            break
    if target is None:  # by name (see chromatic_shift.aligned_image_name)
        root = os.path.splitext(im.mm_image.name or "image")[0]
        target = next(
            (ci for ci in corrected_images if ci.name == f"{root}_ALN.tif"), None
        )

    if target is None or target.data_reference is None:
        return None
    try:
        return omero_tools.get_omero_obj_from_mm_obj(conn=im._conn, mm_obj=target)
    except Exception as e:
        logger.warning(f"Could not find the corrected image of {image_id}: {e}")
        return None


def ChromaticShiftDataset_input_data_Image(im):
    """Context of the image dashboard of a chromatic shift analysis.

    Only the Z projections (uint8) are kept in the session. The Z planes shown
    in the before/after view are read from OMERO when the Z slider moves
    (views.image_planes), so large stacks do not bloat the session.

    With average_references only the combined image is corrected; the other
    images then have no corrected image of their own and are corrected for
    display with the dataset's correction file, one section at a time
    (views.corrected_section).
    """
    from microscopemetrics.analyses import chromagnon_apply

    im.mm_image = load.load_image(im.omero_image, load_array=False)
    raw_mip = _omero_mip(im.omero_image)

    corrected = _find_corrected_image(im)
    corrected_mip = None
    if corrected is not None:
        try:
            corrected_mip = _display_uint8(_omero_mip(corrected))
        except Exception as e:
            logger.warning(f"Could not read the corrected image {corrected.getId()}: {e}")
            corrected = None

    correction_ann_id = None
    if corrected is None:
        correction_ann_id = chromagnon_correction.dataset_correction_ann_id(
            im.dataset_manager.omero_dataset
        )
        if correction_ann_id is not None:
            try:
                path = chromagnon_correction.download_correction(
                    im._conn, correction_ann_id
                )
                section = chromagnon_apply.correct_section(
                    im.mm_image, np.moveaxis(raw_mip, -1, 0), path
                )
                corrected_mip = _display_uint8(np.moveaxis(section, 0, -1))
            except Exception as e:
                logger.warning(
                    f"Could not correct image {im.omero_image.getId()} for display: {e}"
                )
                correction_ann_id = None

    context = {
        "image_index": im.image_index,
        "mm_image": im.mm_image,
        "mm_dataset": im.dataset_manager.mm_dataset,
        "assay_config": im.dataset_manager.assay_configuration,
        "image_id": int(im.omero_image.getId()),
        "corrected_image_id": int(corrected.getId()) if corrected is not None else None,
        "correction_ann_id": correction_ann_id,
        "size_z": int(im.omero_image.getSizeZ()),
        "mip_z": _display_uint8(raw_mip),
        "corrected_mip": corrected_mip,
    }
    im.context = serialize(context)


def EmptyMetricsDatasetCollection(pm):
    pm.load_data()
    pm.load_input_config()
    pm.load_thresholds()
    context = {
        "project_id": int(pm.omero_project.getId()),
        "project_name": pm.omero_project.getName(),
        "project_description": pm.omero_project.getDescription() or "",
        "dataset_class": None,
        "min_date": None,
        "max_date": None,
        "unprocessed_datasets": list(pm.unprocessed_datasets),
        "input_parameters": pm.input_parameters,
        "sample": pm.sample,
        "thresholds": pm.thresholds,
    }
    pm.context = serialize(context)


def HarmonizedMetricsDatasetCollection(pm):
    pm.load_data()
    pm.load_input_config()
    pm.load_thresholds()
    dates = []
    min_date = None
    max_date = None
    last_dataset_id = None
    kkm_config = pm.assay_configuration.kkm_configuration
    collection_key_measurements_by_kkm = {name: [] for name in kkm_config}
    collection_key_measurements_by_dataset_id = {}
    collection_comments_by_dataset_id = {}

    for dataset in pm.mm_dataset_collection.dataset_collection:
        if not dataset.processed:
            # In principle, omero-metrics is generating and processing datasets in one go, so this should never happen
            raise ValueError(f"Dataset {dataset.name} is not processed")
        key_measurements_by_kkm = {
            name: [
                {
                    # TODO: We are removing here time from the date, but this might bite us back at some point
                    # We should consider keeping time in the date
                    "date": dataset.acquisition_datetime.split("T")[0],
                    "dataset_id": int(dataset.data_reference.omero_object_id),
                    **(
                        {
                            km[x.key]: km[name]
                            for km in dataset.output.key_measurements
                        }
                        if x.key
                        else {
                            "no_key": km[name]
                            for km in dataset.output.key_measurements
                        }
                    ),
                    **(
                        {
                            f"{km[x.key]}_err": km[x.error_bar]
                            for km in dataset.output.key_measurements
                        }
                        if x.key and x.error_bar
                        else (
                            {
                                "no_key_err": km[x.error_bar]
                                for km in dataset.output.key_measurements
                            }
                            if x.error_bar
                            else {}
                        )
                    ),
                    **(
                        {
                            f"{km[x.key]}_rgb": wavelength_to_rgb(
                                km[x.wavelength_nm]
                            )
                            for km in dataset.output.key_measurements
                        }
                        if x.key and x.wavelength_nm
                        else (
                            {
                                "no_key_rgb": wavelength_to_rgb(km[x.wavelength_nm])
                                for km in dataset.output.key_measurements
                            }
                            if x.wavelength_nm
                            and not any(
                                [
                                    np.isnan(km[x.wavelength_nm])
                                    for km in dataset.output.key_measurements
                                ]
                            )
                            else (
                                {
                                    f"{km[x.key]}_rgb": idx_to_rgb(i)
                                    for i, km in enumerate(
                                        dataset.output.key_measurements
                                    )
                                }
                                if x.key
                                else {
                                    "no_key_rgb": idx_to_rgb(i)
                                    for i, km in enumerate(
                                        dataset.output.key_measurements
                                    )
                                }
                            )
                        )
                    ),
                }
            ]
            for name, x in kkm_config.items()
        }
        for name in kkm_config:
            collection_key_measurements_by_kkm[name].extend(
                key_measurements_by_kkm[name]
            )
        collection_key_measurements_by_dataset_id[
            dataset.data_reference.omero_object_id
        ] = {
            "caption": f"{dataset.name} acquired on {dataset.acquisition_datetime}",
            "names": list(kkm_config.keys()),
            "display_names": [x.display_name for x in kkm_config.values()],
            "descriptions": [x.description for x in kkm_config.values()],
            "keys": [x.key for x in kkm_config.values()],
            "display_in_group_level": [
                x.display_in_group_level for x in kkm_config.values()
            ],
            "units": [x.units for x in kkm_config.values()],
            "axis": [x.axis for x in kkm_config.values()],
            "values": [
                [km[name] for name in kkm_config]
                for km in dataset.output.key_measurements
            ],
        }

        if dataset.output.comment:
            collection_comments_by_dataset_id[
                int(dataset.data_reference.omero_object_id)
            ] = {
                "author": dataset.output.comment.author,
                "datetime": dataset.output.comment.comment_datetime,
                "text": dataset.output.comment.text,
            }

        dates.append(dataset.acquisition_datetime)
        min_date = (
            min(min_date, dataset.acquisition_datetime)
            if min_date
            else dataset.acquisition_datetime
        )
        if (
            max_date is not None
            and dataset.acquisition_datetime > max_date
            or max_date is None
        ):
            max_date = dataset.acquisition_datetime
            last_dataset_id = dataset.data_reference.omero_object_id
    context = {
        "project_id": int(pm.omero_project.getId()),
        "dataset_class": pm.mm_dataset_collection.dataset_class,
        "project_name": pm.mm_dataset_collection.name,
        "project_description": pm.mm_dataset_collection.description,
        "mm_dataset_collection": pm.mm_dataset_collection,
        "key_measurements_by_kkm": collection_key_measurements_by_kkm,
        "key_measurements_by_dataset_id": collection_key_measurements_by_dataset_id,
        "comments_by_dataset_id": collection_comments_by_dataset_id,
        "dates": dates,
        "min_date": min_date,
        "max_date": max_date,
        "last_dataset_id": last_dataset_id,
        "mm_unprocessed_datasets": list(pm.unprocessed_datasets),
        "input_parameters": pm.input_parameters,
        "sample": pm.sample,
        "thresholds": pm.thresholds,
        "assay_config": pm.assay_configuration,
    }
    pm.context = serialize(context)


def MetricsDatasetCollections(gm):
    # gm.load_data()
    for pm in gm.mm_dataset_collections:
        pm.load_context()
    context = {
        "experimenter_group_id": int(gm.omero_experimenter_group_id),
        "experimenter_group_name": gm.omero_experimenter_group.getName(),
        "experimenter_group_description": gm.omero_experimenter_group.getDescription(),
        "experimenters": gm.experimenters,
        "project_contexts": [p.context for p in gm.mm_dataset_collections],
    }
    gm.context = serialize(context)


def EmptyMetricsDatasetCollections(gm):
    gm.load_data()
    context = {
        "experimenter_group_id": int(gm.omero_experimenter_group_id),
        "experimenter_group_name": gm.omero_experimenter_group.getName(),
        "experimenter_group_description": gm.omero_experimenter_group.getDescription(),
        "experimenters": gm.experimenters,
    }
    gm.context = serialize(context)
