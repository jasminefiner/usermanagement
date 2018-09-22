from flask import render_template, flash, request, url_for, redirect
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from . import auth
from .forms import LogInForm, RegistrationForm
from .. import db, mail
from ..models import User

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LogInForm()
    if current_user.is_authenticated:
        flash('You are already logged in!', 'warning')
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        # get email and password from the form if it is validated
        email = form.email.data
        password = form.password.data

        # Find the user with the email address given in the form
        user = User.query.filter_by(email=email).first()

        if user and user.verify_password(password):
            # If the user exists, log in the user
            # redirect to the main index
            login_user(user)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            flash('You have been logged in!', 'success')
            return redirect(next)
        flash('Invalid email or password.', 'danger')
    # log errors from the form if it doesn't validate
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'warning')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first() is not None:
            # Email has already been used
            flash('A user with that email address has already registered.', 'danger')
            return redirect(url_for('auth.register'))
        elif User.query.filter_by(username=form.username.data).first() is not None:
            # Username has already been used
            flash('Username is taken.', 'danger')
            return redirect(url_for('auth.register'))

        # form is validated and all good. Create the user.
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        # Generate confirmation token
        token = user.generate_confirmation_token()

        # Send confirmation token to user via email
        # Create instance of message
        msg = Message()
        msg.recipients = [user.email]
        msg.subject = 'Account Confirmation'
        msg.html = render_template('auth/email/account_confirmation.html', user=user, token=token)
        mail.send(msg)
        flash('You have successfully registered. Please check your email to confirm your account.', 'success')
        return redirect(url_for('auth.login'))
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')
    return render_template('auth/register.html', form=form, current_user=current_user)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash('Your account is already confirmed.', 'warning')
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have successfully confirmed your account.', 'success')
    else:
        flash('Invalid confirmation token. Your token has either expired or is invalid.')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed and request.blueprint != 'auth' and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        flash('You are confirmed!', 'success')
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', user=current_user)

@auth.route('/confirm')
@login_required
def resend_confirmation():
    if current_user.confirmed:
        flash('You are already confirmed. No need to send new link.', 'success')
        return redirect(url_for('main.index'))
    token = current_user.generate_confirmation_token()
    # Send confirmation token to user
    msg = Message()
    msg.recipients = [current_user.email] # this will be user.email
    msg.html = render_template('auth/email/account_confirmation.html', user=current_user, token=token)
    mail.send(msg)

    flash('A new confirmation token email has been send to you.', 'success')
    return redirect(url_for('main.index'))
