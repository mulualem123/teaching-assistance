from werkzeug.security import generate_password_hash, check_password_hash

class User (UserMaxin, db.Model):
    id =db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password():
        return check_password_hash(self.password, password)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))