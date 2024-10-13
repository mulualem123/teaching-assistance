from . import app, account_db

with app.app_context():
    tables = account_db.engine.table_names()
    print("Tables in the database:", tables)