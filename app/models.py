from flask import current_app
from app import db, login_manager
from flask_login import UserMixin
from itsdangerous import JSONWebSignatureSerializer
from hashlib import md5

from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(80))
    confirmed = db.Column(db.Boolean, default=False)
    # User profile attributes
    name = db.Column(db.String(120))
    age = db.Column(db.Integer())
    location = db.Column(db.String(120))
    bio = db.Column(db.Text())

    def avatar(self, size=100, default='identicon', rating='g'):
        hash = md5(self.email.lower().encode('utf-8')).hexdigest()
        url = 'https://secure.gravatar.com/avatar'
        return ('{url}/{hash}?s={size}&d={default}&r={rating}'
                .format(url=url,
                        hash=hash,
                        default=default,
                        size=size,
                        rating=rating))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def change_password(self, new_password):
        self.password_hash = generate_password_hash(new_password)

    def generate_password_reset_token(self, expiration=3600):
        s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'reset_password': self.id}).decode('utf-8')

    @staticmethod
    def password_reset(token, new_password):
        s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset_password'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'change_email': self.id,
                        'new_email': new_email}).decode('utf-8')

    def email_change(self, token):
        s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('change_email'))
        new_email = data.get('new_email')
        if user is None:
            return False
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))
