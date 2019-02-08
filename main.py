from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:jim@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY'] = True
db = SQLAlchemy(app)
app.secret_key = "a1ll3kjl1k4nlbv1v4jh1jh5111hjvhj1cv5jh1k"


class Blogs(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blogs', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


#@app.before_request
#def require_login():
#    only_pages = ['blog', 'index', 'signup', 'login']
#    if request.endpoint not in only_pages and 'username' not in session:
#        return redirect('/login')



@app.route('/', methods=['POST', 'GET'])
def index():


    all_users = User.query.all()
    return render_template('index.html', all_users=all_users)

@app.route('/blog', methods=['POST', 'GET'])
def blog_display():

    if "username" in request.args:
        blog_id = request.args.get("username")
        blog_post = Blogs.query.get(blog_id)
        persons_blog = Blogs.query.filter_by(owner=user).all()
        return render_template('singleUser.html', page_title="user.username" + "'s Posts", persons_blog=persons_blog)

    one_post = request.args.get("id")
    if one_post:
        blog = Blogs.query.get(one_post)
        return render_template('blogentry.html', blog=blog)

    else:  
        blog = Blogs.query.all()
        return render_template('blog.html', page_title= 'All Posts', blog=blog)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():


    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        

        title_error=''
        body_error=''

        if len(title) == 0:
            title_error = "Enter a title!"
        if len(body) == 0:
            body_error == "Enter text for your post!"

        if title_error or body_error:
            return render_template('newpost.html', titlebase="New Entry", title_error= title_error, body_error=body_error, title=title, body=body)

        else:
            if len(title) and len(body) > 0:
                author = User.query.filter_by(username=session['username']).first()
                new_post = Blogs(title, body, author)
                db.session.add(new_post)
                db.session.commit()
                return redirect('/blog?id=' + str(new_post.id))

@app.route("/login", methods=['GET', 'POST'])
def login():
    name_error = ''
    pass_error = ''
    username = ''

    if request.method == 'GET':
        if 'username' not in session:
            return render_template('login.html', page_title='Login')
        else:
            return redirect('/newpost')
    
    if request.method == 'POST':
        user_login = request.form['user_login']
        user_pass  = request.form['user_pass']
        user = User.query.filter_by(username=username).first()

        if user_login and user_pass == user:
            session['username'] = user.username
            return redirect('/newpost')

        if user_login and user_pass != user:
            pass_error = "Wrong password, please try again."
            return render_template('login.html', pass_error=pass_error)

        if not user:
            name_error = "This username does not exist. Create an account!"
            return render_template('login.html', name_error=name_error, user_login = user_login)
    
    else:
        return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup_complete_form():

    user_errors = ''
    pass_error = ''
    verpass_error = ''
    username_errors = ''

    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verpass = request.form['verpass']

        if len(username) < 3 or len(username) > 20:
            user_errors = "Usernames length must be four to twenty characters!"
        
        if len(password) < 3 or len(password) > 20:
            pass_error = "Password length must be four to twenty characters!"
        
        if password != verpass:
            verpass_error = "Passwords do not match! Try Again."

        if user_errors != '' or pass_error != '' or verpass_error != '':
            return render_template('signup.html', user_errors=user_errors, pass_error=pass_error, verpass_error=verpass_error, username=username)
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            username_errors = "This username already exists! Choose a different username!"
            return render_template('signup.html', username_errors = username_errors)
        
        if not user_exists:
            user_create = User(username, password)
            db.session.add(user_create)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    else:
        return render_template('signup.html')

@app.route("/logout")
def logout():
    del session['username']
    return redirect('/')      

                
if __name__ == '__main__':
    app.run()