from flask import Flask, render_template, g, request
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_principal import Principal, Permission, RoleNeed

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
db = SQLAlchemy(app)

# Flask-Login initialization
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Flask-Principal initialization
principal = Principal(app)

# Database models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    roles = db.relationship('Role', secondary='user_roles')

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))

# Flask-Principal setup
admin_permission = Permission(RoleNeed('admin'))

# Custom decorator for authorization
def requires_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if permission == 'admin':
                if admin_permission.can():
                    return f(*args, **kwargs)
                else:
                    return "Permission denied (requires admin)", 403
            else:
                return "Invalid permission specified", 400
        return decorated_function
    return decorator

# Sample route requiring admin permission
@app.route('/admin')
@login_required
@requires_permission('admin')
def admin_page():
    return f"Welcome, {current_user.username}! This is the Admin Page."

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return "Login successful"
        else:
            return "Login failed", 401
    return "Please log in"

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return "Logged out successfully"

if __name__ == '__main__':
    app.run()
