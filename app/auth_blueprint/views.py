from flask import render_template, flash, request, url_for, redirect
from flask_login import login_user, logout_user, current_user
from . import auth
from .forms import LogInForm
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
