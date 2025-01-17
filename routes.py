from app import app
from flask import render_template, redirect, flash, request, url_for, session
from models import db, User, QualificationType, QuizTaker, Subject, Chapter, Quiz, Questions, Score
from werkzeug.security import generate_password_hash, check_password_hash

@app.route("/")
def index():
    return "Quiz App"


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_post():
    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    if not username or not password or not confirm_password:
        flash("Please fill out all the fields!")
        return redirect(url_for("register"))

    if confirm_password != password:
        flash("Please enter same password for the both fields!")
        return redirect(url_for("register"))
    
    user = User.query.filter_by(username=username).first()

    if user:
        flash("Username already exists!")
        return redirect(url_for("register"))
    
    pass_hash = generate_password_hash(password)

    new_user = User(username=username, password_hash=pass_hash)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("login"))


@app.route("/login")
def login():
    return render_template("login.html")