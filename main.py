from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner_id')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_variable = User.query.filter_by(username=username).first()
        if user_variable and user_variable.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            return redirect('/login')

    return render_template('login.html')



@app.route('/logout', methods=['POST', 'GET'])
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/index', methods=['POST', 'GET'])
def index():
    username_list = User.query.all()
    return render_template('index.html', username_list=username_list) 
    

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            username_error = ""
            password_error = ""
            verify_error = ""

            if len(username) == 0:
                username_error = "Don't forget to enter a username."
                username = ""
            elif len(username) < 3:
                    username_error = "Usernames must be at least 3 characters long."
                    username = ""

            if len(password) == 0:
                password_error = "Don't forget to enter a password."
                password = ""
            elif len(password) < 3:
                    password_error = "Passwords must be at least 3 characters long."

            if verify != password:
                verify_error = "Ooops, your passwords do not match."

            if not username_error and not password_error and not verify_error:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')

            else:
                return render_template('signup.html', username_error=username_error,password_error=password_error, verify_error=verify_error, username=username, password='', verify='')

        else:
            flash('That username already exists.', 'error')
            return redirect('/signup')

    else:
        return render_template('signup.html')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.args.get('user'):
        single_user_variable = request.args.get('user')
        blog_entries = Blog.query.filter_by(owner=single_user_variable).all()
        return render_template('singleUser.html', blog_entries=blog_entries)
    
    if request.args.get('blog'):
        single_post_id = request.args.get('blog')
        single_post = Blog.query.filter_by(id=single_post_id).first()
        return render_template('single_post.html', blog=single_post)

    blog_entries = Blog.query.all()
    return render_template('blog_listing.html', blog_entries=blog_entries)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        username = session['username']
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=username).first()
        if owner:
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
            else:
                return render_template('newpost.html', title=title, body=body, title_error=title_error, body_error=body_error)

        else:
            flash('Error, please try again', 'error')
            return redirect('/newpost')
                

    else:
        return render_template('newpost.html')


if __name__ == '__main__':
    app.run()