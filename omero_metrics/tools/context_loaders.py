from omero_metrics.tools.serializers import serialize


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


def context_loader_FieldIlluminationDataset(dm):
    dm.load_data(load_images=True, force_reload=True)
    list_images, list_channels = concatenate_images(
        dm.mm_dataset.input_data.field_illumination_images
    )
    context = {
        "mm_dataset": dm.mm_dataset,
        "image_data": list_images,
        "channel_names": list_channels,
        "kkm": dm.kkm,
    }
    dm.context = serialize(context)


def context_loader_PSFBeadsDataset(dm):
    dm.load_data(load_images=False, force_reload=True)
    context = {
        "mm_dataset": dm.mm_dataset,
        "kkm": dm.kkm,
    }
    dm.context = serialize(context)
