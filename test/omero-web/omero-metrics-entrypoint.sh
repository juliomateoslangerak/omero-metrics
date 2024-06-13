#!/bin/bash

echo "Migrate the Database at startup of project"

while ! /opt/omero/web/venv3/bin/python /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb/manage.py migrate  2>&1; do
   echo "Migration is in progress status"
   sleep 3
done

echo "Django docker is fully configured successfully."

exec "$@"
