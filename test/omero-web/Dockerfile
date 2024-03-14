FROM ghcr.io/manics/omero-web-docker:ubuntu
USER root
RUN apt-get update
RUN apt-get install -y git
RUN /opt/omero/web/venv3/bin/pip install bootstrap4
#RUN /opt/omero/web/venv3/bin/pip install pandas
RUN /opt/omero/web/venv3/bin/pip install django-plotly-dash
RUN /opt/omero/web/venv3/bin/pip install dpd_static_support
RUN /opt/omero/web/venv3/bin/pip install dash-bootstrap-components
RUN /opt/omero/web/venv3/bin/pip install django-bootstrap4
RUN /opt/omero/web/venv3/bin/pip install dash_mantine_components
RUN /opt/omero/web/venv3/bin/pip install -U "git+https://github.com/juliomateoslangerak/microscopemetrics-omero.git"
RUN echo "STATICFILES_FINDERS = [ 'django.contrib.staticfiles.finders.FileSystemFinder', 'django.contrib.staticfiles.finders.AppDirectoriesFinder', 'django_plotly_dash.finders.DashAssetFinder', 'django_plotly_dash.finders.DashComponentFinder', 'django_plotly_dash.finders.DashAppDirectoryFinder', ]" >> /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/settings.py
RUN echo "PLOTLY_COMPONENTS = ['dpd_components','dash_bootstrap_components', 'dash_mantine_components','dpd_static_support']" >> /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/settings.py
RUN echo "X_FRAME_OPTIONS = 'SAMEORIGIN'" >> /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/settings.py
RUN echo 'TEMPLATES[0]["OPTIONS"]["context_processors"].append("django.template.context_processors.request")' >> /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/settings.py
#RUN /opt/omero/web/venv3/bin/pip install dpd_static_support
USER omero-web
#/opt/omero/web/venv3/bin/python /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/manage.py migrate