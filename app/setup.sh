virtualenv -p python3 ENV
source ENV/bin/activate
pip install --upgrade pip
# TODO use requirements.txt
pip install flask
pip install flask-sqlalchemy
pip install mysqlclient
deactivate
