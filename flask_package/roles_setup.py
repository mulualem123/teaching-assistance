# roles_setup.py

from . import app, user_datastore, db
from .models import db as account_db, User, Role, roles_users 

with app.app_context():
    # Create roles
    user_datastore.create_role(name='admin', description='Admin role')
    user_datastore.create_role(name='editor', description='Editor role')
    user_datastore.create_role(name='database_manager', description='Database Manager role')
    user_datastore.create_role(name='normal_user', description='Normal User role')
    user_datastore.create_role(name='student', description='Student role')
    #account_db.session.commit()
    db.session.commit()
