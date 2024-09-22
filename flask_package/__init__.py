import os
import requests
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
from .forms import RegistrationForm, LoginForm    #Orginal
from .models import db as account_db    #Orginal
from werkzeug.utils import secure_filename
import click

app = Flask(__name__)

#pp_parent_folder = r'C:\\Users\\selon\\Documents\\Bete Christian\\Mezmur'
sundayClassPP = r'C:\\Users\\selon\\Documents\\Bete Christian\\Lecture'
#pp_parent_folder = r'C:/Users/MulleTec001/OneDrive/Documents/flask/teaching-assistance/flask_package/pp'
#pp_parent_folder = r'C:/Users/selon/Documents/Bete Christian/Mezmur'
#pp_parent_folder = r'/python-docker/flask_package/doc/pp'
pp_parent_folder = r'flask_package/doc/pp/'
audio_folder = r'flask_package/static/audio/'

#sqlite3
#app.config['DATABASE'] = r'/python-docker/flask_package/site.db'
app.config['DATABASE'] = r'flask_package/instance/site.db'
#app.config['DATABASE'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' #Account creation
#app.config['SQLALCHEMY_DATABASE_URI'] = r'flask_package/instance/users.db' #Account creation

db.init_app(app) #initiating sqlite3
print ("sql initiated")

account_db.init_app(app)    #Account creation
#login_manager= LoginManager(app)  #Account creation
login_manager= LoginManager()  #Account creation
login_manager.init_app(app)  #Account creation
login_manager.login_view = 'login'  #Account creation

#Telegram
TOKEN = '7611669258:AAEchAugok05KQ_OqFzOc-59bY8FkSZQiwE'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

