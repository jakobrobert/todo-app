from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# TODO extract into separate file
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    completed = db.Column(db.Boolean)


@app.route("/")
def index():
    todos = Todo.query.all()
    return render_template("index.html", todos=todos)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
