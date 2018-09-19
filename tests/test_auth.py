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
