"""
Database initialization module.
Creates the shared SQLAlchemy instance used across all models.
"""

from flask_sqlalchemy import SQLAlchemy

# Shared SQLAlchemy instance - imported by all model modules
db = SQLAlchemy()


def init_db(app):
    """
    Initialize the database with the Flask application context.
    Creates all tables if they do not already exist.

    Args:
        app: Flask application instance with database configuration.
    """
    db.init_app(app)
    with app.app_context():
        db.create_all()
