from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo


class LogInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('password2')])
    password2 = PasswordField('Repeat Password')
    submit = SubmitField('Register')


class ChangePasswordForm(FlaskForm):
    oldpassword = PasswordField('Old Password', validators=[DataRequired()])
    newpassword = PasswordField('New Password',
                                validators=[DataRequired(),
                                            EqualTo('newpassword2')])
    newpassword2 = PasswordField('Repeat New Password',
                                 validators=[DataRequired()])
    submit = SubmitField('Change Password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    newpassword = PasswordField('New Password',
                                validators=[DataRequired(),
                                            EqualTo('newpassword2')])
    newpassword2 = PasswordField('Repeat New Password',
                                 validators=[DataRequired()])
    submit = SubmitField('Reset Password')


class EmailChangeForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Email(),
                                    EqualTo('email2')])
    email2 = StringField('Repeat Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Change Email')


class EditProfileForm(FlaskForm):
    name = StringField('Name')
    age = StringField('Age')
    location = StringField('Location')
    bio = TextAreaField('Short Bio')
    submit = SubmitField('Save Changes')
