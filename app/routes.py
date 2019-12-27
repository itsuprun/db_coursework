from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, ContactForm, SearchForm, OrderForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Product, Category, Productphoto, Order, Orderproduct
from app.email import send_password_reset_email, send_contact_form_email
from sqlalchemy import desc, asc
import math

@app.route('/')
def static_file():
	return app.send_static_file('login.html')

@app.route('/index', methods=['GET', 'POST'])
#@login_required
def index():
	bestSellerPhotos = Productphoto.query.filter_by(photo_status = 2).all()
	old_banner = Productphoto.query.filter_by(photo_status = 3).first().photo_link
	form = SearchForm()
	if form.validate_on_submit():
		searchData = form.search.data
		return redirect(url_for('product', page = 1, filter = 'search', data = searchData))
	return render_template('index.html', title='Home', bestSellerPhotos = bestSellerPhotos[0:4], old_banner = old_banner, form = form)

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
		user_order = Order(user_id = current_user.id, phone_number = '', adress = '')
		db.session.add(user_order)
		db.session.commit()
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

@app.route('/product/<page>', defaults = {'filter': None}, methods = ['GET','POST'])
@app.route('/product/<page>/<filter>', defaults = {'data': None}, methods = ['GET','POST'])
@app.route('/product/<page>/<filter>/<data>', methods = ['GET','POST'])
def product(page, filter = None, data = None):
	if filter == None:
		listOfProduct = Product.query.all()
	elif filter == 'old':
		oldProductPhotos = Productphoto.query.filter_by(photo_status = 3).all()
		listOfProduct = []
		for photo in oldProductPhotos:
			listOfProduct.append(photo.photo)
	elif filter == 'search':
		listOfProduct = Product.query.filter(Product.name.like('%{}%'.format(data))).all()	
	listOfProducts = listOfProduct*20
	productsStore = [[[0 if i+j*9+k*3 >= len(listOfProducts) else listOfProducts[i+j*9+k*3] for i in range(3)] for k in range(3)] for j in range(math.ceil(len(listOfProducts)/9))]
	numberOfPages = len(productsStore)
	products = productsStore[int(page)-1]
	categories = Category.query.all()
	form = SearchForm()
	if form.validate_on_submit():
		searchData = form.search.data
		return redirect(url_for('product', page = 1, filter = 'search', data = searchData))
	return render_template('product.html', categories = categories, products = products, zip=zip,
	 numberOfPages = numberOfPages, page = int(page), filter = filter, data = data, form=form)



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

@app.route('/error404')
def error_404():
	return render_template('404.html')

@app.route('/checkout', defaults = {'orderedProductId': None}, methods = ['GET','POST'])
@app.route('/checkout/<orderedProductId>', defaults = {'deleteProductId': None}, methods = ['GET','POST'])
@app.route('/checkout/<orderedProductId>/<deleteProductId>', methods = ['GET','POST'])
@login_required
def checkout(orderedProductId = None, deleteProductId = None):
	if (orderedProductId != None and orderedProductId != 'delete'):
		order_id = current_user.orders.filter_by(user_id = current_user.id).order_by(desc(Order.timestamp)).first().id
		p = Orderproduct(product_id = orderedProductId, order_id = order_id)
		db.session.add(p)
		db.session.commit()
	if deleteProductId != None:
		product_to_delete = Orderproduct.query.filter_by(id = deleteProductId).first()
		db.session.delete(product_to_delete)
		db.session.commit()	
	current_order = current_user.orders.filter_by(user_id = current_user.id).order_by(desc(Order.timestamp)).first()
	ordered_products_list = Orderproduct.query.filter_by(order_id = current_order.id).all()
	return render_template('checkout.html', ordered_products_list = ordered_products_list,len = len, zip = zip)

@app.route('/order/<current_order>', methods = ['GET','POST'])
@login_required
def order(current_order):
	form = OrderForm()
	current_order = Order.query.filter_by(id = current_order).first()
	if form.validate_on_submit():
		current_order.adress = form.adress.data
		current_order.phone_number = form.phone.data
		db.session.commit()
		return redirect(url_for('order_submit'))
	return render_template('order.html', form = form)

@app.route('/order_submit')
@login_required
def order_submit():
	return render_template('order_submit.html')