with app.app_context():
    account_db.create_all()


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
#A dictionery of key = mezmur id and value = audio name
audio_dic = { } #Delete
#my_map = changealphabet.geez_alpha_database()
my_map = {'ሀ': 'he', 'ለ': 'le', 'ሐ': 'He', 'መ': 'me', 'ሠ': 'se', 'ረ': 're', 'ሰ': 'se', 'ሸ': 'Se', 'ቀ': 'qe', 'ቈ': 'que', 'ቐ': 'Qe', 'ቘ': 'Que', 'በ': 'be', 'ቨ': 've', 'ተ': 'te', 'ቸ': 'ce', 'ኀ': 'h2e', 'ኈ': 'hue', 'ነ': 'ne', 'ኘ': 'Ne', 'አ': 'e', 'ከ': 'ke', 'ኰ': 'kue', 'ኸ': 'Ke', 'ዀ': 'Kue', 'ወ': 'we', 'ዐ': 'Oe', 'ዘ': 'ze', 'ዠ': 'Ze', 'የ': 'ye', 'ደ': 'de', 'ጀ': 'je', 'ገ': 'ge', 'ጐ': 'gue', 'ጠ': 'Te', 'ጨ': 'Ce', 'ጰ': 'Pe', 'ጸ': 'xe', 'ፀ': 'xe', 'ፈ': 'fe', 'ፐ': 'pe', '።': '.', '፩': 1, 8.0: 8.0, '፲': 10, '፹': 80, 'ጘ': 'Ge', 'ⶓ': 'Gue', 'ሇ': 'hoa', 'ኯ': 'koa', 'ዸ': 'd2e', 'ሁ': 'hu', 'ሉ': 'lu', 'ሑ': 'Hu', 'ሙ': 'mu', 'ሡ': 's2u', 'ሩ': 'ru', 'ሱ': 'su', 'ሹ': 'Su', 'ቁ': 'qu', 'ቊ': 'qui', 'ቑ': 'Qu', 'ቚ': 'Qui', 'ቡ': 'bu', 'ቩ': 'vu', 'ቱ': 'tu', 'ቹ': 'cu', 'ኁ': 'h2u', 'ኊ': 'hui', 'ኑ': 'nu', 'ኙ': 'Nu', 'ኡ': 'u', 'ኩ': 'ku', 'ኲ': 'kui', 'ኹ': 'Ku', 'ዂ': 'Kui', 'ዉ': 'wu', 'ዑ': 'Ou', 'ዙ': 'zu', 'ዡ': 'Zu', 'ዩ': 'yu', 'ዱ': 'du', 'ጁ': 'ju', 'ጉ': 'gu', 'ጒ': 'gui', 'ጡ': 'Tu', 'ጩ': 'Cu', 'ጱ': 'Pu', 'ጹ': 'xu', 'ፁ': 'x2u', 'ፉ': 'fu', 'ፑ': 'pu', '፡': ';', '፪': 2, 9.0: 9.0, '፳': 20, '፺': 90, 'ጙ': 'Gu', 'ⶔ': 'Gui', 'ሏ': 'lua', 'ዃ': 'Kua', 'ዹ': 'd2u', 'ሂ': 'hi', 'ሊ': 'li', 'ሒ': 'Hi', 'ሚ': 'mi', 'ሢ': 's2i', 'ሪ': 'ri', 'ሲ': 'si', 'ሺ': 'Si', 'ቂ': 'qi', 'ቋ': 'qua', 'ቒ': 'Qi', 'ቛ': 'Qua', 'ቢ': 'bi', 'ቪ': 'vi', 'ቲ': 'ti', 'ቺ': 'ci', 'ኂ': 'h2i', 'ኋ': 'hua', 'ኒ': 'ni', 'ኚ': 'Ni', 'ኢ': 'i', 'ኪ': 'ki', 'ኳ': 'kua', 'ኺ': 'Ki', 'ዊ': 'wi', 'ዒ': 'Oi', 'ዚ': 'zi', 'ዢ': 'Zi', 'ዪ': 'yi', 'ዲ': 'di', 'ጂ': 'ji', 'ጊ': 'gi', 'ጓ': 'gua', 'ጢ': 'Ti', 'ጪ': 'Ci', 'ጲ': 'Pi', 'ጺ': 'xi', 'ፂ': 'x2i', 'ፊ': 'fi', 'ፒ': 'pi', '፣': ',', '፫': 3, '፴': 30, '" "': '" "', 'ጚ': 'Gi', 'ጟ': 'Gua', 'ሗ': 'Hua', 'ዏ': 'woa', 'ዺ': 'd2i', 'ሃ': 'ha', 'ላ': 'la', 'ሓ': 'Ha', 'ማ': 'ma', 'ሣ': 's2a', 'ራ': 'ra', 'ሳ': 'sa', 'ሻ': 'Sa', 'ቃ': 'qa', 'ቌ': 'quie', 'ቓ': 'Qa', 'ቜ': 'Quie', 'ባ': 'ba', 'ቫ': 'va', 'ታ': 'ta', 'ቻ': 'ca', 'ኃ': 'h2a', 'ኌ': 'huie', 'ና': 'na', 'ኛ': 'Na', 'ኣ': 'a', 'ካ': 'ka', 'ኴ': 'kuie', 'ኻ': 'Ka', 'ዄ': 'Kuie', 'ዋ': 'wa', 'ዓ': 'Oa', 'ዛ': 'za', 'ዣ': 'Za', 'ያ': 'ya', 'ዳ': 'da', 'ጃ': 'ja', 'ጋ': 'ga', 'ጔ': 'guie', 'ጣ': 'Ta', 'ጫ': 'Ca', 'ጳ': 'Pa', 'ጻ': 'xa', 'ፃ': 'x2a', 'ፋ': 'fa', 'ፓ': 'pa', '፥': ':', '፬': 4, '፵': 40, " '": " '", 'ጛ': 'Ga', 'ⶕ': 'Guie', 'ሟ': 'mua', 'ዟ': 'zua', 'ዻ': 'd2a', 'ሄ': 'hie', 'ሌ': 'lie', 'ሔ': 'Hie', 'ሜ': 'mie', 'ሤ': 's2ie', 'ሬ': 'rie', 'ሴ': 'sie', 'ሼ': 'Sie', 'ቄ': 'qie', 'ቍ': 'qW', 'ቔ': 'Qie', 'ቝ': 'QW', 'ቤ': 'bie', 'ቬ': 'vie', 'ቴ': 'tie', 'ቼ': 'cie', 'ኄ': 'h2ie', 'ኍ': 'hW', 'ኔ': 'nie', 'ኜ': 'Nie', 'ኤ': 'ie', 'ኬ': 'kie', 'ኵ': 'kW', 'ኼ': 'Kie', 'ዅ': 'KW', 'ዌ': 'wie', 'ዔ': 'Oie', 'ዜ': 'zie', 'ዤ': 'Zie', 'ዬ': 'yie', 'ዴ': 'die', 'ጄ': 'jie', 'ጌ': 'gie', 'ጕ': 'gW', 'ጤ': 'Tie', 'ጬ': 'Cie', 'ጴ': 'Pie', 'ጼ': 'xie', 'ፄ': 'x2ie', 'ፌ': 'fie', 'ፔ': 'pie', '፤': '::', '፭': 5, '፶': 50, '""': '""', 'ጜ': 'Gie', 'ⶖ': 'GW', 'ሧ': 's2ua', 'ዧ': 'Zua', 'ዼ': 'd2ie', 'ህ': 'h', 'ል': 'l', 'ሕ': 'H', 'ም': 'm', 'ሥ': 's2', 'ር': 'r', 'ስ': 's', 'ሽ': 'S', 'ቅ': 'q', 'ቕ': 'Q', 'ብ': 'b', 'ቭ': 'v', 'ት': 't', 'ች': 'c', 'ኅ': 'h2', 'ን': 'n', 'ኝ': 'N', 'እ': 'A', 'ክ': 'k', 'ኽ': 'K', 'ው': 'w', 'ዕ': 'O', 'ዝ': 'z', 'ዥ': 'Z', 'ይ': 'y', 'ድ': 'd', 'ጅ': 'j', 'ግ': 'g', 'ጥ': 'T', 'ጭ': 'C', 'ጵ': 'P', 'ጽ': 'x', 'ፅ': 'x2', 'ፍ': 'f', 'ፕ': 'p', '፦': ';-', '፮': 6, '፷': 60, 'ጝ': 'G', 'ሯ': 'rua', 'ዯ': 'yoa', 'ዽ': 'd2', 'ሆ': 'ho', 'ሎ': 'lo', 'ሖ': 'Ho', 'ሞ': 'mo', 'ሦ': 's2o', 'ሮ': 'ro', 'ሶ': 'so', 'ሾ': 'So', 'ቆ': 'qo', 'ቖ': 'Qo', 'ቦ': 'bo', 'ቮ': 'vo', 'ቶ': 'to', 'ቾ': 'co', 'ኆ': 'h2o', 'ኖ': 'no', 'ኞ': 'No', 'ኦ': 'o', 'ኮ': 'ko', 'ኾ': 'Ko', 'ዎ': 'wo', 'ዖ': 'Oo', 'ዞ': 'zo', 'ዦ': 'Zo', 'ዮ': 'yo', 'ዶ': 'do', 'ጆ': 'jo', 'ጎ': 'go', 'ጦ': 'To', 'ጮ': 'Co', 'ጶ': 'Po', 'ጾ': 'xo', 'ፆ': 'x2o', 'ፎ': 'fo', 'ፖ': 'po', '.': '..', '፯': 7, '፸': 70, 'ጞ': 'Go', 'ሷ': 'sua', 'ዷ': 'dua', 'ዾ': 'd2o'}
#print(my_map)

    
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        
        account_db.create_all()
        # check if email exitsts
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))
        
        # check if username exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        # create new user
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        account_db.session.add(user)
        account_db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in', 'successful')
            return redirect(url_for('index'))
        flash('Invalid email or password', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return f'hello,{current_user.username}! welcome to your dashboard'

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out', 'warnning')
    return redirect(url_for('login'))

# A route to display a form for the user to enter a paragraph in Geez alphabet
@app.route("/")
def index():
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
                            tags=db.get_taglist()
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
        return render_template("translate.html", latin_text=changealphabet.geez_to_latin(geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
    else:
        return render_template("translate.html",files = os.listdir(pp_parent_folder), rows= db.get_data())
    
#Return Audio
@app.route("/audio/<id>")
def audio(id):
    #files = os.listdir(r'flask_package\pp')
    #return render_template("index.html", files=files, events=events)
    #files = os.listdir(r"C:\\Users\\selon\\Documents\\Bete Christian\\Mezmur")
    #get the audio file from database from passed id
    print("This is passed id from mezmur page " + str(id))
    #First print list of audios 
    audio_list = db.get_audio(id)
    if audio_list:
        selected_audio = audio_list[0]
        print("001 audio/Selected_audio_exist " + str(selected_audio))
    else:
    # Handle the case where the list is empty
        selected_audio = "NA"
        print("002 Selected_audio " + str(selected_audio))
    
    #return send_from_directory('static/audio', "audio_2023-07-05_21-32-44.ogg")
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
            db.mv_database(title,geez_text,latin_text,"NA","NA","NA","NA","NA")
            #mv_database(title,geez_text,latin_text,filename,audio,cat1,cat2,cat3):
            #rows = db.get_data()
            #print(f"latin_text '{latin_text}'")
            #return render_template("index.html", latin_text=latin_text, lg_text = lg_text, geez_text_t = geez_text, translated_text = translated_text,files = os.listdir(r'/python-docker/flask_package/pp'))
            #return render_template("index.html", latin_text=changealphabet.geez_to_latin(my_map, geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
            return render_template("index.html", latin_text=changealphabet.geez_to_latin(geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
            #if geez_text != "": 
            #    return render_template("index.html", latin_text=changealphabet.geez_to_latin(my_map, geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
            #else:
            #    return render_template("index.html",files = os.listdir(pp_parent_folder), rows= db.get_data())            
        elif 'my_button' in rq.form:
            lg_text = googletransfun.translate_tig_eng()
            test = "Button clicked!"
            return render_template('index.html', test_text=test, lg_text = lg_text)
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
    if rq.method == 'POST':
        # check if the post request has the file part
        if 'file' not in files:
            flash('No file part')
            return "No File exist"
    upload(rq.files)
    return render_template("index.html",files = os.listdir(pp_parent_folder), rows= db.get_data())

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
    if geez_text != "": 
        #return render_template("index.html", latin_text=changealphabet.geez_to_latin(my_map, geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
        return render_template("mezmur.html", latin_text=changealphabet.geez_to_latin(geez_text), lg_text = googletransfun.check_language_type(geez_text), geez_text_t = geez_text, translated_text = googletransfun.translate_tig_eng(geez_text),files = os.listdir(pp_parent_folder), rows= db.get_data())
    else:
        return render_template("mezmur.html",files = os.listdir(pp_parent_folder), rows= db.get_data())

@app.route('/update/<id>',  methods=['GET', 'POST'])
@login_required
def update (id):
    #print(id)
    mezdata = db.get_selected_data(id) #Getting the selected row from db database
    #print("id " + str(mezdata[0]))
    #print("Title " + str(mezdata[1]))
    #print("Titleen " + str(mezdata[2]))
    #print("Azmach " + str(mezdata[3]))
    #print("Azmachen" + str(mezdata[4]))
    
    latin_text = mezdata[4] 
    
        
    if (mezdata[2]==None or mezdata[2]==" "):
        #db.set_titleen(changealphabet.geez_to_latin(my_map, mezdata[1]), id)
        db.set_titleen(changealphabet.geez_to_latin(mezdata[1]), id)
        #print ("Titleen ")
        #print (mezdata[2])
        
    if (mezdata[4]==None or mezdata[4]==" "):
        #db.set_azmachen(changealphabet.geez_to_latin(my_map, mezdata[3]), id)
        db.set_azmachen(changealphabet.geez_to_latin(mezdata[3]), id)
        #print ("Azmachen") 
        #print (mezdata[4])
        #latin_text = changealphabet.geez_to_latin(my_map, mezdata[3])
        latin_text = changealphabet.geez_to_latin(mezdata[3])

    return render_template("update.html", 
                           mezdata=mezdata, 
                           lg_text = googletransfun.check_language_type(mezdata[2]),
                           translated_text = googletransfun.translate_tig_eng(mezdata[2]),
                           latin_text = latin_text,
                           tags=db.get_taglist())

@app.route('/pushupdate', methods=['POST'])    
def pushupdate():
    app.config['UPLOAD_FOLDER'] = audio_folder
    app.config['ALLOWED_EXTENSIONS'] = {'mp3','mpeg','ogg','mp4','m4a'}
    if rq.method == 'POST':

        #upload(rq.files)
        id = rq.form.get("id")
        print("Id from form ")
        print(id)
        title = rq.form.get("title")
        #print(title)
        titleen = rq.form.get("titleen")
        #print(titleen)
        geez_text = rq.form.get("geez_text")
        #print(geez_text)
        alpha_text = rq.form.get("alpha_text")
        #print(alpha_text)
        
        db.set_title(title,id)
        db.set_titleen(titleen,id)
        db.set_azmach(geez_text,id)
        db.set_azmachen(alpha_text,id)
        
        #Getting the file name form upload. upload function upload file and return the file's name
        mez_audio_filename = upload(rq.files)
        print ("mez_audio_filename " + str(mez_audio_filename))
        if "File has no name" not in mez_audio_filename :
            db.set_audio_file(mez_audio_filename,id)   
         
        audio_dic[id]=mez_audio_filename
        #print(audio_dic[id])
        rows= db.get_data()  
        
        
        selected_tags = rq.form.getlist('selected_tags')  # get the selected tags from the form
        if selected_tags:
            num = 1
            print ("This is going to print tags")
            for  tag in selected_tags:
                print ("Tag " + str(num) + str(tag))
                num = num + 1
            
            db.update_mez_tags(selected_tags, id)

        #for row in rows:
        #    for i in range(11):
        #        print (row[i]) 
        #audio_files={row[0]:audio_dic.get(row[0], None) for row in rows}
  
    return render_template("mezmur.html", 
                        latin_text=changealphabet.geez_to_latin(geez_text), 
                        lg_text = googletransfun.check_language_type(geez_text), 
                        geez_text_t = geez_text, 
                        translated_text = googletransfun.translate_tig_eng(geez_text),
                        files = os.listdir(pp_parent_folder), 
                        rows= db.get_data(),
                        mez_tags = db.get_allMezTags(),
                        tags=db.get_taglist()
                       )
    
                
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
  
#Add Tag to the list 
@app.route('/add_tag', methods=['GET', 'POST'])
def add_tag():
    if rq.method == 'POST':
        tag_name = rq.form.get('name')
        db.add_tags(tag_name)
        return redirect(url_for('add_tag'))
    return render_template("tags.html", tags=db.get_taglist())
    
#Attach a Tag to a Mezmur
@app.route('/add_tag_to_mezmur/<int:mez_id>', methods=['GET', 'POST'])
def add_tag_to_mez(mez_id):
    tag_name = request.form.get('name')
    db.add_tags_to_mez(mez_id,tag_name)
    return redirect(url_for('mezmur'))

#getting built #Telegram
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    chat_id = data.get('chat_id')
    message = data.get('message')
    
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    
    response = requests.post(TELEGRAM_API_URL, json=payload)
    return response.json()

    
app.config["SECRET_KEY"]= b'\xa4\x99hM\x12s\xc3\x8d'


    