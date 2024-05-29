FROM ghcr.io/manics/omero-web-docker:ubuntu
USER root
RUN apt-get update
RUN apt-get install -y libgl1-mesa-glx
RUN apt-get install libgl1
RUN apt-get update
RUN apt-get install -y git curl
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs
COPY requirements.txt ./
RUN /opt/omero/web/venv3/bin/pip install -r ./requirements.txt
RUN echo "STATICFILES_FINDERS = [ 'django.contrib.staticfiles.finders.FileSystemFinder', 'django.contrib.staticfiles.finders.AppDirectoriesFinder', 'django_plotly_dash.finders.DashAssetFinder', 'django_plotly_dash.finders.DashComponentFinder', 'django_plotly_dash.finders.DashAppDirectoryFinder', ]" >> /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/settings.py
RUN echo "PLOTLY_COMPONENTS = ['dpd_components','dash_bootstrap_components','dash_iconify', 'dash_mantine_components','dpd_static_support']" >> /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/settings.py
RUN echo "X_FRAME_OPTIONS = 'SAMEORIGIN'" >> /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/settings.py
#RUN echo "PLOTLY_DASH = { 'ws_route' :   'dpd/ws/channel', 'http_route' : 'dpd/views', 'http_poke_enabled' : True, 'insert_demo_migrations' : False, 'cache_timeout_initial_arguments': 60, 'view_decorator': None, 'cache_arguments': False, 'serve_locally': False, }" >> /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/settings.py
RUN echo 'TEMPLATES[0]["OPTIONS"]["context_processors"].append("django.template.context_processors.request")' >> /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/settings.py
ENV REACT_VERSION=18.2.0
RUN npm install react@${REACT_VERSION}
RUN apt-get update
RUN apt-get install libxrender1
USER omero-web
#/opt/omero/web/venv3/bin/python /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/manage.py migrate

