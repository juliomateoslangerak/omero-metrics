import logging
from dataclasses import fields
from datetime import datetime
from typing import Union

from microscopemetrics.samples import (
    argolight,
    field_illumination,
    numpy_to_image_byref,
)
from microscopemetrics_schema.datamodel import (
    microscopemetrics_schema as mm_schema,
)
from omero.gateway import (
    BlitzGateway,
    DatasetWrapper,
    ImageWrapper,
    ProjectWrapper,
)

from OMERO_metrics.tools import dump, load, omero_tools

logger = logging.getLogger(__name__)

ANALYSIS_CLASS_MAPPINGS = {
    "ArgolightBAnalysis": argolight.ArgolightBAnalysis,
    "ArgolightEAnalysis": argolight.ArgolightEAnalysis,
    "FieldIlluminationAnalysis": field_illumination.FieldIlluminationAnalysis,
}

OBJECT_TO_DUMP_FUNCTION = {
    mm_schema.Image: dump.dump_image,
    mm_schema.Roi: dump.dump_roi,
    mm_schema.Tag: dump.dump_tag,
    mm_schema.KeyValues: dump.dump_key_value,
    mm_schema.Table: dump.dump_table,
}


def _annotate_processing(
    omero_object: Union[ImageWrapper, DatasetWrapper, ProjectWrapper],
    start_time: datetime.time,
    end_time: datetime.time,
    analysis_config: dict,
    namespace: str,
) -> None:
    annotation = {
        "analysis_class": analysis_config["analysis_class"],
        "start_time": str(start_time),
        "end_time": str(end_time),
        **analysis_config["parameters"],
    }

    omero_tools.create_key_value(
        conn=omero_object._conn,
        annotation=annotation,
        omero_object=omero_object,
        annotation_name="microscopemetrics processing metadata",
        namespace=namespace,
    )


def process_image(
    image: ImageWrapper, analysis_config: dict
) -> mm_schema.MetricsDataset:
    logger.info(
        f"Running analysis {analysis_config['analysis_class']} on image: {image.getId()}"
    )

    analysis = ANALYSIS_CLASS_MAPPINGS[analysis_config["analysis_class"]](
        name=analysis_config["name"],
        description=analysis_config["description"],
        microscope=analysis_config["microscope"],
        input={
            analysis_config["data"]["name"]: numpy_to_image_byref(
                array=load.load_image(image),
                name=image.getName(),
                description=image.getDescription(),
                image_url=omero_tools.get_ref_from_object(image),
            ),
            **analysis_config["parameters"],
        },
        output={},
    )
    analysis.run()

    logger.info(
        f"Analysis {analysis_config['analysis_class']} on image {image.getId()} completed"
    )

    return analysis


def process_dataset(dataset: DatasetWrapper, config: dict) -> None:
    logger.info(f"Analyzing data from Dataset: {dataset.getId()}")
    logger.info(config)

    for analysis_name, analysis_config in config["study_config"][
        "analysis"
    ].items():
        if analysis_config["do_analysis"]:
            logger.info(f"Running analysis {analysis_name}...")
            start_time = datetime.now()

            if (
                "tag_id" in analysis_config["data"]
                and analysis_config["data"]["tag_id"] is not None
            ):
                images = omero_tools.get_tagged_images_in_dataset(
                    dataset, analysis_config["data"]["tag_id"]
                )
            else:
                images = [i for i in dataset.listChildren()]

            for image in images:
                mm_dataset = process_image(
                    image=image, analysis_config=analysis_config
                )
                if not mm_dataset.processed:
                    logger.error("Analysis failed. Not dumping data")

                try:
                    dump_strategy = config["main_config"]["dump_strategy"][
                        mm_dataset.class_name
                    ]
                    dump_image_process(
                        image=image,
                        analysis=mm_dataset,
                        dataset_dump_strategy=dump_strategy,
                    )

                except KeyError as e:
                    logger.error(
                        f"No dump strategy found for {mm_dataset.class_name}"
                    )
                    raise e

            try:
                logger.info("Adding comment")
                comment = config["script_parameters"]["Comment"]
            except KeyError:
                logger.info("No comment provided")
                comment = None

            if comment is not None:
                omero_tools.create_comment(
                    conn=dataset._conn,
                    omero_object=dataset,
                    comment_text=comment,
                    namespace=ANALYSIS_CLASS_MAPPINGS[
                        analysis_config["analysis_class"]
                    ].class_model_uri,
                )
            end_time = datetime.now()

            logger.info("Annotating processing metadata")
            _annotate_processing(
                omero_object=dataset,
                start_time=start_time,
                end_time=end_time,
                analysis_config=analysis_config,
                namespace=ANALYSIS_CLASS_MAPPINGS[
                    analysis_config["analysis_class"]
                ].class_model_uri,
            )


def dump_image_process(
    image: ImageWrapper,
    analysis: mm_schema.MetricsDataset,
    dataset_dump_strategy: dict,
) -> None:
    for output_field in fields(analysis.output):
        output_element = getattr(analysis.output, output_field.name)

        for target_type, dump_strategy in dataset_dump_strategy[
            output_field.name
        ].items():
            if dump_strategy["link"]:
                if target_type == "image":
                    target_omero_object = image
                elif target_type == "dataset":
                    target_omero_object = image.getParent()
                elif target_type == "project":
                    target_omero_object = image.getParent().getParent()
                else:
                    logger.error(
                        f"Invalid target type {target_type} for {output_field.name}"
                    )
                    continue
                dump_output_element(
                    output_element=output_element,
                    target_omero_object=target_omero_object,
                    append_to_existing="append_to_existing" in dump_strategy
                    and dump_strategy["append_to_existing"],
                    as_table="as_table" in dump_strategy
                    and dump_strategy["as_table"],
                )


def dump_output_element(
    output_element: mm_schema.MetricsOutput,
    target_omero_object: Union[ImageWrapper, DatasetWrapper, ProjectWrapper],
    append_to_existing: bool = False,
    as_table: bool = False,
) -> None:
    if isinstance(output_element, list):
        for e in output_element:
            dump_output_element(e, target_omero_object)
    else:
        logger.info(f"Dumping {output_element.class_name} to OMERO")
        conn = target_omero_object._conn
        for t, f in OBJECT_TO_DUMP_FUNCTION.items():
            if isinstance(output_element, t):
                return f(
                    conn,
                    output_element,
                    target_omero_object,
                    append_to_existing,
                    as_table,
                )

        logger.info(
            f"{output_element.class_name} output could not be dumped to OMERO"
        )

        return None
