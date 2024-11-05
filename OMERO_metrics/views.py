from django.utils.datetime_safe import datetime
from OMERO_metrics.tools import delete
from omeroweb.webclient.decorators import login_required, render_response
from OMERO_metrics.tools.data_managers import (
    DatasetManager,
    ProjectManager,
    ImageManager,
)
from django.shortcuts import render
from OMERO_metrics.tools.omero_tools import (
    get_ref_from_object,
)
from OMERO_metrics.tools.load import load_config_file_data
from OMERO_metrics.tools.load import load_image
from microscopemetrics_schema import datamodel as mm_schema
from microscopemetrics.analyses import field_illumination, psf_beads
from OMERO_metrics.tools import dump
import omero
import logging
from OMERO_metrics.tools import load
from django.urls import reverse

logger = logging.getLogger(__name__)

from omero.gateway import FileAnnotationWrapper

DATA_TYPE = {
    "FieldIlluminationInputParameters": [
        "FieldIlluminationDataset",
        "FieldIlluminationInputData",
        "field_illumination_image",
        field_illumination.analyse_field_illumination,
    ],
    "PSFBeadsInputParameters": [
        "PSFBeadsDataset",
        "PSFBeadsInputData",
        "psf_beads_images",
        psf_beads.analyse_psf_beads,
    ],
}


@login_required(setGroupContext=True)
def download_file(request, conn=None, **kwargs):
    """Download a file by triggering the omero_table view"""
    try:
        file_id = kwargs.get("file_id")
        if not file_id:
            raise ValueError("File ID is required")

        # Build the URL for the view you want to trigger
        response_url = reverse("omero_table", args=[file_id, "csv"])
        uri = request.build_absolute_uri(response_url)

        return uri
    except Exception as e:
        return str(e)  # Or consider returning an HttpResponse with the error


@login_required()
def index(request, conn=None, **kwargs):
    experimenter = conn.getUser()
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,
    }
    return render(request, "OMERO_metrics/index.html", context)


def web_gateway_templates(request, base_template):
    """Simply return the named template. Similar functionality to
    django.views.generic.simple.direct_to_template"""
    template_name = "OMERO_metrics/web_gateway/%s.html" % base_template
    return render(request, template_name, {})


@login_required()
@render_response()
def webclient_templates(request, base_template, **kwargs):
    """Simply return the named template.
    Similar functionality to
    django.views.generic.simple.direct_to_template"""
    template_name = "OMERO_metrics/web_gateway/%s.html" % base_template
    return {"template": template_name}


@login_required(setGroupContext=True)
def image_rois(request, image_id, conn=None, **kwargs):
    """Simply shows a page of ROI
    thumbnails for the specified image"""
    return render(
        request,
        "OMERO_metrics/image_rois.html",
        {"ImageId": image_id},
    )


template_name_dash = "OMERO_metrics/dash_template/dash_template.html"


@login_required(setGroupContext=True)
def center_viewer_image(request, image_id, conn=None, **kwargs):
    dash_context = request.session.get("django_plotly_dash", dict())
    try:
        image_wrapper = conn.getObject("Image", image_id)
        im = ImageManager(conn, image_wrapper)
        im.load_data()
        im.visualize_data()
        context = im.context
        dash_context["context"] = context
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=template_name_dash,
            context={"app_name": im.app_name},
        )
    except Exception as e:
        dash_context["context"] = {"message": str(e)}
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=template_name_dash,
            context={"app_name": "WarningApp"},
        )


@login_required(setGroupContext=True)
def center_viewer_project(request, project_id, conn=None, **kwargs):
    dash_context = request.session.get("django_plotly_dash", dict())
    try:
        project_wrapper = conn.getObject("Project", project_id)
        pm = ProjectManager(conn, project_wrapper)
        pm.load_data()
        pm.is_homogenized()
        pm.load_config_file()
        pm.load_threshold_file()
        pm.check_processed_data()
        pm.visualize_data()
        context = pm.context
        dash_context["context"] = context
        dash_context["context"]["project_id"] = project_id
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=template_name_dash,
            context={"app_name": pm.app_name},
        )
    except Exception as e:
        dash_context["context"] = {"message": str(e)}
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=template_name_dash,
            context={"app_name": "WarningApp"},
        )


@login_required(setGroupContext=True)
def center_viewer_group(request, conn=None, **kwargs):
    if request.session.get("active_group"):
        active_group = request.session["active_group"]
    else:
        active_group = conn.getEventContext().groupId
    file_ann, map_ann = load.get_annotations_tables(conn, active_group)
    dash_context = request.session.get("django_plotly_dash", dict())
    group = conn.getObject("ExperimenterGroup", active_group)
    group_name = group.getName()
    group_description = group.getDescription()
    context = {
        "group_id": active_group,
        "group_name": group_name,
        "group_description": group_description,
        "file_ann": file_ann,
        "map_ann": map_ann,
    }
    dash_context["context"] = context
    request.session["django_plotly_dash"] = dash_context
    return render(
        request,
        template_name=template_name_dash,
        context={"app_name": "omero_group_dash"},
    )


@login_required(setGroupContext=True)
def center_viewer_dataset(request, dataset_id, conn=None, **kwargs):
    dash_context = request.session.get("django_plotly_dash", dict())
    try:
        dataset_wrapper = conn.getObject("Dataset", dataset_id)
        dm = DatasetManager(conn, dataset_wrapper, load_images=True)
        dm.load_data()
        dm.is_processed()
        dm.visualize_data()
        dash_context["context"] = dm.context
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=template_name_dash,
            context={"app_name": dm.app_name},
        )
    except Exception as e:
        dash_context["context"] = {"message": str(e)}
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=template_name_dash,
            context={"app_name": "WarningApp"},
        )


