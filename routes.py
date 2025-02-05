from app import app
from flask import render_template, redirect, flash, request, url_for, session
from models import db, User, QualificationType, QuizTaker, Subject, Chapter, Quiz, Questions, Score
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import time


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
    session["is_admin"] = user.is_admin

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


# CRUD Chapter
@app.route("/subject/chapter/add/<int:subject_id>")
@admin_required
def add_chapter(subject_id):
    subjects = Subject.query.all()
    subject = Subject.query.get(subject_id)

    if not subject:
        flash("Subject does not exist!")
        return redirect(url_for("admin"))
    
    return render_template("chapter/add.html", subjects=subjects, subject=subject)


@app.route("/subject/chapter/add/<int:subject_id>", methods=["POST"])
@admin_required
def add_chapter_post(subject_id):
    subject = Subject.query.get(subject_id)

    if not subject:
        flash("Subject does not exist!")
        return redirect(url_for("admin"))
    
    name = request.form.get("chapter_name")
    description = request.form.get("chapter_description")
    sub_id = request.form.get("subject_id")
    
    if not name or not description or not sub_id:
        flash("Please fill all the fields!")
        return redirect(url_for("add_chapter", subject_id=subject_id))
    
    chapter = Chapter(name=name, description=description, subject_id=subject_id)

    db.session.add(chapter)
    db.session.commit()

    flash("Chapter added successfully!")
    return redirect(url_for("admin"))


@app.route("/subject/chapter/<int:id>/view")
@admin_required
def view_chapter(id):
    chapter = Chapter.query.get(id)

    if not chapter:
        flash("Chapter does not exist!")
        return redirect(url_for("admin"))
    
    return render_template("chapter/view.html", chapter=chapter)


@app.route("/subject/chapter/<int:id>/update")
@admin_required
def update_chapter(id):
    chapter = Chapter.query.get(id)

    if not chapter:
        flash("Chapter does not exist!")
        return redirect(url_for("admin"))
    
    return render_template("chapter/update.html", chapter=chapter)


@app.route("/subject/chapter/<int:id>/update", methods=["POST"])
@admin_required
def update_chapter_post(id):
    chapter = Chapter.query.get(id)

    if not chapter:
        flash("Chapter does not exist!")
        return redirect(url_for("admin"))
    
    name = request.form.get("chapter_name")
    description = request.form.get("chapter_description")

    if not name or not description:
        flash("Please fill all the fields!")
        return redirect(url_for("update_chapter", id=id))
    
    chapter.name = name
    chapter.description = description

    db.session.commit()
    flash("Chapter updated successfully!")
    return redirect(url_for("admin"))


@app.route("/subject/chapter/<int:id>/delete")
@admin_required
def delete_chapter(id):
    chapter = Chapter.query.get(id)

    if not chapter:
        flash("Chapter does not exist!")
        return redirect(url_for("admin"))
    
    return render_template("chapter/delete.html", chapter=chapter)


@app.route("/subject/chapter/<int:id>/delete", methods=["POST"])
@admin_required
def delete_chapter_post(id):
    chapter = Chapter.query.get(id)

    if not chapter:
        flash("Chapter does not exist!")
        return redirect(url_for("admin"))

    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted successfully!")
    return redirect(url_for("admin"))


# CRUD Quiz
@app.route("/admin/quiz")
@admin_required
def quiz():
    quizzes = Quiz.query.all()

    return render_template("quiz/quiz.html", quizzes=quizzes)


@app.route("/quiz/add")
@admin_required
def add_quiz():
    chapters = Chapter.query.all()

    return render_template("quiz/add.html", chapters=chapters)


@app.route("/quiz/add", methods=["POST"])
@admin_required
def add_quiz_post():
    chapter_id = request.form.get("chapter_id")
    date_html_format = request.form.get("date")
    duration = request.form.get("duration")

    if not chapter_id or not date_html_format or not duration:
        flash("Please fill all the fields!")
        return redirect(url_for("add_quiz"))
    
    date = datetime.strptime(date_html_format, "%Y-%m-%d").date()

    quiz = Quiz(chapter_id=chapter_id, date_of_quiz=date, duration=duration)

    db.session.add(quiz)
    db.session.commit()

    flash("New quiz added successfully!")
    return redirect(url_for("quiz"))


@app.route("/quiz/<int:id>/view")
@admin_required
def view_quiz(id):
    quiz = Quiz.query.get(id)

    return render_template("quiz/view.html", quiz=quiz)


