import unittest
from app import create_app, db
from app.models import User

class AuthenticationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.client = self.app.test_client()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/auth/login', data = {
            'email': email,
            'password': password,
        }, follow_redirects=True)

    def register(self, email, username, password, password2):
        return self.client.post('/auth/register', data = {
            'email': email,
            'username': username,
            'password': password,
            'password2': password2
        }, follow_redirects=True)

    ### TEST LOGIN/REGISTER/LOGOUT FUNCTIONALITY

    def test_login_route(self):
        response = self.client.get('/auth/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<h1>Log In</h1>', response.get_data(as_text=True))

    def test_login(self):
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        response = self.login('john@example.com', 'cat')
        self.assertEqual(response.status_code, 200)
        self.assertIn('You have been logged in!', response.get_data(as_text=True))

    def test_bad_login(self):
        u = User(email="john@example.com", username="john", password="cat")
        db.session.add(u)

        response = self.login(u.email, 'dog')
        self.assertIn('Invalid email or password.', response.get_data(as_text=True))

        response = self.login('someemail@example.com', 'cat')
        self.assertIn('Invalid email or password.', response.get_data(as_text=True))

    def test_no_login_route_if_logged_in(self):
        u = User(email='example@example.com', username='example', password='cat')
        db.session.add(u)
        self.login(u.email, 'cat')
        response = self.client.get('/auth/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('You are already logged in!', response.get_data(as_text=True))

    def test_logout_route(self):
        response = self.client.get('auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('You have been logged out.', response.get_data(as_text=True))

    def test_register_route(self):
        response = self.client.get('/auth/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<h1>Register</h1>', response.get_data(as_text=True))

    def test_register(self):
        response = self.register(
            "john@example.com",
            "john",
            'cat',
            'cat')
        self.assertIn('You have successfully registered. Please check your email to confirm your account.', response.get_data(as_text=True))

    def test_bad_register(self):
        u = User(email='john@example.com', username='john', password='cat')
        db.session.add(u)
        response = self.register(
            'john@example.com',
            'jack',
            'cat',
            'cat'
        )
        self.assertIn('A user with that email address has already registered.', response.get_data(as_text=True))

        response = self.register(
            'jack@example.com',
            'john',
            'cat',
            'cat'
        )
        self.assertIn('Username is taken.', response.get_data(as_text=True))
        self.assertIn('Register', response.get_data(as_text=True))

        response = self.register(
            'mary@example.com',
            'mary',
            'cat',
            'dog'
        )
        self.assertIn('Error in the Password field - Field must be equal to password2.', response.get_data(as_text=True))
        self.assertIn('Register', response.get_data(as_text=True))

    def test_confirmation_route(self):
        self.register('john@example.com',
                      'john',
                      'cat',
                      'cat')
        u = User.query.filter_by(email='john@example.com').first()
        token = u.generate_confirmation_token()
        response = self.client.get('/auth/confirm/token', follow_redirects=True)
        self.assertIn('Please log in to access this page.', response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)

    def test_logged_in_unconfirmed_route(self):
        # Unconfirmed logged in user
        u = User(email='john@example.com', username='john', password='cat', confirmed=False)
        db.session.add(u)
        response = self.login(u.email, 'cat')
        self.assertIn('You have not confirmed your account yet.', response.get_data(as_text=True))

        # Confirmed logged in user
        u.confirmed = True
        db.session.add(u)
        response = self.client.get('/auth/unconfirmed', follow_redirects=True)
        self.assertIn('You are confirmed!', response.get_data(as_text=True))
        
    def test_logged_out_unconfirmed_route(self):
        response = self.client.get('/auth/unconfirmed', follow_redirects=True)
        self.assertIn('Please log in to access this page.', response.get_data(as_text=True))

    def test_logged_in_resend_confirmation_route(self):
        u = User(email='john@example.com', username='john', password='cat', confirmed=False)
        db.session.add(u)
        self.login(u.email, 'cat')
        response = self.client.get('/auth/confirm', follow_redirects=True)
        self.assertIn('A new confirmation token email has been send to you.', response.get_data(as_text=True))

        u.confirmed=True
        db.session.add(u)
        response = self.client.get('/auth/confirm', follow_redirects=True)
        self.assertIn('You are already confirmed. No need to send new link.', response.get_data(as_text=True))

    def test_logged_out_resend_confirmation_route(self):
        response = self.client.get('/auth/confirm', follow_redirects=True)
        self.assertIn('Please log in to access this page', response.get_data(as_text=True))
