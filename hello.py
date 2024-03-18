from flask import Flask, render_template


# flask instance
app = Flask(__name__)

# create route decotator
@app.route('/')

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