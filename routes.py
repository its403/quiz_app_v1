from app import app
from flask import render_template, redirect, flash, request, url_for, session
from models import db, User, QualificationType, QuizTaker, Subject, Chapter, Quiz, Questions, Score
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


# Decorators for auth and admin
def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        # Checking if user in session, else log in to access index.
        if "user_id" in session:
            return func(*args, **kwargs)
        else:
            flash("Please log in to continue")
            return redirect(url_for("login"))

    return inner


def admin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue")
            return redirect(url_for("login"))

        user = User.query.get(session["user_id"])

        if not user.is_admin:
            flash("You are not authorized to access this page")
            return redirect(url_for("index"))
        return func(*args, **kwargs)

    return inner


# Index
@app.route("/")
@auth_required
def index():
    user = User.query.get(session["user_id"])

    if user.is_admin:
        return redirect(url_for("admin"))
    
    return render_template("index.html")


# Register Functionality
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


# Login Functionality
@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        flash("Please fill out all the fields!")
        return redirect(url_for("login"))

    user = User.query.filter_by(username=username).first()

    if not user:
        flash("Please enter correct username!")
        return redirect(url_for("login"))

    if not check_password_hash(user.password_hash, password):
        flash("Please enter correct password!")
        return redirect(url_for("login"))

    session["user_id"] = user.id

    flash(f"{user.username} successfully logged in!")

    return redirect(url_for("index"))


# Logout Functionality
@app.route("/logout")
@auth_required
def logout():
    session.pop("user_id")
    flash("Logged out successfully")
    return redirect(url_for("login"))


# Admin Functionality
@app.route("/admin")
@admin_required
def admin():
    subjects = Subject.query.all()
    return render_template("admin/dashboard.html", subjects=subjects)


# CRUD Subject
@app.route("/admin/subject/add")
@admin_required
def add_subject():
    return render_template("subject/add.html")


@app.route("/admin/subject/add", methods=["POST"])
@admin_required
def add_subject_post():
    name = request.form.get("subject_name")
    description = request.form.get("subject_description")

    if not name or not description:
        flash("Please fill all the fields!")
        return redirect(url_for("add_subject"))
    
    subject = Subject(name=name, description=description)
    db.session.add(subject)
    db.session.commit()
    flash("Subject added successfully")
    return redirect(url_for("admin"))


@app.route("/admin/subject/<int:id>/view")
@admin_required
def view_subject(id):
    subject =  Subject.query.get(id)

    if not subject:
        flash("Subject does not exist!")
        return redirect(url_for("admin"))
    
    return render_template("subject/view.html", subject=subject)


@app.route("/admin/subject/<int:id>/update")
@admin_required
def update_subject(id):
    subject = Subject.query.get(id)
    
    if not subject:
        flash("Subject does not exist!")
        return redirect(url_for("admin"))
    
    return render_template("subject/update.html", subject=subject)


@app.route("/admin/subject/<int:id>/update", methods=["POST"])
@admin_required
def update_subject_post(id):
    subject = Subject.query.get(id)
    
    if not subject:
        flash("Subject does not exist!")
        return redirect(url_for("admin"))

    name = request.form.get("subject_name")
    description = request.form.get("subject_description")

    if not name or not description:
        flash("Please fill out all the fields!")
        return redirect(url_for("update_subject", id=id))
    
    subject.name = name
    subject.description = description

    db.session.commit()
    flash("Subject updated successfully!")
    return redirect(url_for("admin"))


@app.route("/admin/subject/<int:id>/delete")
@admin_required
def delete_subject(id):
    subject = Subject.query.get(id)
    
    if not subject:
        flash("Subject does not exist!")
        return redirect(url_for("admin"))

    return render_template("subject/delete.html", subject=subject)

@app.route("/admin/subject/<int:id>/delete", methods=["POST"])
@admin_required
def delete_subject_post(id):
    subject = Subject.query.get(id)
    
    if not subject:
        flash("Subject does not exist!")
        return redirect(url_for("admin"))

    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted successfully!")
    return redirect(url_for("admin"))