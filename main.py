from flask import Flask,render_template,redirect,url_for,abort,request
from flask_bootstrap import Bootstrap5
from forms import LoginForm,RegisterForm,CommentForm,DatabaseForm
from flask_ckeditor import CKEditor

from flask_login import LoginManager,UserMixin,login_user,logout_user,current_user
from werkzeug.security import generate_password_hash, check_password_hash


from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.orm import relationship,DeclarativeBase,Mapped,mapped_column
from sqlalchemy import Integer, String, Float

from flask_gravatar import Gravatar

import random
import requests
from datetime import datetime
import os
from functools import wraps

logged_in = 0
not_registering = 1
current_user_id = 0
user_obj = None

app =  Flask(__name__)

ckeditor = CKEditor(app)

class Base(DeclarativeBase):
    pass

database = SQLAlchemy(model_class=Base)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return database.session.get(User,user_id)

def admin_only(function):
    @wraps(function)
    def wrapper(*args,**kwargs):
        if current_user.id != 1:
            return abort(404)
        return function(*args,**kwargs)
    return wrapper


app.config['SECRET_KEY']="mrpvproject"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI',"sqlite:///polling.db")

database.init_app(app) 

bootstrap_app = Bootstrap5(app)

#Creating tables
class User(UserMixin, database.Model):
    __tablename__ = "user"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    icon : Mapped[str]= mapped_column(String(500))
    username : Mapped[str]= mapped_column(String(50))
    email : Mapped[str]= mapped_column(String(50))
    password : Mapped[str]= mapped_column(String(50))
    created: Mapped[str] = mapped_column(String(50), nullable=True)
    
    comments = relationship("Comment",back_populates = "comment_author")
    subcomments = relationship("Subcomment",back_populates = "subcomment_author")

    
class Comment(database.Model):
    __tablename__ = "Comment"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    upvote : Mapped[int] = mapped_column(Integer, nullable=True) #make it false later
    downvote : Mapped[int] = mapped_column(Integer, nullable=True)
    body : Mapped[str] = mapped_column(String(5000))
    head : Mapped[str] = mapped_column(String(150))
    bg_image : Mapped[str] = mapped_column(String(900), nullable=True) 
    userId : Mapped[int] = mapped_column(Integer, database.ForeignKey("user.id"))
    
    comment_author = relationship("User", back_populates="comments")
    
class Subcomment(database.Model):
    __tablename__ = "Subcomment"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    body : Mapped[str] = mapped_column(String(5000))
    user_id : Mapped[str] = mapped_column(Integer, database.ForeignKey("user.id"))
    subcomment_author = relationship("User", back_populates="subcomments")
    
class icon(database.Model):
    __tablename__ = "icon"
    id : Mapped[int] = mapped_column(Integer,primary_key = True)
    link: Mapped[str] = mapped_column(String(500))


with app.app_context():
    database.create_all()

@app.route('/register',methods = ['GET','POST'])
def register():
    global not_registering,current_user_id,user_obj,logged_in
    not_registering = 0
    register_form_object = RegisterForm()
    print("this is registering")
    if register_form_object.validate_on_submit():
        entred_email = request.form.get('email')
        print("this part")
        user_email = database.session.execute(database.select(User).where(User.email == entred_email)).scalar()
        if user_email == None:
            hashed_password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256',salt_length=8)
            icons = [i for i in database.session.execute(database.select(icon)).scalars().all()]
            selected_icon = "https://www.svgrepo.com/show/384674/account-avatar-profile-user-11.svg" if len(icons) == 0 else random.choice(icons).link
            print(selected_icon)
            new_user = User(
                username = register_form_object.username.data,
                icon = selected_icon,
                email = register_form_object.email.data,
                password = hashed_password,
                created = datetime.now().strftime("%Y-%m-%d")
            )
            user_obj = new_user
            logged_in = 1
            print("here !!!!!!!")
            current_user_id = user_obj.id
            database.session.add(new_user)
            database.session.commit()
            login_user(new_user)
            print("user added sucessfully")
            
            return redirect(url_for("home"))
        else:
            error = "This account already exists, Please try another one"
            return render_template('register.html',
                                   logged_in = logged_in,
                                   register_form = register_form_object,
                                   error = error)
    return render_template('register.html', 
                        register_form = register_form_object, 
                        not_registering = not_registering)


