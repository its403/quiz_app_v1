from app import app
from models import db, Subject
from flask import request, jsonify
from flask_marshmallow import Marshmallow

ma = Marshmallow(app)

class SubjectSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description')

subject_schema = SubjectSchema()
subjects_schema = SubjectSchema(many=True)


@app.route("/api/subject", methods=["POST"])
def post():
    name = request.json["name"]
    description = request.json["description"]

    new_subject = Subject(name=name, description=description)

    db.session.add(new_subject)
    db.session.commit()

    return subject_schema.jsonify(new_subject)


@app.route("/api/subject", methods=["GET"])
def get_subjects():
    all_subjects = Subject.query.all()

    result = subjects_schema.dump(all_subjects)

    return jsonify(result)


@app.route("/api/subject/<int:id>", methods=["GET"])
def get(id):
    subject = Subject.query.get(id)

    return subject_schema.jsonify(subject)


@app.route("/api/subject/<int:id>", methods=["PUT"])
def put(id):
    subject = Subject.query.get(id)

    name = request.json["name"]
    description = request.json["description"]
    
    subject.name = name
    subject.description = description

    db.session.commit()

    return subject_schema.jsonify(subject)


@app.route("/api/subject/<int:id>", methods=["DELETE"])
def delete(id):
    subject = Subject.query.get(id)

    db.session.delete(subject)
    db.session.commit()

    return subject_schema.jsonify(subject)