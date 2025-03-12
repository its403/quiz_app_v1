from app import app
from models import db, Subject, Chapter
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


class ChapterSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'subject_id')

chapter_schema = ChapterSchema()
chapters_schema = ChapterSchema(many=True)


@app.route("/api/chapter", methods=["POST"])
def chapter_post():
    name = request.json["name"]
    description = request.json["description"]
    subject_id = request.json["subject_id"]

    new_chapter = Chapter(name=name, description=description, subject_id=subject_id)

    db.session.add(new_chapter)
    db.session.commit()

    return chapter_schema.jsonify(new_chapter)


@app.route("/api/chapter", methods=["GET"])
def get_chapters():
    chapters = Chapter.query.all()

    result = chapters_schema.dump(chapters)

    return jsonify(result)


@app.route("/api/chapter/<int:id>", methods=["GET"])
def get_chapter(id):
    chapter = Chapter.query.get(id)

    result = chapter_schema.dump(chapter)

    return jsonify(result)


@app.route("/api/chapter/<int:id>", methods=["PUT"])
def put_chapter(id):
    chapter = Chapter.query.get(id)

    name = request.json["name"]
    description = request.json["description"]
    subject_id = request.json["subject_id"]

    chapter.name = name
    chapter.description = description
    chapter.subject_id = subject_id

    db.session.commit()

    return chapter_schema.jsonify(chapter)


@app.route("/api/chapter/<int:id>", methods=["DELETE"])
def chapter_delete(id):
    chapter = Chapter.query.get(id)

    db.session.delete(chapter)
    db.session.commit()

    return chapter_schema.jsonify(chapter)