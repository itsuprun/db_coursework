from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, ContactForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Product, Category, Productphoto
from app.email import send_password_reset_email, send_contact_form_email
import math

@app.route('/')
def static_file():
	return app.send_static_file('login.html')

@app.route('/index')
#@login_required
def index():
	user = {'username': 'Miguel'}
	posts = [
		{
			'author': {'username': 'John'},
			'body': 'Beautiful day in Portland!'
		},
		{
			'author': {'username': 'Susan'},
			'body': 'The Avengers movie was so cool!'
		}
	]
	bestSellerPhotos = Productphoto.query.filter_by(photo_status = 2).all()
	return render_template('index.html', title='Home', posts=posts, bestSellerPhotos = bestSellerPhotos[0:4])

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		#next_page = request.args.get('next')
		#if not next_page or url_parse(next_page).netloc != '':
		#    next_page = url_for('index')
		#return redirect(next_page)
		return redirect(url_for('index'))
	return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/product/<page>')
def product(page):
	listOfProduct = Product.query.all()
	listOfProducts = listOfProduct*20
	productsStore = [[[0 if i+j*9+k*3 >= len(listOfProducts) else listOfProducts[i+j*9+k*3] for i in range(3)] for k in range(3)] for j in range(math.ceil(len(listOfProducts)/9))]
	numberOfPages = len(productsStore)
	products = productsStore[int(page)-1]
	categories = Category.query.all()
	return render_template('product.html', categories = categories, products = products, zip=zip,
	 numberOfPages = numberOfPages, page = int(page))



@app.route('/single/<productName>')
@login_required
def single(productName):
	product = Product.query.filter_by(name = productName).first_or_404()
	photos = Productphoto.query.filter_by(product_id = product.id).filter_by(photo_status = 0).all()
	relativeProducts = Product.query.filter_by(category_id = product.category_id).all()
	relativePhotos = []
	for prod in relativeProducts:
		relativePhotos.append(prod.photos.filter_by(product_id = prod.id).filter_by(photo_status = 1).first())
	return render_template('single.html', product = product, photos = photos, relativePhotos = relativePhotos[0:4])


@app.route('/contact', methods=['GET', 'POST'])
def contact():
	form = ContactForm()
	if form.validate_on_submit():
		send_contact_form_email(form.username.data,form.email.data,form.text.data)
		flash('Your message sended. Wait for an answer!')
		return redirect(url_for('index'))
	return render_template('contact.html', form = form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)