@app.route("/quiz/<int:id>/update")
@admin_required
def update_quiz(id):
    quiz = Quiz.query.get(id)

    if not quiz:
        flash("Quiz does not exist!")
        return redirect(url_for("quiz"))
    
    return render_template("quiz/update.html", quiz=quiz)


@app.route("/quiz/<int:id>/update", methods=["POST"])
@admin_required
def update_quiz_post(id):
    quiz = Quiz.query.get(id)

    if not quiz:
        flash("Quiz does not exist!")
        return redirect(url_for("quiz"))
    
    date_html_format = request.form.get("date")
    duration = request.form.get("duration")

    if not date_html_format or not duration:
        flash("Please fill all the fields!")
        return redirect(url_for("update_quiz", id=id))
    
    date = datetime.strptime(date_html_format, "%Y-%m-%d").date()

    quiz.date_of_quiz = date
    quiz.duration = duration

    db.session.commit()
    flash("Quiz updated successfully!")
    return redirect(url_for("quiz"))


@app.route("/quiz/<int:id>/delete")
@admin_required
def delete_quiz(id):
    quiz = Quiz.query.get(id)

    if not quiz:
        flash("Quiz does not exist!")
        return redirect(url_for("quiz"))
    
    return render_template("quiz/delete.html", quiz=quiz)


@app.route("/quiz/<int:id>/delete", methods=["POST"])
@admin_required
def delete_quiz_post(id):
    quiz = Quiz.query.get(id)

    if not quiz:
        flash("Quiz does not exist!")
        return redirect(url_for("quiz"))
    
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully!")
    return redirect(url_for("quiz"))


# CRUD Questions
@app.route("/quiz/<int:quiz_id>/question/add")
@admin_required
def add_question(quiz_id):
    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        flash("Quiz does not exist!")
        return redirect(url_for("quiz"))
    
    return render_template("question/add.html", quiz=quiz)


@app.route("/quiz/<int:quiz_id>/question/add", methods=["POST"])
@admin_required
def add_question_post(quiz_id):
    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        flash("Quiz does not exist!")
        return redirect(url_for("quiz"))
    
    ques_title = request.form.get("ques_title")
    ques_statement = request.form.get("ques_statement")
    marks = request.form.get("marks")
    option_a = request.form.get("option_a")
    option_b = request.form.get("option_b")
    option_c = request.form.get("option_c")
    option_d = request.form.get("option_d")
    answer = request.form.get("answer")

    # return (f"{ques_title},{ques_statement},{marks},{option_a},{option_b},{option_c},{option_d},{answer}")
    if not ques_title or not ques_statement or not marks or not option_a or not option_b or not option_c or not option_d or not answer:
        flash("Please fill all the fields!")
        return redirect(url_for("add_question", quiz_id=quiz_id))
    
    ques = Questions(quiz_id=quiz_id, ques_title=ques_title, ques_statement=ques_statement, option_a=option_a, option_b=option_b, option_c=option_c, option_d=option_d, answer=answer, marks=marks)

    db.session.add(ques)
    db.session.commit()

    flash("New question added successfully!")
    return redirect(url_for("add_question", quiz_id=quiz_id))


@app.route("/quiz/question/<int:id>/update")
@admin_required
def update_question(id):
    question = Questions.query.get(id)

    if not question:
        flash("Question does not exist!")
        return redirect(url_for("quiz"))
    
    return render_template("question/update.html", question=question)


@app.route("/quiz/question/<int:id>/update", methods=["POST"])
@admin_required
def update_question_post(id):
    question = Questions.query.get(id)

    if not question:
        flash("Question does not exist!")
        return redirect(url_for("quiz"))
    
    ques_title = request.form.get("ques_title")
    ques_statement = request.form.get("ques_statement")
    marks = request.form.get("marks")
    option_a = request.form.get("option_a")
    option_b = request.form.get("option_b")
    option_c = request.form.get("option_c")
    option_d = request.form.get("option_d")
    answer = request.form.get("answer")

    if not ques_title or not ques_statement or not marks or not option_a or not option_b or not option_c or not option_d or not answer:
        flash("Please fill all the fields!")
        return redirect(url_for("update_question", id=id))
    
    # return (f"{ques_title},{ques_statement},{marks},{option_a},{option_b},{option_c},{option_d},{answer}")

    question.ques_title = ques_title
    question.ques_statement = ques_statement
    question.option_a = option_a
    question.option_b = option_b
    question.option_c = option_c
    question.option_d = option_d
    question.answer = answer
    question.marks = marks

    db.session.commit()

    flash("Question updated successfully!")
    return redirect(url_for("quiz"))


