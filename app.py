from flask import Flask, render_template, send_from_directory, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime 
from pytz import timezone
import os

# Init flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pk.db'
app.config['SECRET_KEY'] = "performance king"

# Init database
class Base(DeclarativeBase):
	pass 
db = SQLAlchemy(model_class=Base)

# Contacts model
class Contacts(db.Model):
	# Row elements
	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str]
	email: Mapped[str]
	phone: Mapped[str]
	message: Mapped[str]
	date: Mapped[str]

	# String return
	def __repr__(self):
		return f'<name, email, phone, message: {self.name}, {self.email}, {self.phone}, {self.message}>'

# Init database with app and tables
db.init_app(app)
with app.app_context():
	db.create_all()



'''
Page Routes
'''
# Index page
@app.route('/')
def index():
	return render_template('index.html')

# Admin page
@app.route('/admin')
def admin():
	return render_template('admin.html')

# Admin contacts page
@app.route('/admin_contacts')
def admin_contacts():
	# Checks that request is from login
	if f'{request.host_url}admin' == request.referrer or f'{request.host_url}admin_contacts' == request.referrer:
		# Pull contacts from database
		contact_list = Contacts.query.order_by(Contacts.date)
		for i, contact in enumerate(contact_list):
			print(f'{i}: {contact.name}, {contact.phone}, {contact.email}')

		return render_template('admin_contacts.html', contact_list=contact_list)

	return redirect('/admin')



'''
Static Routes
'''
# Static assets
@app.route('/assets/<path:path>')
def static_assets(path):
	return send_from_directory('static/assets', path)

# Static css
@app.route('/css/<path:path>')
def static_css(path):
	return send_from_directory('static/css', path)

# Static js
@app.route('/js/<path:path>')
def static_js(path):
	return send_from_directory('static/js', path)



'''
API Routes
'''
# Post contact info API
@app.route('/submit_contact_info', methods=['POST'])
def submit_contact_info():
	# Pull data sent
	name = request.form['name']
	email = request.form['email']
	phone = request.form['phone']
	message = request.form['message']
	print(f"name, email, phone, message: {name}, {email}, {phone}, {message}")

	# Enter into database
	contact = Contacts(
		name=name,
		email=email,
		phone=phone,
		message=message,
		date=datetime.now(timezone('EST'))
	)
	db.session.add(contact)
	db.session.commit()

	return redirect('/#contact')

# Post admin login API
@app.route('/admin_login', methods=['POST'])
def admin_login():
	# Pull data sent
	username = request.form['username'].strip()
	password = request.form['password'].strip()
	print(f"username, password: {username}, {password}")

	# Check username and password, go to admin_contacts page
	def_username, def_password = 'admin', 'admin123'
	if username == def_username and password == def_password:
		return redirect('/admin_contacts')

	return redirect('/admin')

# Post delete contact API
@app.route('/contact_delete', methods=['POST'])
def contact_delete():
	# Pull contact id
	id = request.form['contact_id']
	print(f'id: {id}')

	# Delete from table
	Contacts.query.filter(Contacts.id == id).delete()
	db.session.commit()

	return redirect('/admin_contacts')



# Ran directly on debug
if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5001)

