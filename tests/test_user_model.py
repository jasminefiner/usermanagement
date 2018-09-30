import unittest
from flask import current_app
from app import create_app, db
from app.models import User


class UserModelTestCase(unittest.TestCase):
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

    def test_password_setter(self):
        u = User(password='password')
        db.session.add(u)
        self.assertTrue(u.password_hash is not None)

    def test_password_salts_are_random(self):
        u1 = User(password='cat')
        u2 = User(password='cat')
        self.assertNotEqual(u1.password_hash, u2.password_hash)

    def test_no_password_getter(self):
        u = User(password='password')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_valid_confirmation_token(self):
        u = User(password='cat')
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(email='john@example.com', username='john', password='cat')
        u2 = User(email='mary@example.com', username='mary', password='cat')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_change_password(self):
        u = User(email='john@example.com', username='john', password='cat')
        db.session.add(u)
        hash = u.password_hash
        u.change_password('dog')
        self.assertNotEqual(hash, u.password_hash)
        self.assertFalse(u.verify_password('cat'))
        self.assertTrue(u.verify_password('dog'))

    def test_generate_password_reset_token(self):
        u = User(email='john@example.com', username='john', password='cat')
        db.session.add(u)
        token = u.generate_password_reset_token()
        self.assertTrue(token is not None)

    def test_password_reset(self):
        u = User(email='john@example.com', username='john', password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_password_reset_token()
        self.assertTrue(User.password_reset(token, 'dog'))
        self.assertFalse(u.verify_password('cat'))

    def test_generate_email_change_token(self):
        u = User(email='john@example.com', username='john', password='cat')
        db.session.add(u)
        token = u.generate_email_change_token('mary@example.com')
        self.assertTrue(token is not None)

    def test_email_change(self):
        u = User(email='john@example.com', username='john', password='cat')
        db.session.add(u)
        db.session.commit()

        token = u.generate_email_change_token('john@example.com')
        self.assertFalse(u.email_change(token))

        token = u.generate_email_change_token('mary@example.com')
        self.assertTrue(u.email_change(token))
        self.assertEqual(u.email, 'mary@example.com')
        self.assertNotEqual(u.email, 'john@example.com')

        token = u.generate_email_change_token(None)
        self.assertFalse(u.email_change(token))

        token = u.generate_email_change_token('john@example.com')
        db.session.delete(u)
        db.session.commit()
        self.assertFalse(u.email_change(token))

    def test_user_profile_attributes(self):
        u = User(email='john@example.com', username='john', password='cat')
        db.session.add(u)
        self.assertEqual(u.name, None)
        self.assertEqual(u.age, None)
        self.assertEqual(u.location, None)
        self.assertEqual(u.bio, None)
        u.name = 'John Smith'
        u.age = 36
        u.location = 'London, UK'
        u.bio = 'This is a short bio'
        self.assertNotEqual(u.name, None)
        self.assertNotEqual(u.age, None)
        self.assertNotEqual(u.location, None)
        self.assertNotEqual(u.bio, None)

    def test_avatar(self):
        u = User(email='john@example.com', username='john', password='cat')
        avatar = u.avatar()
        avatar_256 = u.avatar(256)
        avatar_pg = u.avatar(rating='pg')
        avatar_retro = u.avatar(default='retro')
        self.assertNotEqual(avatar, None)
        self.assertIn('s=256', avatar_256)
        self.assertIn('r=pg', avatar_pg)
        self.assertIn('d=retro', avatar_retro)


if __name__ == '__main__':
    unittest.main()
