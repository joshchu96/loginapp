from flask import Flask, redirect, render_template, flash, session, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, User, Feedback
from form import RegisterForm, LoginForm, FeedbackForm


 
app = Flask(__name__)

app.config['SECRET_KEY'] = "password"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///loginapp"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
debugger = DebugToolbarExtension(app)

db.init_app(app)
app.app_context().push()
db.create_all()

@app.route("/")
def home():
    return redirect('/register')

@app.route("/register", methods=["GET","POST"])
def register_form():
    """Form that will register/create a user"""
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        newUser = User.encrpytion(username,password,email,first_name,last_name)
        db.session.add(newUser)
        db.session.commit()
        flash("Your User Account has been created!")
        return redirect("/secret")

    return render_template('form_register.html', form=form)

@app.route("/login", methods=["GET","POST"])
def create_handle_login():
    """Create login form and authenticate it"""
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        #authenticate the submission data using bcrpyt
        user = User.authentication(username,password)

        if user:
            session["username"]= username 
            return redirect(f"/users/{username}")
        else:
            flash("Wrong username or password!")
            return redirect("/login")
    
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.pop["username"]
    return redirect("/")


@app.route("/users/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first()
    feedbacks =Feedback.query.filter_by(username=username).all()

    return render_template("profile.html", user=user, feedbacks=feedbacks)
 
@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Remove User from the db"""
    user = User.query.filter_by(username=username).first()

    if (user and session.get("username")== username):
        Feedback.query.filter_by(username=username).delete()

        db.session.delete(user)
        db.session.commit()

        session.pop("username")
        return redirect("/")
    
    return redirect("/")

    
@app.route("/users/<username>/feedback/add", methods=["GET","POST"])
def display_feedback_form(username):
    """Show form for adding feedback """
    user = User.query.filter_by(username=username).first()

    if (user and session.get("username")== username):
        form = FeedbackForm()

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            new_feedback = Feedback(title=title,content=content,username=username)
            db.session.add(new_feedback)
            db.session.commit()

            return redirect(f"/users/{username}")
        
        flash("You filled out the form wrong!")
        return render_template("feedback.html", form=form)
    
    flash("You are not logged in!")
    return redirect("/login")

@app.route("/feedback/<int:feedback_id>/update",methods=["GET","POST"])
def display_fb_form(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    user = session.get("username")

    if(feedback.username == user.username): 
        if request.method == "POST":
            # Update the feedback content based on the form data
            feedback.title = request.form["title"]
            feedback.content = request.form["content"]
        
            # Commit the changes to the database
            db.session.commit()

            return redirect(f"users/{user}")
        return render_template("feedback_update.html", feedback=feedback)
    

@app.route("/feedback/<int:feedback_id>/delete")
def delete_specific_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    user = session.get("username")

    if(feedback.username == user):
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f"users/{user.username}")


    
