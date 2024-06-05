from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import String  # Import String type
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os


# flask instance
app = Flask(__name__)
# Add CKEditor
ckeditor = CKEditor(app)
# Add Database
# old SQLite db
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://udav7f289ske1h:pf132b76df6356e1e744b88cf56f8a5e9e57e464de21548c8073803288ccf3a8d@cd5vlri6nnqe17.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d2gs7cosuafj1s?sslmode=require'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://udav7f289ske1h:pf132b76df6356e1e744b88cf56f8a5e9e57e464de21548c8073803288ccf3a8d@cd5vlri6nnqe17.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d2gs7cosuafj1s'
db_uri = os.getenv('DATABASE_URI', 'sqlite:///default.db')
# new mySQL dB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@db/our_users'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
# secret key
app.config['SECRET_KEY'] = "my super secret key"
# DB initialization

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# flask login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

# pass stuff to navbar
@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)

# create admin page
@app.route('/admin')
@login_required
def admin():
	id = current_user.id
	if id == 15:
		return render_template("admin.html")
	else:
		flash("You Must Be The Admin To Access This Page")
		return redirect(url_for('dashboard'))

# create a search function
@app.route('/search', methods=["POST"])
def search():
	form = SearchForm()
	posts = Posts.query
	if form.validate_on_submit():
		# Get data from submitted form
		post.searched = form.searched.data
		# Query the database
		posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
		posts = posts.order_by(Posts.title).all()

		return render_template("search.html",
			form=form,
			searched=post.searched,
			posts = posts)


# create a login page
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			# check hash
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash("Login Successful!")
				return redirect(url_for('dashboard'))
			else:
				flash("Wrong Password, Try Again")
		else:
			flash("User Doesn't Exist")


	return render_template('login.html', form=form)

# create logout Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You Have Been logged Out")
	return redirect(url_for('login'))

# create a dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
	form = UserForm()
	id = current_user.id
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favourite_color = request.form['favourite_color']
		name_to_update.username = request.form['username']
		name_to_update.about_author = request.form['about_author']
		name_to_update.profile_pic = request.files['profile_pic']


		# grab image name
		pic_filename = secure_filename(name_to_update.profile_pic.filename)
		# set UUID
		pic_name = str(uuid.uuid1()) + "_" + pic_filename
		# save the image
		saver = request.files['profile_pic']
		

		# change into a string to save to db
		
		name_to_update.profile_pic = pic_name
		try:
			db.session.commit()
			name_to_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER']), pic_name)
			flash("User Updated Successfully")
			return render_template("dashboard.html",
				form=form,
				name_to_update=name_to_update)
		except:
			flash("Error looks like there was a problem")
			return render_template("dashboard.html",
				form=form,
				name_to_update=name_to_update)
	else:
		return render_template("dashboard.html",
			form=form,
			name_to_update=name_to_update,
			id = id)
	return render_template('dashboard.html')



@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)
	id = current_user.id
	if id == post_to_delete.poster.id:
		try:
			db.session.delete(post_to_delete)
			db.session.commit()

			# return a message
			flash("Blog Post Deleted!")

			posts = Posts.query.order_by(Posts.date_posted)
			return render_template("posts.html", posts=posts)

		except:
			# return an error message
			flash("Whoops, There Was A Problem Deleting The Post")

			posts = Posts.query.order_by(Posts.date_posted)
			return render_template("posts.html", posts=posts)
	else:
		# return a message
		flash("You Aren't Authorized To Delete That Post")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)

@app.route('/posts')
def posts():
	# grab all the posts from the database
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", posts=posts)


@app.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template('post.html', post=post)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		#post.author = form.author.data
		post.slug = form.slug.data
		post.content = form.content.data
		# Update Database
		db.session.add(post)
		db.session.commit()
		flash("Post Has Been Updated!")
		return redirect(url_for('post', id=post.id))

	if current_user.id == post.poster_id:
		form.title.data = post.title
		#form.author.data = post.author
		form.slug.data = post.slug
		form.content.data = post.content
		return render_template('edit_post.html', form=form)
	else:
		flash("You Aren't Authorized To Edit This Post!")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)


# add post page
@app.route('/add-post', methods=['GET','POST'])
### @login_required
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		poster = current_user.id
		post = Posts(title=form.title.data, content=form.content.data,poster_id=poster, slug=form.slug.data)
		# clear the form
		form.title.data = ''
		form.content.data = ''
		#form.author.data = ''
		form.slug.data = ''

		# add post data to Database
		db.session.add(post)
		db.session.commit()

		# return a message
		flash("Blog Post Submitted Successfully!")

	# redirect to the web page
	return render_template("add_post.html", form=form)

