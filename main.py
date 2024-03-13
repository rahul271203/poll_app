from flask import Flask,render_template,redirect,url_for,abort,request
from flask_bootstrap import Bootstrap5
from forms import LoginForm,RegisterForm,CommentForm
from flask_ckeditor import CKEditor

from flask_login import LoginManager,UserMixin,login_user,logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.orm import relationship,DeclarativeBase,Mapped,mapped_column
from sqlalchemy import Integer, String, Float

import random
import requests
from datetime import datetime

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
    def wrapper(*args, **kwargs):
        if current_user_id != 1:
            return abort(404)
        return function
            
    return wrapper

app.config['SECRET_KEY']="mrpvproject"
app.config['SQLALCHEMY_DATABASE_URI'] = r"sqlite:///I:\My Drive\sem 4\Miniproject\semantic analysis\Polling_app\instance\polling.db"

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
    
    # Corrected the relationship definition
    # comments = relationship("Comment", backref ="comment_by")

class Comment(database.Model):
    __tablename__ = "Comment"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    upvote : Mapped[int]= mapped_column(Integer, nullable=True) #make it false later
    downvote : Mapped[int]= mapped_column(Integer, nullable=True)
    body : Mapped[str]= mapped_column(String(5000))
    head : Mapped[str]= mapped_column(String(150))
    
    # user_id : Mapped[int] = mapped_column(Integer, database.ForeignKey('user.id'))  
    # comment_by = relationship('User', backref ='Comment')
    
class icon(database.Model):
    __tablename__ = "icon"
    id : Mapped[int] = mapped_column(Integer,primary_key = True)
    link: Mapped[str] = mapped_column(String(500))


with app.app_context():
    database.create_all()

@app.route('/register',methods = ['GET','POST'])
def register():
    global not_registering,current_user_id,user_obj
    not_registering = 0
    register_form_object = RegisterForm()
    if register_form_object.validate_on_submit():
        entred_email = request.form.get('email')
        user_email = database.session.execute(database.select(User).where(User.email == entred_email)).scalar()
        if user_email == None:
            hashed_password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256',salt_length=8)
            icons = [i for i in database.session.execute(database.select(icon)).scalars().all()]
            print(icons)
            selected_icon = random.choice(icons)
            new_user = User(
                username = register_form_object.username.data,
                icon = selected_icon.link,
                email = register_form_object.email.data,
                password = hashed_password,
                created = datetime.now().strftime("%Y-%m-%d")
            )
            user_obj = new_user
            database.session.add(new_user)
            database.session.commit()
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
    global logged_in,current_user_id,user_obj
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
                user_obj = user
                return redirect(url_for('home'))
            else:
                print("wrong pass")
                error = "Wrong password"
                return render_template('index.html',
                                       current_user_id = current_user_id,
                                       logged_in = logged_in,
                                       login_form = form_instance,
                                       error = error)
        else:
            print("no account")
            error = "No account by this name"
            print(current_user_id)
            return render_template('index.html',
                                   current_user_id = current_user_id,
                                   logged_in = logged_in,
                                   login_form = form_instance,
                                   error = error)    
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    global logged_in, current_user_id
    logged_in = 0
    current_user_id = 0
    logout_user()
    return redirect(url_for('home'))

@app.route('/')
def home():
    global current_user_id,logged_in,user_obj
    login_form_object = LoginForm()
    quote = random.choice(requests.get(url = "https://type.fit/api/quotes").json())
    quote_text = f"'{quote['text']}' - {quote['author'].split(',')[0]}"
    return render_template('index.html',
                           quote = quote_text,
                           user_obj = user_obj,
                           logged_in = logged_in,
                           login_form = login_form_object, 
                           current_user_id = current_user_id)
    
@app.route('/profile')
def profile():
    return render_template('profile.html',
                           user_obj = user_obj)
    
@app.route('/new_comment',methods = ['GET','POST'])
def new_comment():
    comment_form = CommentForm()
    login_form_object = LoginForm()
    if comment_form.validate_on_submit():
        new_comment = Comment(
            head = comment_form.head.data,
            body = comment_form.body.data
        )
        database.session.add(new_comment)
        database.session.commit()
        print("user added sucessfully")
        return redirect(url_for("home"))
    return render_template('new_comment.html',
                           comment_form = comment_form,
                           user_obj = user_obj,
                           logged_in = logged_in,
                           login_form = login_form_object, 
                           current_user_id = current_user_id) 
    
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')




if __name__ == "__main__":
    app.run(debug=True)