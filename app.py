from flask_package import app, db

##Checks the Flask app's configuration to make sure it is listening on the correct port. This will print the port the Flask app is listening on when it is started
if __name__ == "__main__":
    with app.app_context():
        # This ensures the tables for the custom mezmur DB are created if they don't exist.
        db.init_db()
        # The user database (users.db) is already handled by `create_all()` in __init__.py

    # The logic to create an admin user has been moved to a Flask CLI command.
    # Run `flask create-admin` in your terminal to create the admin user.
    
    # Enable debug mode for troubleshooting
    app.run(host='0.0.0.0', port=5000, debug=True)