@app.route("/quiz/question/<int:id>/delete")
@admin_required
def delete_question(id):
    question = Questions.query.get(id)

    if not question:
        flash("Question does not exist!")
        return redirect(url_for("quiz"))
    
    return render_template("question/delete.html", question=question)


@app.route("/quiz/question/<int:id>/delete", methods=["POST"])
@admin_required
def delete_question_post(id):
    question = Questions.query.get(id)

    if not question:
        flash("Question does not exist!")
        return redirect(url_for("quiz"))
    
    db.session.delete(question)
    db.session.commit()

    flash("Question deleted successfully!")
    return redirect(url_for("quiz"))


# Summary 
@app.route("/admin/summary")
@admin_required
def admin_summary():
    return render_template("admin/summary.html")


# User Side Logic
@app.route("/upcoming-quiz")
@auth_required
def upcoming_quiz():
    quizzes = Quiz.query.all()

    return render_template("upcoming_quiz.html", quizzes=quizzes)


@app.route("/upcoming-quiz/<int:id>")
@auth_required
def view_upcoming_quiz(id):
    quiz = Quiz.query.get(id)

    if not quiz:
        flash("Quiz does not exist!")
        return redirect(url_for("upcoming_quiz"))
    
    return render_template("view_quiz.html", quiz=quiz)


@app.route("/quiz-start/<int:id>", methods=["GET"])
@auth_required
def quiz_start(id):
    quiz = Quiz.query.get(id)

    if "quiz_progress" not in session or session.get("quiz_id") != id:
        session["quiz_progress"] = 0
        session["score"] = 0
        session["quiz_id"] = id
        session["start_time"] = int(time.time())
    
    elapsed_time = int(time.time()) - session["start_time"]
    remaining_time = max(quiz.duration * 60 - elapsed_time, 0)
    remaining_minutes = remaining_time//60
    remaining_seconds = remaining_time%60

    progress = session["quiz_progress"]

    if progress >= len(quiz.questions):
        session["time_taken"] = quiz.duration - (remaining_time//60)
        return redirect(url_for("result"))
    
    
    current_question = quiz.questions[progress]
    
    no_of_ques = len(quiz.questions)

    return render_template("display_question.html", ques=current_question, mins=remaining_minutes, secs=remaining_seconds, no_of_ques=no_of_ques)


@app.route("/quiz-start/<int:id>", methods=["POST"])
@auth_required
def quiz_start_post(id):
    quiz = Quiz.query.get(id)
    progress = session["quiz_progress"]

    if "submit_quiz" in request.form:
        current_question = quiz.questions[progress]
        ans = request.form.get("answer")
    
        if ans == current_question.answer:
            session["score"] += current_question.marks
        
        return redirect(url_for("result"))
    
    current_question = quiz.questions[progress]
    ans = request.form.get("answer")
    
    if ans == current_question.answer:
        session["score"] += current_question.marks
    
    session["quiz_progress"] += 1
    
    return redirect(url_for("quiz_start", id=id))


@app.route("/result")
@auth_required
def result():
    final_score = session["score"]
    total_time_taken = session["time_taken"]
    session.pop("quiz_progress")
    session.pop("score")
    session.pop("quiz_id")
    session.pop("start_time")

    return render_template("result.html", final_score=final_score, total_time_taken=total_time_taken)


# Search Functionality
@app.route("/admin/search")
@admin_required
def search():
    parameter = request.args.get("parameter")
    query = request.args.get("query")

    if not parameter or not query:
        flash("Please enter something before searching!")

    if not query:
        return render_template("admin/search.html", query=query, parameter=None)
    elif parameter == "uname":
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()
        return render_template("admin/search.html", parameter=parameter, users=users)
    elif parameter == "sname":
        subjects = Subject.query.filter(Subject.name.ilike(f'%{query}%')).all()
        return render_template("admin/search.html", parameter=parameter, subjects=subjects)
    elif parameter == "qname":
        quizzes = Quiz.query.join(Chapter).filter(Chapter.name.ilike(f'%{query}%')).all()
        return render_template("admin/search.html", parameter=parameter, quizzes=quizzes)
    
    return render_template("admin/search.html", parameter=parameter, query=query)


@app.route("/search")
@auth_required
def search_user():
    parameter = request.args.get("parameter")
    query = request.args.get("query")

    if not parameter or not query:
        flash("Please enter something before searching!")

    return render_template("search_result.html", parameter=parameter, query=query)