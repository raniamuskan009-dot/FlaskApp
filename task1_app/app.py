from flask import Flask, render_template, session
from forms import ContactForm
import html

import os
from flask import request
from werkzeug.utils import secure_filename

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


import os
from dotenv import load_dotenv
load_dotenv()

from flask_talisman import Talisman

from functools import wraps
from flask import abort

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app)

#  SECRET KEY (REQUIRED)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

#  SESSION SECURITY (TASK 3)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

#  CSRF PROTECTION (TASK 3)
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

#  DATABASE (TASK 2 CONTINUED)
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

#  PASSWORD HASHING (TASK 5)
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

# =====================
# MODELS
# =====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))

with app.app_context():
    db.create_all()

# =====================
# TASK 5: REGISTER USER
# =====================
@app.route('/register')
@limiter.limit("5 per minute")  
def register():
    # password = 123456 (example)
    hashed_pw = bcrypt.generate_password_hash("123456").decode('utf-8')

    user = User(email="admin@gmail.com", password=hashed_pw, is_admin=True)
    db.session.add(user)
    db.session.commit()

    return "User created with hashed password"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# =====================
# MAIN FORM (TASK 1+2+3)
# =====================
@app.route('/', methods=['GET', 'POST'])
def form():
    form = ContactForm()

    if form.validate_on_submit():
        # SANITIZATION (TASK 1)
        name = html.escape(form.name.data)
        phone = html.escape(form.phone.data)
        email = html.escape(form.email.data)

        # SAFE DB INSERT (TASK 2)
        contact = Contact(name=name, phone=phone, email=email)
        db.session.add(contact)
        db.session.commit()

        # SESSION (TASK 3)
        session['user'] = name
        session['is_admin'] = True

        return render_template('success.html', name=name)

    return render_template('form.html', form=form)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "File uploaded successfully"

    return "Invalid file"

# =====================
# TASK 4: ERROR HANDLING
# =====================
@app.errorhandler(404)
def error_404(e):
    return render_template('error404.html'), 404

@app.errorhandler(500)
def error_500(e):
    return render_template('error500.html'), 500

# =====================
# RUN
# =====================
if __name__ == '__main__':
    app.run(debug=True)

#SECURITY HEADERS
Talisman(app, content_security_policy=None, force_https=False)

#RATE LIMITING
limiter = Limiter(get_remote_address, app=app,
                  default_limits=["200 per day", "50 per hour"])

#FILE UPLOAD CONFIG
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


#decorater
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # simple check using session (since no flask-login used)
        if not session.get('is_admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
#adminroute
@app.route('/admin')
@admin_required
def admin_panel():
    return "Welcome Admin"
