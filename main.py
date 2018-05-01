from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    pw_hash = db.Column(db.String(200))
    blogs = db.relationship('Blog', backref='owner', lazy='joined')

    def __init__(self, username, pw_hash):
        self.username = username
        self.pw_hash = make_pw_hash(password)


@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return render_template('login.html')


@app.route('/index', methods=['POST', 'GET'])
def index():
    username_list = User.query.all()
    return username_list


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        username_error = ""
        password_error = ""
        verify_error = ""

        if len(username) == 0:
            username_error = "Don't forget to enter a username."
            username = ""
        else:
            if len(username) < 3:
                username_error = "Usernames must be at least 3 characters long."
                username = ""

        if len(password) == 0:
            password_error = "Don't forget to enter a password."
            password = ""
        else:
            if len(password) < 3:
                password_error = "Passwords must be at least 3 characters long."

        if verify != password:
            verify_error = "Ooops, your passwords do not match."

        # validation
        if not username_error and not password_error and not verify_error:
            if not existing_user:
                new_user = User(username, pw_hash)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost?username={0}'.format(new_user))
            else:
                return render_template('signup.html', username=username, password=password, verify=verify, username_error=username_error, password_error=password_error, verify_error=verify_error)
                
        else:
            return render_template('signup.html', username_error=username_error, password_error=password_error, verify_error=verify_error, username=username, password='', verify='')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and check_pw_hash(password, username.pw_hash):
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            return redirect('/login')

    return render_template
    

@app.route('/logout', methods=['POST'])
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.args.get('id'):
        single_post_id = int(request.args.get('id'))
        single_post = Blog.query.get(single_post_id)
        return render_template('single_post.html', single_post=single_post)

    if request.args.get('user'):
        single_user_variable = request.args.get('user')
        single_user = Blog.query.get(single_user_variable)
        return render_template('singleUser.html')
    
    else:
        blog_entries = Blog.query.all()
        return render_template('blog_listing.html', blog_entries=blog_entries)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        title_error = ''
        body_error = ''

        if len(title) == 0:
            title_error = "You have to add a title."

        if len(body) == 0:
            body_error = "You have to add some text to this blog post."

        if not title_error and not body_error:
            newblog = Blog(title, body, owner)
            db.session.add(newblog)
            db.session.commit()
            return redirect('/blog?id='+str(newblog.id))
            # this is the url. stuff in "" is static,
            # concatenated with newblog with attribute 'id'.
            # redirects to /blog with newblog id, python knows
            # that the id info is already contained there.
        else:
            return render_template('newpost.html', title=title, body=body, title_error=title_error, body_error=body_error)
    
    return render_template('newpost.html')


if __name__ == '__main__':
    app.run()