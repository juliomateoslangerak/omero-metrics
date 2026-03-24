set -eu

export PATH="/opt/omero/web/venv3/bin:$PATH"
python=/opt/omero/web/venv3/bin/python
cd /opt/omero/web/venv3/lib/python3.10/site-packages/omeroweb

echo "Run migrate to update the database OMERO.web"
$python manage.py migrate

echo "Collecting static files for OMERO.web"
$python manage.py collectstatic --noinput