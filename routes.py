from flask import render_template, redirect, url_for, flash, request
from Purchase import app
from models import Item, User
from Purchase import db
from forms import RegisterForm, LoginForm, PurchaseItemForm
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/buy', methods=['GET', 'POST'])
@login_required
def buy_page():
    purchase_form = PurchaseItemForm()
    if request.method == "POST":
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.owner = current_user.id
                current_user.budget -= p_item_object.price
                with app.app_context():
                  db.session.commit()
                  flash(f'{p_item_object.name} purchased for {p_item_object.price}$ succesfully', category='success')
            else:
                flash(f'Insufficient balance {p_item_object.name}', category='danger')

        return redirect(url_for('buy_page'))

    if request.method == "GET":
      items = Item.query.filter_by(owner=None)
      owned_items = Item.query.filter_by(owner=current_user.id)
      return render_template('buy.html', items=items, purchase_form=purchase_form, owned_items=owned_items,)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        with app.app_context():
            db.session.add(user_to_create)
            db.session.commit()
            logout_user()
            flash(f'Account created successfully! Logged in as{user_to_create}', category='success')
            return redirect(url_for('buy_page'))
    if form.errors != {}:# no errors from validation
        for err_msg in form.errors.values():
            flash(f'Error creating user: {err_msg}', category='danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
        ):
           login_user(attempted_user)
           flash(f'Welcome : {attempted_user.username} ', category='success')
           return redirect(url_for('buy_page'))
        else:
            flash('Invalid username and password', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("Logged out successfully", category='info')
    return redirect(url_for('home_page'))
