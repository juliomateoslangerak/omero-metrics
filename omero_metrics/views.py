from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from django.urls import reverse
import omero.gateway as gateway
from omeroweb.webgateway import views as webgateway_views
from django.conf import settings
from .tools import load
from omeroweb.webclient.decorators import login_required, render_response
from io import BytesIO
from .tools.data_preperation import *
from .tools.load import *
import logging
import omero
from omero.rtypes import rstring
import omero.gateway
import random


@login_required()
def index(request, conn=None, **kwargs):
    experimenter = conn.getUser()
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,
    }
    return render(request, "metrics/index.html", context)


@login_required()
def dash_example_1_view(request, conn=None, template_name="metrics/foi_key_measurement.html", **kwargs):
    'Example view that inserts content into the dash context passed to the dash application'
    experimenter = conn.getUser()
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,

    }
    # create some context to send over to Dash:
    dash_context = request.session.get("django_plotly_dash", dict())
    dash_context['django_to_dash_context'] = "I am Dash receiving context from Django"
    request.session['django_plotly_dash'] = dash_context
    return render(request, template_name=template_name, context=context, )


@login_required()
def session_state_view(request, template_name, **kwargs):
    'Example view that exhibits the use of sessions to store state'

    session = request.session

    omero_views_count = session.get('django_plotly_dash', {})

    ind_use = omero_views_count.get('ind_use', 0)
    ind_use += 1
    omero_views_count['ind_use'] = ind_use

    context = {'ind_use': ind_use}

    session['django_plotly_dash'] = omero_views_count

    return render(request, template_name=template_name, context=context)


# @login_required()
# def data_view(request, conn=None, **kwargs):
#     g = conn.listGroups()
#     for i in g:
#         group_id=i.getId()
#     conn.SERVICE_OPTS.setOmeroGroup(group_id)
#     data_loader(conn, 10, 'Fake data')
#     return render(request, template_name='metrics/add_data.html', context={})


def webgateway_templates(request, base_template):
    """ Simply return the named template. Similar functionality to
    django.views.generic.simple.direct_to_template """
    template_name = 'metrics/webgateway/%s.html' % base_template
    return render(request, template_name, {})


@login_required()
@render_response()
def webclient_templates(request, base_template, **kwargs):
    """ Simply return the named template. Similar functionality to
    django.views.generic.simple.direct_to_template """
    template_name = 'metrics/webgateway/%s.html' % base_template
    return {'template': template_name}


@login_required()
def image_rois(request, image_id, conn=None, **kwargs):
    """ Simply shows a page of ROI thumbnails for the specified image """
    roi_ids = image_id
    return render(request, 'metrics/omero_views/image_rois.html',
                  {'roiIds': roi_ids})


@login_required()
def center_viewer_dataset(request, dataset_id, conn=None, **kwargs):
    datasetWrapper = conn.getObject("Dataset", dataset_id)
    projectWrapper = datasetWrapper.getParent()
    analysis_type = get_analysis_type(projectWrapper)
    if analysis_type == "PSFBeads":
        data = get_dataset_mapAnnotation(datasetWrapper)
        dash_context = request.session.get("django_plotly_dash", dict())
        dash_context['data'] = data
        request.session['django_plotly_dash'] = dash_context
        return render(request, 'metrics/omero_views/center_view_dataset_psf_beads.html', {'dataset_id': dataset_id})
    elif analysis_type == "FieldIllumination":
        data = get_dataset_mapAnnotation(datasetWrapper)
        dash_context = request.session.get("django_plotly_dash", dict())
        dash_context['data'] = data
        request.session['django_plotly_dash'] = dash_context
        return render(request, 'metrics/omero_views/center_view_dataset_foi.html',
                      {'dataset_id': dataset_id})
    else:
        return render(request, 'metrics/omero_views/center_view_unknown_analysis_type.html')


