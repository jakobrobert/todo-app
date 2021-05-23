virtualenv -p python3 ENV
source ENV/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
