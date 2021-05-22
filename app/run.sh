source ENV/bin/activate
export FLASK_APP=todo_app
export FLASK_ENV=development
HOST=0.0.0.0
PORT=1024
flask run --host $HOST --port $PORT
