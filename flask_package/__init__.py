import os
import base64
from datetime import datetime
#import requests
import pandas as pd
import fitz as fz
import sqlite3
from flask import Flask, render_template,send_from_directory, send_file, request as rq, flash, redirect, url_for
from pptx import Presentation
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy #Account creation
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user #Account creation
#from flask_package.mailing import Gmail
from . import db                #Orginal
from .extractpp import extract  #Orginal
from . import googletransfun    #Orginal
from . import changealphabet    #Orginal
from .forms import RegistrationForm, LoginForm, PlaylistForm    #Orginal
from .models import db as account_db, User, Role, roles_users, Playlist, PlaylistSong    #Orginal
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, roles_required
from flask_migrate import Migrate  # Import Migrate here
from werkzeug.utils import secure_filename
import click
from flask import jsonify

app = Flask(__name__)

pp_parent_folder = r'C:\\Users\\selon\\Documents\\Bete Christian\\Mezmur'
sundayClassPP = r'C:\\Users\\selon\\Documents\\Bete Christian\\Lecture'
#pp_parent_folder = r'C:/Users/MulleTec001/OneDrive/Documents/flask/teaching-assistance/flask_package/pp'
#pp_parent_folder = r'C:/Users/selon/Documents/Bete Christian/Mezmur'
#pp_parent_folder = r'/python-docker/flask_package/doc/pp'
#pp_parent_folder = r'flask_package/doc/pp/'
audio_folder = r'flask_package/static/audio/'

#sqlite3
#app.config['DATABASE'] = r'/python-docker/flask_package/site.db'
app.config['DATABASE'] = r'flask_package/instance/site.db'
#app.config['DATABASE'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' #Account creation
#app.config['SQLALCHEMY_DATABASE_URI'] = r'flask_package/instance/users.db' #Account creation

app.config['SECRET_KEY'] = 'super-secret-key'
app.config['SECURITY_PASSWORD_SALT'] = 'super-secret-salt'
db.init_app(app) #initiating sqlite3
print ("sql initiated")

account_db.init_app(app)    #Account creation
migrate = Migrate(app, account_db)
#login_manager= LoginManager(app)  #Account creation
login_manager= LoginManager()  #Account creation
login_manager.init_app(app)  #Account creation
login_manager.login_view = 'login'  #Account creation

#Telegram
TOKEN = '7611669258:AAEchAugok05KQ_OqFzOc-59bY8FkSZQiwE'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(account_db, User, Role)
security = Security(app, user_datastore)
        
with app.app_context():
    account_db.create_all()
    print("Tables created successfully!")

# Import models after initializing account_db to avoid circular imports
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from .models import User    #Orginal
#gamail = Gmail(app)
#test = gamail.reminder  # test the connection with gmail server
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'mulualem.hailom@gmail.com'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# Uppload file Configuration
app.config['UPLOAD_FOLDER'] = pp_parent_folder
app.config['ALLOWED_EXTENSIONS'] = {'pdf','pptx','ppt'}
#Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
#Initialization 
geez_text = ""
#events to display on calendar card. Go to index page and call this array once you pass through home function
events = [
    {
        'title': 'event1',
        'date': '2024-10-15'
    },
    {
        'title': 'event2',
        'date': '2024-10-20'
    }
]

def create_default_admin():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email=os.getenv('ADMIN_EMAIL')).first():
            admin_role = user_datastore.find_or_create_role(name='admin', description='Administrator')
            user_datastore.create_user(
                email=os.getenv('ADMIN_EMAIL'),
                password=generate_password_hash(os.getenv('ADMIN_PASSWORD')),
                roles=[admin_role]
            )
            db.session.commit()
            #use the following export variables to set up Admin Email and Admin Password
                #export ADMIN_EMAIL='admin@example.com'
                #export ADMIN_PASSWORD='your_secure_password'
                            
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        with app.app_context():
            account_db.create_all()
        
        # Check if email exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))
        
        # Check if username exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        with app.app_context():
            new_user = user_datastore.create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data  # Ensuring we hash passwords properly
            )
            account_db.session.commit()
            
            user_datastore.add_role_to_user(new_user, 'normal_user')
            account_db.session.commit()
        
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

        #user = User(username=form.username.data, email=form.email.data)
        #user.set_password(form.password.data)
        #account_db.session.add(user)
        
