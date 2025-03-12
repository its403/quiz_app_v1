from app import app
from models import db, Subject, Chapter, Quiz, Score
from flask import request, jsonify
from flask_marshmallow import Marshmallow
from datetime import datetime

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


class QuizSchema(ma.Schema):
    class Meta:
        fields = ('id', 'chapter_id', 'date_of_quiz', 'duration')

quiz_schema = QuizSchema()
quizzes_schema = QuizSchema(many=True)


@app.route("/api/quiz", methods=["POST"])
def quiz_post():
    chapter_id = request.json["chapter_id"]
    date_of_quiz = request.json["date_of_quiz"]
    duration = request.json["duration"]

    date_of_quiz = datetime.strptime(date_of_quiz, "%Y-%m-%d").date()

    new_quiz = Quiz(chapter_id=chapter_id, date_of_quiz=date_of_quiz, duration=duration)

    db.session.add(new_quiz)
    db.session.commit()

    return quiz_schema.jsonify(new_quiz)


@app.route("/api/quiz", methods=["GET"])
def get_quizzes():
    quizzes = Quiz.query.all()

    result = quizzes_schema.dump(quizzes)

    return jsonify(result)


@app.route("/api/quiz/<int:id>", methods=["GET"])
def get_quiz(id):
    quiz = Quiz.query.get(id)

    result = quiz_schema.dump(quiz)

    return jsonify(result)


@app.route("/api/quiz/<int:id>", methods=["PUT"])
def put_quiz(id):
    quiz = Quiz.query.get(id)

    chapter_id = request.json["chapter_id"]
    date_of_quiz = request.json["date_of_quiz"]
    duration = request.json["duration"]

    date_of_quiz = datetime.strptime(date_of_quiz, "%Y-%m-%d").date()

    quiz.chapter_id = chapter_id
    quiz.date_of_quiz = date_of_quiz
    quiz.duration = duration

    db.session.commit()

    return quiz_schema.jsonify(quiz)


@app.route("/api/quiz/<int:id>", methods=["DELETE"])
def quiz_delete(id):
    quiz = Quiz.query.get(id)

    db.session.delete(quiz)
    db.session.commit()

    return quiz_schema.jsonify(quiz)


class ScoreSchema(ma.Schema):
    class Meta:
        fields = ('id', 'quiz_id', 'user_id', 'time_taken', 'total_score', 'date')

score_schema = ScoreSchema()
scores_schema = ScoreSchema(many=True)


@app.route("/api/score", methods=["GET"])
def get_scores():
    scores = Score.query.all()

    result = scores_schema.dump(scores)

    return jsonify(result)


@app.route("/api/score/<int:id>", methods=["GET"])
def get_score(id):
    score = Score.query.get(id)

    result = score_schema.dump(score)

    return jsonify(result)


@app.route("/api/score/<int:id>", methods=["DELETE"])
def score_delete(id):
    score = Score.query.get(id)

    db.session.delete(score)
    db.session.commit()

    return score_schema.jsonify(score)