# JSON thing
@app.route('/date')
def get_current_date():
	favourite_pizza = {
		"John": "Pepperoni",
		"Mary": "Cheese",
		"Tim": "Mushroom"
	}
	return favourite_pizza
	#return {"Date": date.today()}




@app.route('/delete/<int:id>')
def delete(id):
	user_to_delete = Users.query.get_or_404(id)
	name = None
	form = UserForm()

	try:
		db.session.delete(user_to_delete)
		db.session.commit()
		flash("User Deleted Successfully")

		our_users = Users.query.order_by(Users.date_added)
		return render_template("add_user.html",
				form=form,
				name=name,
				our_users=our_users)

	except:
		flash("Oops, there was a problem deleting this user")
		return render_template("add_user.html",
				form=form,
				name=name,
				our_users=our_users)




#update database record
@app.route('/update/<int:id>', methods=['GET','POST'])
@login_required
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favourite_color = request.form['favourite_color']
		name_to_update.username = request.form['username']
		try:
			db.session.commit()
			flash("User Updated Successfully")
			return redirect(url_for('dashboard'))
		except:
			flash("Error looks like there was a problem")
			return render_template("update.html",
				form=form,
				name_to_update=name_to_update)
	else:
		return render_template("update.html",
			form=form,
			name_to_update=name_to_update,
			id = id)





#def index():
#	return "<h1>Hello World!</h1>"


#FILTERS!

#safe
#capitalize
#lower
#upper
#title
#trim
#striptags
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			# hash the password
			hashed_pw = generate_password_hash(form.password_hash.data, "pbkdf2:sha256")
			user = Users(username = form.username.data, name=form.name.data, email=form.email.data, favourite_color=form.favourite_color.data, password_hash=hashed_pw)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data  = ''
		form.username.data = ''
		form.email.data = ''
		form.favourite_color.data = ''
		form.password_hash = ''


		flash("User Added Successfully")
	our_users = Users.query.order_by(Users.date_added)
	return render_template("add_user.html",
			form=form,
			name=name,
			our_users=our_users)

# create route decotator
@app.route('/')
def index():
	first_name = "John"
	stuff = "This is bold text"

	favourite_pizza = ["Pepperoni","Cheese","Mushrom",41]
	return render_template("index.html",
		first_name=first_name,
		stuff=stuff,
		favourite_pizza=favourite_pizza)

# localhost:5000/user/John
@app.route('/user/<name>')

def user(name):
	return render_template("user.html", user_name=name)

#Create custom error page

#invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# internal server error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500

# create password test page
@app.route('/test_pw', methods=['GET','POST'])
def test_pw():
	email = None
	password = None
	pw_to_check = None
	passed = None
	form = PasswordForm()

	# validate form
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		# clear the form
		form.email.data = ''
		form.password_hash.data = ''

		# lookup user by email
		pw_to_check = Users.query.filter_by(email=email).first()

		# check hashed password
		passed = check_password_hash(pw_to_check.password_hash, password)

	return render_template("test_pw.html",
		email = email,
		password = password,
		pw_to_check = pw_to_check,
		passed = passed,
		form = form)

# create name page
@app.route('/name', methods=['GET','POST'])
def name():
	name = None
	form = NamerForm()
	# validate form
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form Submitted Successfully!")

	return render_template("name.html",
		name = name,
		form = form)



# create a blog post Model
class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(255))
	content = db.Column(db.Text)
	#author = db.Column(db.String(255))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(255))
	# foreign key to link users (refers to the primary key of the users)
	poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# Create Model
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False, unique=True)
	name = db.Column(db.String(200), nullable=False)
	email = db.Column(db.String(120), nullable=False, unique=True)
	favourite_color = db.Column(db.String(120))
	about_author = db.Column(db.Text(), nullable=True)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	profile_pic = db.Column(db.String(120), nullable=True)
	# Do some password stuff
	password_hash = db.Column(db.String(120))
	# User Can Have Many Posts (1 to M)
	posts = db.relationship('Posts', backref='poster')

	@property
	def password(self):
		raise AttributeError('Password is not a readable attribute!')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	# Create a String
	def __repr__(self):
		return '<Name %r>' % self.name
