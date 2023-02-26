source ENV/bin/activate
export FLASK_APP=todo_app:app
export FLASK_ENV=development
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=1024
flask run