@login_required()
def center_viewer_image(request, image_id, conn=None, **kwargs):
    image = conn.getObject("Image", image_id)
    analysis_type = get_analysis_type(image.getParent().getParent())
    image_loaded = load_image(image)
    dash_context = request.session.get("django_plotly_dash", dict())
    dash_context['ima'] = image_loaded
    if analysis_type == "PSFBeads":

        request.session['django_plotly_dash'] = dash_context
        return render(request, 'metrics/omero_views/center_view_image_psf.html')
    elif analysis_type == "FieldIllumination":

        # image_loaded_mip = image_loaded[0].max(axis=0) # Maximum intensity projection

        file_id = getOriginalFile_id(image.getParent())
        df = get_table_originalFile_id(conn, file_id)
        roi_service = conn.getRoiService()
        result = roi_service.findByImage(int(image_id), None, conn.SERVICE_OPTS)
        shapes_rectangle, shapes_line, shapes_point = get_rois_omero(result)
        df_lines_omero = get_info_roi_lines(shapes_line)
        df_rects_omero = get_info_roi_rectangles(shapes_rectangle)
        df_points_omero = get_info_roi_points(shapes_point)

        dash_context['df_lines'] = df_lines_omero
        dash_context['df_rects'] = df_rects_omero
        dash_context['df_points'] = df_points_omero
        dash_context['df_intensity_profiles'] = df
        request.session['django_plotly_dash'] = dash_context
        return render(request, 'metrics/omero_views/center_view_image.html', {'image_id': image_id})
    else:
        return render(request, 'metrics/omero_views/center_view_unknown_analysis_type.html')


@login_required()
def center_viewer_project(request, project_id, conn=None, **kwargs):
    ProjectWrapper = conn.getObject("Project", project_id)
    study_config = get_file_annotation_project(ProjectWrapper)
    processed_datasets, unprocessed_datasets = get_dataset_ids_lists(conn, ProjectWrapper)
    df = processed_data_project_view(processed_datasets)
    dash_context = request.session.get("django_plotly_dash", dict())
    dash_context['data'] = df
    request.session['django_plotly_dash'] = dash_context
    collections_mm_p = load.load_project(conn, project_id)
    context = {'project_id': project_id, 'collections_mm_p': collections_mm_p}
    return render(request, 'metrics/omero_views/center_view_project_test.html', context)


@login_required()
def center_viewer_group(request, conn=None, **kwargs):
    group = conn.getGroupFromContext()
    group_id = group.getId()
    group_name = group.getName()
    group_description = group.getDescription()
    context = {'group_id': group_id, 'group_name': group_name, 'group_description': group_description}
    return render(request, 'metrics/omero_views/center_view_group.html', context)


#------------------------------------------------------------------------View for YAML Data-----------------------------------------------------------------------


@login_required()
def center_view_project_yaml(request, project_id, conn=None, **kwargs):
    pass


@login_required()
def center_viewer_dataset_yaml(request, dataset_id, conn=None, **kwargs):
    project_id = conn.getObject("Dataset", dataset_id).getParent().getId()
    collections_mm_p = load.load_project(conn, project_id)
    dataset = load.get_dataset_by_id(collections_mm_p, int(dataset_id))
    #dataset = [i for i in collections_mm_p.datasets if i.data_reference.omero_object_id == dataset_id][0]
    if dataset.processed:
        match dataset.__class__.__name__:
            case "FieldIlluminationDataset":
                title = 'Field Illumination Dataset'
                df = get_images_intensity_profilers(dataset)
                images = concatenate_images(conn, df)
                dash_context = request.session.get("django_plotly_dash", dict())
                dash_context['title'] = title
                dash_context['images'] = images
                dash_context['key_values_df'] = load.get_key_values(dataset.output)
                request.session['django_plotly_dash'] = dash_context
                return render(request, 'metrics/omero_views/center_view_dataset_foi.html',
                              {'dataset_id': dataset_id})
            case "PSFBeadsDataset":
                return render(request, 'metrics/omero_views/center_view_unknown_analysis_type.html')
            case _:
                return render(request, 'metrics/omero_views/center_view_unknown_analysis_type.html')
    else:
        return render(request, 'metrics/omero_views/unprocessed_dataset.html')
