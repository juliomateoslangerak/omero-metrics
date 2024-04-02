FROM ghcr.io/manics/omero-server-docker:ubuntu
LABEL authors="Julio Mateos Langerak"


RUN mkdir $OMERODIR/lib/scripts/omero/microscope_metrics
COPY scripts/microscope_metrics/* $OMERODIR/lib/scripts/omero/microscope_metrics/
USER root
RUN apt-get update
RUN apt-get install -y git
RUN mkdir /etc/microscopemetrics_omero
COPY microscopemetrics_omero/main_config.yaml /etc/microscopemetrics_omero/
RUN chmod -R 755 $OMERODIR/lib/scripts/omero/microscope_metrics/
RUN /opt/omero/server/venv3/bin/pip install -U "git+https://github.com/juliomateoslangerak/microscope-metrics.git"
RUN /opt/omero/server/venv3/bin/pip install -U "git+https://github.com/juliomateoslangerak/microscopemetrics-omero.git"

USER omero-server
