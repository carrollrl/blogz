from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
# import os
# import jinja2

# template_dir = os.path.join(os.path.dirname(__file__), 'templates')
# jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.args.get('id'):
        single_post_id = int(request.args.get('id'))
        single_post = Blog.query.get(single_post_id)
        return render_template('single_post.html', single_post=single_post)
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
            newblog = Blog(title, body)
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