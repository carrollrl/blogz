from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.args.get('id'):
        return render_template('single_post.html')
    else:
        blog_entries = Blog.query.all()
        return render_template('blog_listing.html', blog_entries=blog_entries)

    #Blog.Query.Get('id')




@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        newblog = Blog(title, body)
        db.session.add(newblog)
        db.session.commit()

    return render_template('newpost.html')



if __name__ == '__main__':
    app.run()