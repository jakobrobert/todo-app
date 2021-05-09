from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

import configparser


config = configparser.ConfigParser()
config.read("server.ini")
URL_PREFIX = config["DEFAULT"]["URL_PREFIX"]
DATABASE_URI = config["DEFAULT"]["DATABASE_URI"]

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    # TODO set defaults
    completed = db.Column(db.Boolean)
    timestamp_created = db.Column(db.TIMESTAMP(timezone=True))


@app.route(URL_PREFIX + "/", methods=["GET"])
def index():
    todos = Todo.query.all()
    return render_template("index.html", todos=todos)


@app.route(URL_PREFIX + "/add", methods=["POST"])
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, completed=False, timestamp_created=func.now())
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("index"))


@app.route(URL_PREFIX + "/update/<int:todo_id>", methods=["GET"])
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for("index"))


@app.route(URL_PREFIX + "/delete/<int:todo_id>", methods=["GET"])
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    db.create_all()
    # use 0.0.0.0 as host so the app is publicly available
    app.run(host="0.0.0.0", port=1024, debug=True)
