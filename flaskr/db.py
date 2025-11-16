import sqlite3
from datetime import datetime

import click
from flask import current_app, g


# Database connection
def get_db(): 
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


# Close database connection
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# Initialize the database
def init_db():
    db = get_db()

    # Read and execute the schema.sql file
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# CLI command to initialize the database
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


# Convert timestamp strings in SQLite to datetime objects in Python
sqlite3.register_converter(
    'timestamp', lambda v: datetime.fromisoformat(v.decode())
)


# Register database functions with the Flask app
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)