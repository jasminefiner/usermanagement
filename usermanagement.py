from app import create_app, db
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

from app.models import User


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User)


@app.cli.command()
def test():
    """Run the unit tests"""

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