#Edit users
@app.route('/edit_user', methods=['GET', 'POST'])
@roles_required('admin')
def edit_user():
    if rq.method == 'POST':
        user_id = rq.form.get('user_id')
        
        user = User.query.get(user_id)
        if not user:
            return "User not found", 404
        
        #update user attribues
        new_username = rq.form.get('username')
        new_email = rq.form.get('email')
        new_active_status = rq.form.get('active')
        
        if new_username:    
            user.username = new_username
        else:
            return "User name can't be None", 400
        
        if new_email:
            user.email = new_email
        else:
            return "Email can't be None", 400
        
        if new_active_status:
            user.active = new_active_status.lower() == 'true'
        else:
            return "Active status can't be None", 400

        selected_roles = rq.form.getlist('roles[]')  # get the selected roles from the form
        user.roles = [] #Clear existing roles
        
        #Assign selected roles to the user
        if selected_roles:
            num = 1
            print ("This is going to print tags")
            for  role_name in selected_roles:
                user_datastore.add_role_to_user(user, role_name)
                print ("role " + str(num) + str(role_name))
                num = num + 1
        else:
            return "No roles selected", 400
        
        #Get selected action from the form
        selected_action = rq.form.get('user_action')
        
        print ("The selected action is " + str(selected_action))
        
        if selected_action.lower() == "activate":
            user.active = True
        elif selected_action.lower() == "deactivate":
            user.active = False
        elif selected_action.lower() == "delete":
            account_db.session.delete(user)
            
        #Add or remove roles
        #user_datastore.add_role_to_user(user, 'new_role')
        #user_datastore.remove_role_from_user(user, 'old_role')
        
        #Commit changes to the database
        account_db.session.commit()
        
        flash(str(user.username)+'\'s' + ' account has successfuly Edited!', 'success')
        return redirect(url_for('edit_user'))

    return render_template("user_manager.html",
        users= User.query.all(),
        roles= Role.query.all())
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    return security.login_form()
    #    form = LoginForm()
    #    if form.validate_on_submit():
    #        user = User.query.filter_by(email=form.email.data).first()
    #        if user and user.check_password(form.password.data):
    #            login_user(user)
    #            flash('Logged in successfully', 'success')
    #            return redirect(url_for('index'))
    #        else:
    #            flash('Invalid email or password', 'danger')
    #            return redirect(url_for('login'))
    #    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out', 'warnning')
    return redirect(url_for('login'))

@app.route('/admin')
@roles_required('admin')
def admin():
    return render_template("user_manager.html",
            users= User.query.all(),
            roles= Role.query.all())

#Add role to the list 
@app.route('/add_role', methods=['GET', 'POST'])
def add_role():
    print ("add_role called in init.py")
    if rq.method == 'POST':
        role_name = rq.form.get('name')
        role_description = rq.form.get('description')
        user_datastore.create_role(name=str(role_name), description=str(role_name))
        account_db.session.commit()
        print (str(role_name) + str(role_description))
        for role in Role.query.all():
            print ("role: " + str(role) )
        return redirect(url_for('admin'))
    return render_template("user_manager.html",
        users= User.query.all(),
        roles= Role.query.all())
        
