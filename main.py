from flask import Flask, request, redirect, render_template, session
from flask import url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'QLciVE2R1J'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


def logged_in():
    if session.get('username'):
        return True
    else:
        return False


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist')
            return redirect('/login')
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if verify == password:
            if not existing_user and len(username) > 3 and len(password) > 3:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                flash('Duplicate user! Usernames and Passwords must be at least 3 characters long!')
                return redirect('/signup')
        else:
            flash('Passwords do not match!')
            return redirect('/signup')
    return render_template('signup.html')


@app.route('/logout')
def logout():
    #if session['username'] != None:
        #del session['username']
    session.pop('username', None) # key and what to replace it with
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def blog():

    #blog_posts = Blog.query.all()
    #blog_posts = list(reversed(blog_posts))

    user = request.args.get('user')
    blog_id = request.args.get('id')

    if request.method == 'GET':
        if user != None:
            user = User.query.filter_by(username=user).first()
            blog_posts = Blog.query.filter_by(owner_id=user.id).all()
            blog_posts = list(reversed(blog_posts))
            return render_template('blog.html', blog_posts=blog_posts, user=user)
        elif blog_id != None:
            post = Blog.query.filter_by(id=blog_id).first()
            user = User.query.filter_by(id=post.owner_id).first()
            user = user.username
            return render_template('blog.html', post=post, user=user)
        else:
            blog_posts = Blog.query.all()
            user = User.query.all()
            blog_posts = list(reversed(blog_posts))
            return render_template('blog.html', blog_posts=blog_posts, user=user)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if logged_in():
        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            username = session['username']
            owner = User.query.filter_by(username=username).first()
            owner_id = owner.id
            new_post = Blog(title, body, owner_id)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog')
        else:
            return render_template('newpost.html')
    else:
        flash("You must login to post!")
        return redirect('/login')


@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


if __name__ == '__main__':
    app.run()