@app.route('/login_user',methods = ['GET','POST'])
def login():
    global logged_in,user_obj,current_user_id
    form_instance = LoginForm()
    if form_instance.validate_on_submit():
        entred_email = request.form.get('email')
        user = database.session.execute(database.select(User).where(User.email == entred_email)).scalar()
        if user != None:
            entered_password = request.form.get('password')
            if check_password_hash(user.password, entered_password):
                login_user(user)
                logged_in = 1
                print(f"login method logged_in = {logged_in}")
                current_user_id = user.id
                print(f"here!!!!!!!!! {current_user_id}")
                user_obj = user
                return redirect(url_for('home'))
            else:
                print("wrong pass")
                error = "Wrong password"
                return render_template('index.html',
                           login_form = form_instance,                           
                           user_obj = user_obj,
                           logged_in = logged_in,
                           current_user_id = current_user_id,                          
                           error = error)
        else:
            print("no account")
            error = "No account by this name"
            print(current_user_id)
            return render_template('index.html',
                           login_form = form_instance,                           
                           user_obj = user_obj,
                           logged_in = logged_in,
                           current_user_id = current_user_id,                          
                           error = error)    
    return redirect(url_for('home'))

@app.route('/') 
def home():
    global current_user_id,logged_in,user_obj
    all_comments = database.session.execute(database.select(Comment)).scalars().all()
    login_form_object = LoginForm()
    quote = random.choice(requests.get(url = "https://type.fit/api/quotes").json())
    quote_text = f"'{quote['text']}' - {quote['author'].split(',')[0]}"
    print(f"current user id is ---> {current_user_id}")
    return render_template('index.html',
                           quote = quote_text,
                           user_obj = user_obj,
                           logged_in = logged_in,
                           login_form = login_form_object, 
                           current_user_id = current_user_id,
                           comments = all_comments)

@app.route('/logout')
def logout():
    global logged_in, current_user_id
    logged_in = 0
    current_user_id = 0
    logout_user()
    return redirect(url_for('home'))


    
@app.route('/profile')
def profile():
    return render_template('profile.html',
                           user_obj = user_obj,
                           logged_in = logged_in,
                           current_user_id = current_user_id)
    
@app.route('/new_comment',methods = ['GET','POST'])
def new_comment():
    login_form_object = LoginForm()
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        new_comment = Comment(
            head = comment_form.head.data,
            body = comment_form.body.data,
            bg_image = comment_form.bg_image.data,
            userId = current_user.id 
        )
        database.session.add(new_comment)
        database.session.commit()
        return redirect(url_for("home"))
    return render_template('new_comment.html',
                           comment_form = comment_form,
                           logged_in = logged_in,
                           user_obj = user_obj,
                           login_form = login_form_object,
                           current_user_id = current_user_id) 

@app.route('/comment/<int:comment_id>')
def show_comment(comment_id):
    global logged_in
    chosen_comment = database.session.execute(database.select(Comment).where(Comment.id == comment_id)).scalar()
    print(chosen_comment.bg_image)
    return render_template('show_comment.html',
                           logged_in = logged_in,
                           user_obj = user_obj,
                           comment = chosen_comment)
  
@app.route('/contact')
def contact():
    login_form_object = LoginForm()
    return render_template('contact.html',
                           user_obj = user_obj,
                           logged_in = logged_in,
                           current_user_id = current_user_id,
                           login_form = login_form_object)

@app.route('/about')
def about():
    login_form_object = LoginForm()
    return render_template('about.html',
                           user_obj = user_obj, 
                           logged_in = logged_in,
                           current_user_id = current_user_id,
                           login_form = login_form_object)


@app.route('/db',methods = ['POST','GET'])
@admin_only
def database_control():
    database_form = DatabaseForm()
    if database_form.validate_on_submit():
        new_icon = icon(link = database_form.icon_link.data)
        database.session.add(new_icon)
        database.session.commit()
    return render_template('database_control.html',
                           database_form = database_form,
                           user_obj = user_obj,
                           logged_in = logged_in,
                           current_user_id = current_user_id)

if __name__ == "__main__":
    app.run(debug=True)
