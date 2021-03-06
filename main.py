from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&xP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    deleted = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner_name = db.Column(db.String(120))

    def __init__(self, title, body, owner, owner_name):
        self.title = title
        self.body = body
        self.deleted = False
        self.owner = owner
        self.owner_name = owner_name

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    username = db.Column(db.String(120))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.username = email.split("@")[0]

#TODO undo these comments for login funcitonality
@app.before_request
def require_login():
    allowed_routes = ["login", "register", "blog"]

    if request.endpoint not in allowed_routes and "email" not in session:
        return redirect('/login')

@app.route("/blog", methods=["POST", "GET"])
def blog():
    blogs = Blog.query.filter_by(deleted=False).all()
    return render_template("blog.html", title="Blogz", blogs=blogs, main=True)

@app.route("/newpost", methods = ["POST", "GET"])
def newpost():
    if request.method == "POST":
        owner = User.query.filter_by(email=session["email"]).first()
        owner_name = owner.username
        title = request.form["title"]
        blog = request.form["body"]
        if title == "" or blog == "":
            flash("Please enter a title and a blog")
            return redirect("/newpost") 
        new_blog = request.form["title"]
        body = request.form["body"]
        new_blog = Blog(new_blog, body, owner, owner_name)
        db.session.add(new_blog)
        db.session.commit()
        return redirect("/blogpost?id={}".format(new_blog.id))        
    return render_template("newpost.html")

@app.route('/register', methods = ["POST", "GET"])
def register():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form['password']
        verify = request.form['verify']

        if password != verify:
            flash("Please ensure password and verification match")
            return redirect('/register')
        else:

            existing_user = User.query.filter_by(email = email).first()
            if not existing_user:
                new_user = User(email,password)
                db.session.add(new_user)
                db.session.commit()
                session["email"] = email
                return redirect('/')
            else:
                flash("Username has already been taken")
                return redirect("/register")

    return render_template('register.html')

@app.route('/login', methods = ["POST", "GET"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form['password']
        user = User.query.filter_by(email = email).first()
        if user and user.password == password:
            session["email"] = email
            flash("Logged in")
            return redirect('/blog')
        else:
            flash("User password incorrect, or user does not exist", "error")

    return render_template('login.html')

@app.route("/blogpost", methods=["POST", "GET"])
def blogpost():
    id = request.args.get("id")
    blog = Blog.query.filter_by(id=id).first()
    return render_template("blogpost.html", title=blog.title, body=blog.body)

@app.route("/myblog")
def myBlog():
    owner = User.query.filter_by(email=session["email"]).first()
    blogs = Blog.query.filter_by(deleted=False, owner=owner).all()
    username = owner.email.split("@")[0]
    return  render_template("blog.html", title="{}'s blog".format(username), blogs = blogs, username = username)

@app.route('/')
def index():
    users = User.query.all()
    return render_template("index.html", users = users)

@app.route("/userblog")
def userBlog():
    user=request.args.get('user')
    owner = User.query.filter_by(id= user).first()
    blogs = Blog.query.filter_by(deleted=False, owner=owner).all()
    username = owner.email.split('@')[0]
    return render_template("blog.html", title="{}'s blog".format(username), blogs = blogs, username = username)

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

if __name__ == '__main__':
    app.run()