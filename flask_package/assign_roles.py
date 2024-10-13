# assign_roles.py

from app import app, user_datastore, account_db

with app.app_context():
    # Create an admin user and assign the admin role
    user = user_datastore.create_user(email='admin@example.com', password='password')
    user_datastore.add_role_to_user(user, 'admin')
    db.session.commit()