@login_required(setGroupContext=True)
def microscope_view(request, conn=None, **kwargs):
    """Simply shows a page of ROI thumbnails for
    the specified image"""
    return render(
        request,
        template_name="OMERO_metrics/microscope.html",
        context={"app_name": "Microscope"},
    )


# These views are called from the dash app, and they return a message and a color to display in the app.


@login_required(setGroupContext=True)
def save_config(request, conn=None, **kwargs):
    """Save the configuration file"""
    try:
        project_id = kwargs["project_id"]
        mm_input_parameters = kwargs["input_parameters"]
        mm_sample = kwargs["sample"]
        project_wrapper = conn.getObject("Project", project_id)
        setup = load_config_file_data(conn, project_wrapper)
        if setup is None:
            try:
                dump.dump_config_input_parameters(
                    conn, mm_input_parameters, mm_sample, project_wrapper
                )
                return (
                    "File saved successfully, Re-click on the project to see the changes",
                    "green",
                )
            except Exception as e:
                if isinstance(e, omero.SecurityViolation):
                    return (
                        "You don't have the necessary permissions to save the configuration. ",
                        "red",
                    )
                else:
                    return str(e), "red"

        else:
            return (
                "Failed to save file, a configuration file already exists",
                "red",
            )
    except Exception as e:
        return str(e), "red"


@login_required(setGroupContext=True)
def run_analysis_view(request, conn=None, **kwargs):
    """Run the analysis"""
    try:
        dataset_wrapper = conn.getObject("Dataset", kwargs["dataset_id"])
        project_wrapper = dataset_wrapper.getParent()
        list_images = kwargs["list_images"]
        comment = kwargs["comment"]
        list_mm_images = [
            load_image(conn.getObject("Image", int(i))) for i in list_images
        ]
        mm_sample = kwargs["mm_sample"]
        mm_input_parameters = kwargs["mm_input_parameters"]
        input_data = getattr(
            mm_schema, DATA_TYPE[mm_input_parameters.class_name][1]
        )
        input_data = input_data(
            **{DATA_TYPE[mm_input_parameters.class_name][2]: list_mm_images}
        )
        mm_microscope = mm_schema.Microscope(
            name=project_wrapper.getDetails().getGroup().getName()
        )
        mm_experimenter = mm_schema.Experimenter(
            orcid="0000-0002-1825-0097", name=conn.getUser().getName()
        )
        mm_dataset = getattr(
            mm_schema, DATA_TYPE[mm_input_parameters.class_name][0]
        )
        mm_dataset = mm_dataset(
            name=dataset_wrapper.getName(),
            description=dataset_wrapper.getDescription(),
            data_reference=get_ref_from_object(dataset_wrapper),
            input_parameters=mm_input_parameters,
            microscope=mm_microscope,
            sample=mm_sample,
            input_data=input_data,
            acquisition_datetime=dataset_wrapper.getDate().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            experimenter=mm_experimenter,
        )
        run_status = DATA_TYPE[mm_input_parameters.class_name][3](mm_dataset)
        if run_status and mm_dataset.processed:
            try:
                mm_comment = mm_schema.Comment(
                    datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    text=comment,
                    comment_type="PROCESSING",
                )
                mm_dataset["output"]["comment"] = mm_comment
                dump.dump_dataset(
                    conn=conn,
                    dataset=mm_dataset,
                    target_project=project_wrapper,
                    dump_as_project_file_annotation=True,
                    dump_as_dataset_file_annotation=True,
                    dump_input_images=False,
                    dump_analysis=True,
                )

                return "Analysis completed successfully", "green"
            except Exception as e:
                return (
                    str(e),
                    "red",
                )
        else:
            logger.error("Analysis failed")
            return "We couldn't process the analysis.", "red"
    except Exception as e:
        return str(e), "red"


@login_required(setGroupContext=True)
def delete_all(request, conn=None, **kwargs):
    """Delete all the files"""
    try:
        group_id = kwargs["group_id"]
        delete.delete_all_mm_analysis(conn, group_id)
        return "Files deleted successfully", "green"
    except Exception as e:
        return str(e), "red"


@login_required(setGroupContext=True)
def save_threshold(request, conn=None, **kwargs):
    """Save the threshold"""
    try:
        project_id = kwargs["project_id"]
        threshold = kwargs["threshold"]
        project_wrapper = conn.getObject("Project", project_id)
        threshold_exist = load.load_thresholds_file_data(project_wrapper)
        if threshold:
            if threshold_exist:
                to_delete = []
                for ann in project_wrapper.listAnnotations():
                    if isinstance(ann, FileAnnotationWrapper):
                        ns = ann.getFile().getName()
                        if ns.startswith("threshold"):
                            to_delete.append(ann.getId())
                conn.deleteObjects(
                    graph_spec="Annotation",
                    obj_ids=to_delete,
                    deleteAnns=True,
                    deleteChildren=True,
                    wait=True,
                )
            file = dump.dump_threshold(conn, project_wrapper, threshold)
            return (
                "Threshold saved successfully, Re-click on the project to see the changes",
                "green",
            )
        else:
            return (
                "Failed to save threshold, a configuration file doesn't exist",
                "red",
            )
    except Exception as e:
        return str(e), "red"
