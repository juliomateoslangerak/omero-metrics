FROM ghcr.io/manics/omero-web-docker:ubuntu
USER root
RUN apt-get update
RUN apt-get update && apt-get install -y git
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs
COPY requirements.txt ./
RUN /opt/omero/web/venv3/bin/pip install -r ./requirements.txt
ENV REACT_VERSION=18.2.0
RUN npm install react@${REACT_VERSION}
COPY ./98-dash-migrate.sh /startup/
RUN chmod +x /startup/98-dash-migrate.sh
USER omero-web
