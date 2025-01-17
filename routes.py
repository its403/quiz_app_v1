from app import app
from flask import render_template, redirect, flash, request, url_for, session
from models import db, User, QualificationType, QuizTaker, Subject, Chapter, Quiz, Questions, Score

@app.route("/")
def index():
    return "Quiz App"

