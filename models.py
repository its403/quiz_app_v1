from app import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
from werkzeug.security import generate_password_hash

db = SQLAlchemy(app)

class QualificationType(Enum):
    HIGH_SCHOOL = "High School"
    BACHELORS = "Bachelors"
    MASTERS = "Masters"
    DOCTRATE = "Doctrate"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    qualification = db.Column(db.Enum(QualificationType), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    scores = db.relationship('Score', back_populates='user')

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False, default="No description available.")

    chapters = db.relationship('Chapter', back_populates='subject')

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False, default="No description available.")
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    subject = db.relationship('Subject', back_populates='chapters')
    quizzes = db.relationship('Quiz', back_populates='chapter')

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    chapter = db.relationship('Chapter', back_populates='quizzes')
    questions = db.relationship('Questions', back_populates='quiz')
    scores = db.relationship('Score', back_populates='quiz')

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    ques_title = db.Column(db.String, nullable=False)
    ques_statement = db.Column(db.String, nullable=False)
    option_a = db.Column(db.String, nullable=False)
    option_b = db.Column(db.String, nullable=False)    
    option_c = db.Column(db.String, nullable=False)        
    option_d = db.Column(db.String, nullable=False)
    answer = db.Column(db.String, nullable=False)
    marks = db.Column(db.Integer, nullable=False)

    quiz = db.relationship('Quiz', back_populates='questions')

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)
    total_score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)

    user = db.relationship('User', back_populates='scores')
    quiz = db.relationship('Quiz', back_populates='scores')

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(is_admin=True).first()

    if not admin:
        pass_hash = generate_password_hash("admin")

        dob = datetime.today().strftime('%Y-%m-%d')

        date = datetime.strptime(dob, "%Y-%m-%d").date()

        admin = User(username="admin", password_hash=pass_hash, name="Admin", qualification="DOCTRATE", dob=date, is_admin=True)

        db.session.add(admin)
        db.session.commit()