# A route to display a form for the user to enter a paragraph in Geez alphabet
@app.route("/")
def index():
    #account_db.create_all()
    #files = os.listdir(r'flask_package\pp')
    #return render_template("index.html", files=files, events=events)
    #files = os.listdir(r"C:\\Users\\selon\\Documents\\Bete Christian\\Mezmur")
    files = os.listdir(pp_parent_folder)
    imageslide1 = 'images/Emebatachn_Dingle_Mariam01.jpeg'
    imageslide2 = 'images/Pawlos01.jpeg'
    imageslide3 = 'images/images.jpeg'
    if geez_text != "": 
    #    return render_template("index.html", latin_text=changealphabet.geez_to_latin(my_map, geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
        return render_template("index.html", latin_text=changealphabet.geez_to_latin(geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data(),imageslide1=imageslide1, imageslide2=imageslide2,imageslide3=imageslide3)
    else:
        return render_template("index.html",files = os.listdir(pp_parent_folder), rows= db.get_data(),imageslide1=imageslide1, imageslide2=imageslide2,imageslide3=imageslide3)
    
# A route to display a form for the user to enter a paragraph in Geez alphabet
@app.route("/mezmur")
def mezmur():
    files = os.listdir(pp_parent_folder)
    form = PlaylistForm()
    mez_tags = db.get_allMezTags()
    #print("The following will print all the mezmur tags")
    #for m_tags in mez_tags:
    #    print("m_tags " + str(m_tags))
    #    print("m_tags[0] " + str(m_tags[0]))
    #    print("m_tags[1] " + str(m_tags[1]))
    #    print("m_tags[2] " + str(m_tags[2]))
        
    #rows= db.get_data()  
    #audio_files={row[0]:audio_dic.get(row[0], None) for row in rows}
    
    return render_template("mezmur.html", 
                            latin_text=changealphabet.geez_to_latin(geez_text), 
                            lg_text = googletransfun.check_language_type(geez_text), 
                            geez_text_t = geez_text, 
                            translated_text = googletransfun.translate_tig_eng(geez_text),
                            files = os.listdir(pp_parent_folder), 
                            rows= db.get_data(),
                            mez_tags = mez_tags,
                            tags=db.get_taglist(),
                            form=form
                           )

@app.route("/sundayclass")
def sundayclass():
    files = os.listdir(sundayClassPP)
    
    #rows= db.get_data()  
    #audio_files={row[0]:audio_dic.get(row[0], None) for row in rows}
    
    if geez_text != "": 
        #return render_template("mezmur.html", latin_text=changealphabet.geez_to_latin(my_map, geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
        return render_template("sundayClass.html", latin_text=changealphabet.geez_to_latin(geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(sundayClassPP), rows= db.get_data())
    else:
        return render_template("sundayClass.html",files = os.listdir(sundayClassPP), rows= db.get_data())

# A route to display a form for the user to enter a paragraph in Geez alphabet
@app.route("/calendar")
def calendar():
    #files = os.listdir(r'flask_package\pp')
    #return render_template("index.html", files=files, events=events)
    #files = os.listdir(r"C:\\Users\\selon\\Documents\\Bete Christian\\Mezmur")
    files = os.listdir(pp_parent_folder)
    if geez_text != "": 
    #    return render_template("index.html", latin_text=changealphabet.geez_to_latin(my_map, geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
        return render_template("calendar.html", latin_text=changealphabet.geez_to_latin(geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
    else:
        return render_template("calendar.html",files = os.listdir(pp_parent_folder), rows= db.get_data())
    
@app.route("/files")
def files():
    #files = os.listdir(r'flask_package\pp')
    #return render_template("index.html", files=files, events=events)
    #files = os.listdir(r"C:\\Users\\selon\\Documents\\Bete Christian\\Mezmur")
    files = os.listdir(pp_parent_folder)
    if geez_text != "": 
    #    return render_template("index.html", latin_text=changealphabet.geez_to_latin(my_map, geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
        return render_template("files.html", latin_text=changealphabet.geez_to_latin(geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
    else:
        return render_template("files.html",files = os.listdir(pp_parent_folder), rows= db.get_data())
    
@app.route("/translate")
def translate():
    #files = os.listdir(r'flask_package\pp')
    #return render_template("index.html", files=files, events=events)
    #files = os.listdir(r"C:\\Users\\selon\\Documents\\Bete Christian\\Mezmur")
    files = os.listdir(pp_parent_folder)
    if geez_text != "": 
    #    return render_template("index.html", latin_text=changealphabet.geez_to_latin(my_map, geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
        return render_template("translate.html", 
                               latin_text=changealphabet.geez_to_latin(geez_text), 
                               lg_text = googletransfun.check_language_type(geez_text), 
                               geez_text_t = geez_text, 
                               translated_text = googletransfun.translate_tig_eng(geez_text),
                               files = os.listdir(pp_parent_folder), 
                               rows= db.get_data())
    else:
        return render_template("translate.html",files = os.listdir(pp_parent_folder), rows= db.get_data())
    
#Return Audio
@app.route("/audio/<id>")
def audio(id):
    # Get the audio file from the database using the passed id
    print("This is passed id from mezmur page: " + str(id))
    audio_list = db.get_audio(id)
    
    if audio_list:
        selected_audio = audio_list[0]
        print("001 audio/Selected_audio_exist " + str(selected_audio))
    else:
        selected_audio = "NA"
        print("002 Selected_audio " + str(selected_audio))
    
    return send_from_directory('static/audio', str(selected_audio))

#A function that returns text from given/selected PowerPoint file.
@app.route('/display/<filename>')
def display (filename):
    # Get the uploaded file from the request
    #f = pp_parent_folder + "\\" + filename
    f = pp_parent_folder + "/" + filename
    # Get the uploaded file from the request
    #f = str(r"C:\Users\selon\Documents\Bete Christian\Mezmur\1-29-2023.pptx")
    #print ("File name"  + str(f))
    # Get the file extension
    _, file_extension = os.path.splitext(f)
    #print ("File extension" + str(file_extension))
    
    # Initialize an empty string to store the extracted text
    text = ""
    # Check the file extension
    if file_extension == '.pptx':
        # Read the PowerPoint file using python-pptx
        prs = Presentation(f)
        ex = extract(f, db, filename)
        if ex.checkfile() != True:
            ex.read()
        else:
            print(str(filename) + " file exist!")
            
        # Loop over the slides and shapes
        for slide in prs.slides:
            #print("test2")
            for shape in slide.shapes:
                # Check if the shape has text
                if shape.has_text_frame and shape.text_frame.text:
                    # Append the text to the text string
                    text += shape.text + "\n"
                    #print(text)
    elif file_extension == '.pdf':
        # Read the PDF file using pymupdf
       # f = open(f, "w") # create a new file or overwrite an existing file
        doc = fz.open(filename=f, filetype="pdf")
        ex = extract(doc, db, filename)
        ex.read()
        # Loop over the pages
        for page in doc:
            # Get the text of the page
            text += page.get_text('text') + "\n"
    else:
        # Return an error message if the file extension is not supported
        return "Unsupported file format. Please upload a PowerPoint or PDF file."
    # Return the text as a Flask response
    #return render_template("index.html", text=text, lg_text = googletransfun.check_language_type(text),translated_text = googletransfun.translate_tig_eng(text), latin_text = changealphabet.geez_to_latin(my_map, text),files = os.listdir(r'C:\Users\selon\Documents\Bete Christian\Mezmur'))
    #return render_template("index.html", text=text, lg_text = googletransfun.check_language_type(text),translated_text = googletransfun.translate_tig_eng(text), latin_text = changealphabet.geez_to_latin(my_map, text),files = os.listdir(pp_parent_folder), rows= db.get_data())
    return render_template("index.html", text=text, lg_text = googletransfun.check_language_type(text),translated_text = googletransfun.translate_tig_eng(text), latin_text = changealphabet.geez_to_latin(text),files = os.listdir(pp_parent_folder), rows= db.get_data())

#This function downloads the files listed on the index page.
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(pp_parent_folder, filename, as_attachment=True)

# A route to process the user's input and display the converted paragraph in Latin alphabet
@app.route("/convert", methods=['GET', 'POST'])
def convert():
    geez_text = rq.form.get("geez_text")
    if rq.method == 'POST' and geez_text != "":
        title = "Mezmur"
        geez_text = rq.form.get("geez_text")
        #translated_text = googletransfun.translate_tig_eng(geez_text)
        #lg_text = googletransfun.check_language_type(geez_text)
        if 't_convert' in rq.form:
            #latin_text = changealphabet.geez_to_latin(my_map, geez_text)
            latin_text = changealphabet.geez_to_latin(geez_text)
            #db.mv_database(title,geez_text,latin_text,"NA","NA","NA","NA","NA")
            #mv_database(title,geez_text,latin_text,filename,audio,cat1,cat2,cat3):
            #rows = db.get_data()
            #print(f"latin_text '{latin_text}'")
            #return render_template("index.html", latin_text=latin_text, lg_text = lg_text, geez_text_t = geez_text, translated_text = translated_text,files = os.listdir(r'/python-docker/flask_package/pp'))
            #return render_template("index.html", latin_text=changealphabet.geez_to_latin(my_map, geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
            return render_template("translate.html", latin_text=changealphabet.geez_to_latin(geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
            #if geez_text != "": 
            #    return render_template("index.html", latin_text=changealphabet.geez_to_latin(my_map, geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
            #else:
            #    return render_template("index.html",files = os.listdir(pp_parent_folder), rows= db.get_data())            
        elif 'my_button' in rq.form:
            lg_text = googletransfun.translate_tig_eng()
            test = "Button clicked!"
            return render_template('translate.html', test_text=test, lg_text = lg_text)
    else:      
        msg = Message('Hello', sender = 'mulualem.hailom@gmail.com', recipients = ['hailomulalem@gmail.com'])
        msg.body = "Hello Flask message sent from Flask-Mail"
        mail.send(msg)
        flash("email have been sent successfuly")
        return render_template('index.html')
#Uppload File
#Check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
        
@app.route("/uplaod", methods=['GET', 'POST'])
def uplaod_file ():
    files = rq.files
    print ("selected files: " + str(files))
    if rq.method == 'POST':
        # check if the post request has the file part
        if 'file' not in rq.files:
            flash('No file part')
            return "No File part"
        file = rq.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return "No file selected for uploading"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #return filename 
            return render_template("translate.html",
                                   files = os.listdir(pp_parent_folder), 
                                   rows= db.get_data())

def upload (files):
    #check if the post request has the file part
    #if 'file' not in files:
    #    print(str(files))
    #    print("file is not in rq.files")
    #    return "No File exist"
    file = files['file']
    print(file)
    #Check if for empty file and has no name
    if file.filename == '':
        print(str(file.filename) + "the file has no name")
        return "File has no name"
    if file and allowed_file(file.filename):
        print("File does exit and is not null")
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        return filename
    else:
        return render_template("index.html",files = os.listdir(pp_parent_folder), rows= db.get_data())
  
@app.route('/delete/<id>')
@login_required
def delete (id):
    db.delete_data(id)
    #return render_template("index.html",files = os.listdir(pp_parent_folder), rows=db.get_data())
    form = PlaylistForm()

    return render_template("mezmur.html", 
                            latin_text=changealphabet.geez_to_latin(geez_text), 
                            lg_text = googletransfun.check_language_type(geez_text), 
                            geez_text_t = geez_text, 
                            translated_text = googletransfun.translate_tig_eng(geez_text),
                            files = os.listdir(pp_parent_folder), 
                            rows= db.get_data(),
                            mez_tags = db.get_allMezTags(),
                            tags=db.get_taglist(),
                            form = form
                           )
    
@app.route('/update/<id>',  methods=['GET', 'POST'])
@login_required
def update (id):
    #print(id)
    mezdata = db.get_selected_data(id) #Getting the selected row from db database
    print("id " + str(mezdata[0]))
    print("Title " + str(mezdata[1]))
    print("Titleen " + str(mezdata[2]))
    print("Azmach " + str(mezdata[3]))
    print("Azmachen" + str(mezdata[4]))
    print("number5 " + str(mezdata[5]))
    print("number6 " + str(mezdata[6]))
    print("number7 " + str(mezdata[7]))
    print("number8 " + str(mezdata[8]))
    print("number9 " + str(mezdata[9]))
    print("number10 " + str(mezdata[10]))
    print("number11 " + str(mezdata[11]))
    print("number12 " + str(mezdata[12]))
    print("number13 " + str(mezdata[13]))
    print("number14 " + str(mezdata[14]))
    
    #variable to be only passed or (updated and passed)
    latin_text = mezdata[4] 
    engTrans = mezdata[5]
    selected_mez_tags = db.get_selectedMezTags(id)
    
    for tag in selected_mez_tags:
        print ("This is selected mezmur's Tag " + str(tag))
       
    if (mezdata[2]==None or mezdata[2]==" "):
        #db.set_titleen(changealphabet.geez_to_latin(my_map, mezdata[1]), id)
        db.set_titleen(changealphabet.geez_to_latin(mezdata[1]), id)
        #print ("Titleen ")
        #print (mezdata[2])
        
    if (mezdata[4]==None or mezdata[4]==""):
        print ("Azmach is empty or null")
        print ("The ID of the Mezmur is " + str(id))
        #db.set_azmachen(changealphabet.geez_to_latin(my_map, mezdata[3]), id)
        latin_text = changealphabet.geez_to_latin(mezdata[3])
        db.set_azmachen(latin_text, id)
        print("latin_text to be passed to update page is " + str(latin_text))

    if (mezdata[5]==None or mezdata[5]=="" or mezdata[5]=="NA"):
        print ("English translate is empty or null")
        engTrans = googletransfun.translate_tig_eng(mezdata[3])
        db.set_engTrans(engTrans,id)
        print ("English translate to be passed to update page is " + str(engTrans))
        
    return render_template("update.html", 
                           mezdata=mezdata,
                           engTrans=engTrans, 
                           lg_text = googletransfun.check_language_type(mezdata[3]),
                           translated_text = googletransfun.translate_tig_eng(mezdata[3]),
                           latin_text = latin_text,
                           tags=db.get_taglist(),
                           selected_mez_tags=selected_mez_tags)

@app.route('/pushupdate', methods=['POST'])
def pushupdate():
    # Configure allowed extensions and upload folder. Note that we've added 'webm' since recorded audio might be in this format.
    app.config['UPLOAD_FOLDER'] = audio_folder
    app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'mpeg', 'ogg', 'mp4', 'm4a', 'webm'}

    form = PlaylistForm()

    if rq.method == 'POST':
        mezmur_id = rq.form.get("id")
        title = rq.form.get("title")
        titleen = rq.form.get("titleen")
        geez_text = rq.form.get("geez_text")
        alpha_text = rq.form.get("alpha_text")
        engTrans = rq.form.get("engTrans")
        timed_geez = rq.form.get("timed-geez")
        timed_latin = rq.form.get("timed-latin")
        timed_english = rq.form.get("timed-english")

        # Update the mezmur details in the database.
        db.set_title(title, mezmur_id)
        db.set_titleen(titleen, mezmur_id)
        db.set_azmach(geez_text, mezmur_id)
        db.set_azmachen(alpha_text, mezmur_id)
        db.set_engTrans(engTrans, mezmur_id)

        # First, attempt to get an uploaded audio file.
        uploaded_filename = upload(rq.files)
        if "File has no name" not in uploaded_filename:
            db.set_audio_file(uploaded_filename, mezmur_id)
        else:
            # No file was uploaded. Check for recorded audio data.
            recorded_audio_data = rq.form.get("recorded_audio", "")
            if recorded_audio_data and recorded_audio_data.startswith("data:"):
                try:
                    # Split the data URL: e.g. "data:audio/webm; codecs=opus;base64,BASE64..."
                    header, encoded = recorded_audio_data.split(',', 1)
                    # Determine the file extension based on the header
                    if "audio/webm" in header:
                        extension = "webm"
                    elif "audio/ogg" in header:
                        extension = "ogg"
                    else:
                        extension = "mp3"  # Default to mp3 if type is unrecognized

                    filename = f"recorded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                    # Write the decoded audio data to file.
                    with open(file_path, "wb") as f:
                        f.write(base64.b64decode(encoded))

                    db.set_audio_file(filename, mezmur_id)
                    print(f"Recorded audio saved as {filename}")
                except Exception as e:
                    print("Error saving recorded audio:", e)

        # Update selected tags (if any)
        selected_tags = rq.form.getlist('selected_tags')
        if selected_tags:
            print("Updating tags:")
            for num, tag in enumerate(selected_tags, start=1):
                print(f"Tag {num}: {tag}")
            db.update_mez_tags(selected_tags, mezmur_id)

    # Render the updated mezmur display page.
    return render_template("mezmur.html", 
                           latin_text=changealphabet.geez_to_latin(geez_text), 
                           lg_text=googletransfun.check_language_type(geez_text), 
                           geez_text_t=geez_text, 
                           translated_text=googletransfun.translate_tig_eng(geez_text),
                           files=os.listdir(pp_parent_folder), 
                           rows=db.get_data(),
                           mez_tags=db.get_allMezTags(),
                           tags=db.get_taglist(),
                           form=form)
    
@app.route('/add_mezmur', methods=['POST'])
def add_mezmur():
    if rq.method == 'POST':
        try:
            # ... your existing code to get form data ...
            title = rq.form.get("title")
            titleen = rq.form.get("titleen") # Added titleen
            geez_text = rq.form.get("geez_text")
            alpha_text = rq.form.get("alpha_text")
            engTrans = rq.form.get("engTrans")
            timed_geez = rq.form.get("timed-geez")
            timed_latin = rq.form.get("timed-latin")
            timed_english = rq.form.get("timed-english")
            selected_tags = rq.form.getlist('selected_tags') # Get selected tags
            
            # Handle file upload (as before)
            audioFile = rq.files.get("file")
            if audioFile and allowed_file(audioFile.filename):
                filename = secure_filename(audioFile.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                audioFile.save(filepath)
                audio_filepath = filepath
            else:
                audio_filepath = None

            # Call your database function
            result = db.add_mezmur(title, titleen, geez_text, alpha_text, engTrans, timed_geez, timed_latin, timed_english, audio_filepath, selected_tags)

            if isinstance(result, str) and result.startswith("Database error:"):
                return jsonify({'error': result}), 500
            else:
                return jsonify({'message': 'Mezmur added successfully'}), 201  # JSON success response

        except Exception as e:
            app.logger.exception(f"Error in add_mezmur: {e}")
            return jsonify({'error': 'An unexpected error occurred'}), 500

    return jsonify({'error': 'Invalid request method'}), 405  # Handle non-POST requests
        
@app.route('/selectedmez/<id>')
def selected(id):
    #print(id)
    text = db.get_selected_data(id)[3]
    #print (text)
    #return render_template("index.html", text=text, lg_text = googletransfun.check_language_type(text),translated_text = googletransfun.translate_tig_eng(text), latin_text = changealphabet.geez_to_latin(my_map, text),files = os.listdir(pp_parent_folder))  
    if geez_text != "": 
        #return render_template("index.html", latin_text=changealphabet.geez_to_latin(my_map, geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
        return render_template("index.html", latin_text=changealphabet.geez_to_latin(geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
    else:
        #return render_template("index.html", text=text, lg_text = googletransfun.check_language_type(text),translated_text = googletransfun.translate_tig_eng(text), latin_text = changealphabet.geez_to_latin(my_map, text),files = os.listdir(pp_parent_folder), rows= db.get_data())
        return render_template("index.html", text=text, lg_text = googletransfun.check_language_type(text),translated_text = googletransfun.translate_tig_eng(text), latin_text = changealphabet.geez_to_latin(text),files = os.listdir(pp_parent_folder), rows= db.get_data())
    
#Search function, takes any a word or a phrase and search in the data base
@app.route('/search', methods=['GET'])
def search():
    search_term = rq.args.get("search_term")
    if not search_term:
        #return "No search term provided", 400
        return  redirect(url_for('mezmur'))
    
    #Search the database for the rows where the title or the ext column contains the term
    results = db.search(search_term)
    
    #Render the sarch results template, passing in the search term and results
    return render_template("mezmur.html",files = os.listdir(pp_parent_folder), search_term=search_term, rows= results)


@app.route('/add_tag', methods=['POST'])
def add_tag():
    if rq.method == 'POST':
        tag_name = rq.form.get('tag_name').strip().lower()
        if not tag_name:
            return jsonify({'error': 'Tag name cannot be empty'}), 400

        if db.tag_exists(tag_name):
            return jsonify({'error': 'Tag already exists'}), 409

        db.add_tag(tag_name)
        return jsonify({'message': 'Tag added successfully', 'tag': tag_name}), 201

    return jsonify({'error': 'Invalid request method'}), 405

#Add tag to list through form
@app.route('/add_tag_form', methods=['GET', 'POST'])
def add_tag_form():
    if rq.method == 'POST':
        tag_name = rq.form.get('name')
        db.add_tags(tag_name)
        return redirect(url_for('add_tag_form'))
    return render_template("tags.html", tags=db.get_taglist()) 
 
#Delete_tag  
@app.route('/delete_tag/<int:tag_id>', methods=['POST'])
def delete_tag(tag_id):
    try:
        db.delete_tag(tag_id)  # Call your database function to delete the tag
        flash('Tag deleted successfully!', 'success')
        return redirect(url_for('add_tag_form'))  # Redirect to the tag management page
    except Exception as e:
        flash(f'Error deleting tag: {e}', 'error')
        return redirect(url_for('add_tag_form'))

#Attach a Tag to a Mezmur
@app.route('/add_tag_to_mezmur/<int:mez_id>', methods=['GET', 'POST'])
def add_tag_to_mez(mez_id):
    tag_name = rq.form.get('name')
    db.add_tags_to_mez(mez_id,tag_name)
    return redirect(url_for('mezmur'))

#getting built #Telegram
@app.route('/send_message', methods=['POST'])
def send_message():
    data = rq.json
    chat_id = data.get('chat_id')
    message = data.get('message')
    
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    
    response = rq.post(TELEGRAM_API_URL, json=payload)
    return response.json()
################################PlayList###################
# Create a playlist
@app.route('/playlist/create', methods=['GET', 'POST'])
@login_required
def create_playlist():
    form = PlaylistForm()
    if form.validate_on_submit():
        new_playlist = Playlist(user_id=current_user.id, name=form.name.data, description=form.description.data)
        account_db.session.add(new_playlist)
        account_db.session.commit()
        flash('playlist created!', 'success')
        return redirect(url_for('mezmur'))
    return render_template('create_playlist.html', form=form)

# View all playlists
@app.route('/playlists')
@login_required
def view_playlists():
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    return render_template('playlists.html', playlists=playlists)

#Gets list of playlists
@app.route('/api/playlists')
@login_required
def get_playlists():
    try:
        playlists = Playlist.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'song_count': p.songs.count()
        } for p in playlists])
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
        
#Load songs from selected playlist.
@app.route('/api/playlists/<int:playlist_id>')
@login_required
def get_playlist(playlist_id):
    try:
        # Get playlist from database
        playlist = Playlist.query.filter_by(
            id=playlist_id,
            user_id=current_user.id
        ).first_or_404()

        # Get songs from SQLite database               
        songs = []
        for song_rel in playlist.songs.all():
            song_data = db.get_selected_data(song_rel.song_id)
            if song_data:
                songs.append({
                    'id': song_data[0],
                    'title': song_data[1],
                    'timed_geez': song_data[6],
                    'timed_latin': song_data[7],
                    'timed_english': song_data[8],
                    'azmach': song_data[3],
                    'azmachen': song_data[4],
                    'engTrans': song_data[5],
                    'audio_url': url_for('audio', id=song_data[0], _external=True)
                })

        return jsonify({
            'id': playlist.id,
            'name': playlist.name,
            'description': playlist.description,
            'created_at': playlist.created_at.isoformat(),
            'song_count': len(songs),
            'songs': songs
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
        
# View a single playlist and its songs
@app.route('/playlist/<int:playlist_id>')
@login_required
def view_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != current_user.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('mezmur'))
    
    # Fetch song details from SQLite (`db`)
    songs = []
    for song_rel in playlist.songs.all():
        song_data = db.get_selected_data(song_rel.song_id)  # Use your SQLite helper
        if song_data:
            songs.append(song_data)
    
    return render_template('playlist.html', playlist=playlist, songs=songs)

@app.route('/playlist/<int:playlist_id>/delete', methods=['POST'])
@login_required
def delete_playlist_old(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != current_user.id:
        abort(403)
    # Delete associated songs
    PlaylistSong.query.filter_by(playlist_id=playlist_id).delete()
    account_db.session.delete(playlist)
    account_db.session.commit()
    flash('Playlist deleted successfully!', 'success')
    return redirect(url_for('view_playlists'))

@app.route('/api/playlists/<int:playlist_id>', methods=['DELETE'])
@login_required
def delete_playlist(playlist_id):
    try:
        # Get playlist and verify ownership
        playlist = Playlist.query.filter_by(
            id=playlist_id,
            user_id=current_user.id
        ).first_or_404()

        # Delete all associated songs first
        PlaylistSong.query.filter_by(playlist_id=playlist_id).delete()
        
        # Delete the playlist
        account_db.session.delete(playlist)
        account_db.session.commit()

        # Get updated list of playlists
        updated_playlists = Playlist.query.filter_by(
            user_id=current_user.id
        ).all()

        return jsonify({
            'status': 'success',
            'message': 'Playlist deleted successfully',
            'playlists': [{
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'song_count': p.songs.count()
            } for p in updated_playlists]
        })

    except Exception as e:
        account_db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 
           
# Add a song to a playlist
@app.route('/add_to_playlist', methods=['POST'])
@login_required
def add_to_playlist_form():
    song_id = rq.form.get('song_id')
    playlist_id = rq.form.get('playlist_id')
    
    # Validate song exists in SQLite (`db`)
    if not db.get_selected_data(song_id):  # Use your SQLite helper
        flash('Song not found!', 'danger')
        return redirect(url_for('mezmur'))
    
    # Validate playlist belongs to user
    playlist = Playlist.query.get(playlist_id)
    if not playlist or playlist.user_id != current_user.id:
        flash('Invalid playlist!', 'danger')
        return redirect(url_for('mezmur'))
    
    # Check if song is already in the playlist
    existing = PlaylistSong.query.filter_by(
        playlist_id=playlist_id, 
        song_id=song_id
    ).first()
    if existing:
        flash('Song already in playlist!', 'warning')
        return redirect(url_for('mezmur'))
    
    # Add to playlist
    new_entry = PlaylistSong(playlist_id=playlist_id, song_id=song_id)
    account_db.session.add(new_entry)
    account_db.session.commit()
    flash('Song added to playlist!', 'success')
    return redirect(url_for('view_playlist', playlist_id=playlist_id))

@app.route('/playlist/<int:playlist_id>/add/<int:song_id>', methods=['POST'])
@login_required
def add_to_playlist(playlist_id, song_id):
    try:
        print(f"Attempting to add song {song_id} to playlist {playlist_id}")
        
        # Retrieve song data (once)
        song_data = db.get_selected_data(song_id)
        if not song_data:
            return jsonify({
                'status': 'error',
                'message': 'Song not found'
            }), 404
        print("Song Data:", song_data)
        
        # Retrieve and validate playlist using get_or_404
        playlist = Playlist.query.get_or_404(playlist_id)
        print("Playlist:", playlist)
        
        # Ensure the playlist belongs to the current user
        if playlist.user_id != current_user.id:
            return jsonify({
                'status': 'error',
                'message': 'Invalid playlist'
            }), 403
        
        # Check if the song is already in the playlist
        if PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first():
            return jsonify({
                'status': 'warning',
                'message': 'Song already in playlist'
            }), 409

        # Add the song to the playlist
        new_entry = PlaylistSong(playlist_id=playlist_id, song_id=song_id)
        account_db.session.add(new_entry)
        account_db.session.commit()
        
        # Create a single consolidated JSON response
        response_data = {
            'status': 'success',
            'message': 'Song added successfully',
            'playlist': {
                'id': playlist.id,
                'name': playlist.name,
                'song_count': playlist.songs.count()
            },
            'song': {
                'id': song_id,
                'title': song_data[1]  # assuming the title is in the second position
            }
        }
        
        print("Returning JSON:", response_data)
        return jsonify(response_data), 201

    except Exception as e:
        account_db.session.rollback()
        print("Error occurred:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

    
# Remove a song from a playlist
@app.route('/remove_from_playlist/<int:playlist_id>/<int:song_id>', methods=['GET','POST'])
@login_required
def remove_from_playlist_form(playlist_id, song_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != current_user.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('view_playlists'))
    
    entry = PlaylistSong.query.filter_by(
        playlist_id=playlist_id, 
        song_id=song_id
    ).first()
    
    if entry:
        account_db.session.delete(entry)
        account_db.session.commit()
        flash('Song removed from playlist!', 'success')
    
    return redirect(url_for('view_playlist', playlist_id=playlist_id))

@app.route('/api/playlists/<int:playlist_id>/songs/<int:song_id>', methods=['DELETE'])
@login_required
def remove_from_playlist(playlist_id, song_id):
    try:
        # Verify playlist ownership
        playlist = Playlist.query.filter_by(
            id=playlist_id,
            user_id=current_user.id
        ).first_or_404()

        # Find and delete the song relationship
        song_rel = PlaylistSong.query.filter_by(
            playlist_id=playlist_id,
            song_id=song_id
        ).first()

        if not song_rel:
            return jsonify({'status': 'error', 'message': 'Song not in playlist'}), 404

        account_db.session.delete(song_rel)
        account_db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Song removed from playlist'
        })

    except Exception as e:
        account_db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
################################PlayList end################
@app.route('/test',  methods=['GET'])
def test():
    users = [
        {
            'username':'john_doe',
            'email':'john@example.com',
            'roles':[{'name':'admin'},{'name':'editor'}]        
        },
        {
            'username':'alex_amor',
            'email':'alex@example.com',
            'roles':[{'name':'user'}]        
        }
    ]
    return render_template("user_manager.html", users=users)

@app.route('/dashboard')
@login_required
def dashboard():
    return f'hello,{current_user.username}! welcome to your dashboard' 
  


###########################Share Playlist #########################
@app.route('/playlist/shared/<int:playlist_id>')
def view_shared_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    return render_template('shared_playlist.html', playlist=playlist)
    
    
app.config["SECRET_KEY"]= b'\xa4\x99hM\x12s\xc3\x8d'