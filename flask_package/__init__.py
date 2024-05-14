import os
import requests
import pandas as pd
import fitz as fz
from flask import Flask, render_template,send_from_directory, send_file, request as rq,flash
from googletrans import Translator
from pptx import Presentation
from flask_mail import Mail, Message

#from flask_package.mailing import Gmail

app = Flask(__name__)
#
#gamail = Gmail(app)
#test = gamail.reminder  # test the connection with gmail server
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'mulualem.hailom@gmail.com'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

#pp_parent_folder = r'C:\\Users\\selon\\Documents\\Bete Christian\\Mezmur'
#pp_parent_folder = r'C:/Users/MulleTec001/OneDrive/Documents/flask/teaching-assistance/flask_package/pp'
pp_parent_folder = r'C:/Users/selon/Documents/Bete Christian/Mezmur'
#pp_parent_folder = r'/python-docker/flask_package/pp'

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

#A function to load geez alphabate to latin alphabate transition and put it in Map
def geez_alpha_database():
    #file_loc = r"flask_package\\doc\\GeezEnglishAlphabetSingle.xlsx" # change this to your file location
    file_loc = r"C:\\Users\\selon\\Documents\\Projects\\VSprojects\\python\\flask\teaching-assistance\\flask_package\\doc\\GeezEnglishAlphabetSingle.xlsx"
    df = pd.read_excel(file_loc) # read the excel file into a dataframe
    map = {} # create an empty map: key is Geez, value is English
    for index, row in df.iterrows(): # iterate over the rows
        key = row.iloc[0] # get the first element of the row as the key
        value = row.iloc[1] # get the second element of the row as the value
        map[key] = value # store the key-value pair in the map
        #print(map)
        for i in range(2, len(row), 2): # iterate over the rest of the elements with a step of 2
            key = row.iloc[i] # get the next element of the row as the key
            value = row.iloc[i+1] # get the next element of the row as the value
            map[key] = value # store the key-value pair in the map
    return(map)

#my_map = geez_alpha_database()
my_map = {'ሀ': 'he', 'ለ': 'le', 'ሐ': 'He', 'መ': 'me', 'ሠ': 's2e', 'ረ': 're', 'ሰ': 'se', 'ሸ': 'Se', 'ቀ': 'qe', 'ቈ': 'que', 'ቐ': 'Qe', 'ቘ': 'Que', 'በ': 'be', 'ቨ': 've', 'ተ': 'te', 'ቸ': 'ce', 'ኀ': 'h2e', 'ኈ': 'hue', 'ነ': 'ne', 'ኘ': 'Ne', 'አ': 'e', 'ከ': 'ke', 'ኰ': 'kue', 'ኸ': 'Ke', 'ዀ': 'Kue', 'ወ': 'we', 'ዐ': 'Oe', 'ዘ': 'ze', 'ዠ': 'Ze', 'የ': 'ye', 'ደ': 'de', 'ጀ': 'je', 'ገ': 'ge', 'ጐ': 'gue', 'ጠ': 'Te', 'ጨ': 'Ce', 'ጰ': 'Pe', 'ጸ': 'xe', 'ፀ': 'x2e', 'ፈ': 'fe', 'ፐ': 'pe', '።': '.', '፩': 1, 8.0: 8.0, '፲': 10, '፹': 80, 'ጘ': 'Ge', 'ⶓ': 'Gue', 'ሇ': 'hoa', 'ኯ': 'koa', 'ዸ': 'd2e', 'ሁ': 'hu', 'ሉ': 'lu', 'ሑ': 'Hu', 'ሙ': 'mu', 'ሡ': 's2u', 'ሩ': 'ru', 'ሱ': 'su', 'ሹ': 'Su', 'ቁ': 'qu', 'ቊ': 'qui', 'ቑ': 'Qu', 'ቚ': 'Qui', 'ቡ': 'bu', 'ቩ': 'vu', 'ቱ': 'tu', 'ቹ': 'cu', 'ኁ': 'h2u', 'ኊ': 'hui', 'ኑ': 'nu', 'ኙ': 'Nu', 'ኡ': 'u', 'ኩ': 'ku', 'ኲ': 'kui', 'ኹ': 'Ku', 'ዂ': 'Kui', 'ዉ': 'wu', 'ዑ': 'Ou', 'ዙ': 'zu', 'ዡ': 'Zu', 'ዩ': 'yu', 'ዱ': 'du', 'ጁ': 'ju', 'ጉ': 'gu', 'ጒ': 'gui', 'ጡ': 'Tu', 'ጩ': 'Cu', 'ጱ': 'Pu', 'ጹ': 'xu', 'ፁ': 'x2u', 'ፉ': 'fu', 'ፑ': 'pu', '፡': ';', '፪': 2, 9.0: 9.0, '፳': 20, '፺': 90, 'ጙ': 'Gu', 'ⶔ': 'Gui', 'ሏ': 'lua', 'ዃ': 'Kua', 'ዹ': 'd2u', 'ሂ': 'hi', 'ሊ': 'li', 'ሒ': 'Hi', 'ሚ': 'mi', 'ሢ': 's2i', 'ሪ': 'ri', 'ሲ': 'si', 'ሺ': 'Si', 'ቂ': 'qi', 'ቋ': 'qua', 'ቒ': 'Qi', 'ቛ': 'Qua', 'ቢ': 'bi', 'ቪ': 'vi', 'ቲ': 'ti', 'ቺ': 'ci', 'ኂ': 'h2i', 'ኋ': 'hua', 'ኒ': 'ni', 'ኚ': 'Ni', 'ኢ': 'i', 'ኪ': 'ki', 'ኳ': 'kua', 'ኺ': 'Ki', 'ዊ': 'wi', 'ዒ': 'Oi', 'ዚ': 'zi', 'ዢ': 'Zi', 'ዪ': 'yi', 'ዲ': 'di', 'ጂ': 'ji', 'ጊ': 'gi', 'ጓ': 'gua', 'ጢ': 'Ti', 'ጪ': 'Ci', 'ጲ': 'Pi', 'ጺ': 'xi', 'ፂ': 'x2i', 'ፊ': 'fi', 'ፒ': 'pi', '፣': ',', '፫': 3, '፴': 30, '" "': '" "', 'ጚ': 'Gi', 'ጟ': 'Gua', 'ሗ': 'Hua', 'ዏ': 'woa', 'ዺ': 'd2i', 'ሃ': 'ha', 'ላ': 'la', 'ሓ': 'Ha', 'ማ': 'ma', 'ሣ': 's2a', 'ራ': 'ra', 'ሳ': 'sa', 'ሻ': 'Sa', 'ቃ': 'qa', 'ቌ': 'quie', 'ቓ': 'Qa', 'ቜ': 'Quie', 'ባ': 'ba', 'ቫ': 'va', 'ታ': 'ta', 'ቻ': 'ca', 'ኃ': 'h2a', 'ኌ': 'huie', 'ና': 'na', 'ኛ': 'Na', 'ኣ': 'a', 'ካ': 'ka', 'ኴ': 'kuie', 'ኻ': 'Ka', 'ዄ': 'Kuie', 'ዋ': 'wa', 'ዓ': 'Oa', 'ዛ': 'za', 'ዣ': 'Za', 'ያ': 'ya', 'ዳ': 'da', 'ጃ': 'ja', 'ጋ': 'ga', 'ጔ': 'guie', 'ጣ': 'Ta', 'ጫ': 'Ca', 'ጳ': 'Pa', 'ጻ': 'xa', 'ፃ': 'x2a', 'ፋ': 'fa', 'ፓ': 'pa', '፥': ':', '፬': 4, '፵': 40, " '": " '", 'ጛ': 'Ga', 'ⶕ': 'Guie', 'ሟ': 'mua', 'ዟ': 'zua', 'ዻ': 'd2a', 'ሄ': 'hie', 'ሌ': 'lie', 'ሔ': 'Hie', 'ሜ': 'mie', 'ሤ': 's2ie', 'ሬ': 'rie', 'ሴ': 'sie', 'ሼ': 'Sie', 'ቄ': 'qie', 'ቍ': 'qW', 'ቔ': 'Qie', 'ቝ': 'QW', 'ቤ': 'bie', 'ቬ': 'vie', 'ቴ': 'tie', 'ቼ': 'cie', 'ኄ': 'h2ie', 'ኍ': 'hW', 'ኔ': 'nie', 'ኜ': 'Nie', 'ኤ': 'ie', 'ኬ': 'kie', 'ኵ': 'kW', 'ኼ': 'Kie', 'ዅ': 'KW', 'ዌ': 'wie', 'ዔ': 'Oie', 'ዜ': 'zie', 'ዤ': 'Zie', 'ዬ': 'yie', 'ዴ': 'die', 'ጄ': 'jie', 'ጌ': 'gie', 'ጕ': 'gW', 'ጤ': 'Tie', 'ጬ': 'Cie', 'ጴ': 'Pie', 'ጼ': 'xie', 'ፄ': 'x2ie', 'ፌ': 'fie', 'ፔ': 'pie', '፤': '::', '፭': 5, '፶': 50, '""': '""', 'ጜ': 'Gie', 'ⶖ': 'GW', 'ሧ': 's2ua', 'ዧ': 'Zua', 'ዼ': 'd2ie', 'ህ': 'h', 'ል': 'l', 'ሕ': 'H', 'ም': 'm', 'ሥ': 's2', 'ር': 'r', 'ስ': 's', 'ሽ': 'S', 'ቅ': 'q', 'ቕ': 'Q', 'ብ': 'b', 'ቭ': 'v', 'ት': 't', 'ች': 'c', 'ኅ': 'h2', 'ን': 'n', 'ኝ': 'N', 'እ': 'A', 'ክ': 'k', 'ኽ': 'K', 'ው': 'w', 'ዕ': 'O', 'ዝ': 'z', 'ዥ': 'Z', 'ይ': 'y', 'ድ': 'd', 'ጅ': 'j', 'ግ': 'g', 'ጥ': 'T', 'ጭ': 'C', 'ጵ': 'P', 'ጽ': 'x', 'ፅ': 'x2', 'ፍ': 'f', 'ፕ': 'p', '፦': ';-', '፮': 6, '፷': 60, 'ጝ': 'G', 'ሯ': 'rua', 'ዯ': 'yoa', 'ዽ': 'd2', 'ሆ': 'ho', 'ሎ': 'lo', 'ሖ': 'Ho', 'ሞ': 'mo', 'ሦ': 's2o', 'ሮ': 'ro', 'ሶ': 'so', 'ሾ': 'So', 'ቆ': 'qo', 'ቖ': 'Qo', 'ቦ': 'bo', 'ቮ': 'vo', 'ቶ': 'to', 'ቾ': 'co', 'ኆ': 'h2o', 'ኖ': 'no', 'ኞ': 'No', 'ኦ': 'o', 'ኮ': 'ko', 'ኾ': 'Ko', 'ዎ': 'wo', 'ዖ': 'Oo', 'ዞ': 'zo', 'ዦ': 'Zo', 'ዮ': 'yo', 'ዶ': 'do', 'ጆ': 'jo', 'ጎ': 'go', 'ጦ': 'To', 'ጮ': 'Co', 'ጶ': 'Po', 'ጾ': 'xo', 'ፆ': 'x2o', 'ፎ': 'fo', 'ፖ': 'po', '.': '..', '፯': 7, '፸': 70, 'ጞ': 'Go', 'ሷ': 'sua', 'ዷ': 'dua', 'ዾ': 'd2o'}
print(my_map)
#A function to accept a map and geez text then change it to eglish alphabate. 
def geez_to_latin(map,text):
    my_map = map
    text=text
    eng_txt=""
    for char in text:
        if char in my_map or char == '':
            print (f"The value '{my_map[char]}' is associated with the key '{char}'.")
            #eng_txt = eng_txt + my_map[char]
            eng_txt = "{}{}".format(eng_txt, my_map[char])
        else:
            eng_txt = eng_txt + char
    return eng_txt

#check given text what language it is
def check_language_type(my_text):
    translator = Translator()
    result = translator.detect(my_text)
    print(result.lang)
    return result.lang
    #result = translator.translate('እንዴት ነህ?', dest='en')
    #print(result.text)
 
#Translation from geez/tigrigna to english    
def translate_tig_eng(my_text):
    translator = Translator()
    result = translator.translate(my_text, dest='en')
    return (result.text)
       
# A route to display a form for the user to enter a paragraph in Geez alphabet
@app.route("/")
def index():
    #files = os.listdir(r'flask_package\pp')
    #return render_template("index.html", files=files, events=events)
    #files = os.listdir(r"C:\\Users\\selon\\Documents\\Bete Christian\\Mezmur")
    files = os.listdir(pp_parent_folder)
    return render_template("index.html")

#A function that returns text from given/selected PowerPoint file.
@app.route('/display/<filename>')
def display (filename):
    # Get the uploaded file from the request
    #f = pp_parent_folder + "\\" + filename
    f = pp_parent_folder + "/" + filename
    print ("inpute" + filename)
    print ("represented" + f)
     # Get the uploaded file from the request
    #f = str(r"C:\Users\selon\Documents\Bete Christian\Mezmur\1-29-2023.pptx")
    print ("File name"  + str(f))
    # Get the file extension
    _, file_extension = os.path.splitext(f)
    print ("File extension" + str(file_extension))
    
    # Initialize an empty string to store the extracted text
    text = ""
    # Check the file extension
    if file_extension == '.pptx':
        # Read the PowerPoint file using python-pptx
        prs = Presentation(f)
        print("test1")
        # Loop over the slides and shapes
        for slide in prs.slides:
            print("test2")
            for shape in slide.shapes:
                # Check if the shape has text
                if shape.has_text_frame and shape.text_frame.text:
                    # Append the text to the text string
                    text += shape.text + "\n"
                    print(text)
    elif file_extension == '.pdf':
        # Read the PDF file using pymupdf
       # f = open(f, "w") # create a new file or overwrite an existing file
        doc = fz.open(filename=f, filetype="pdf")
        # Loop over the pages
        for page in doc:
            # Get the text of the page
            text += page.get_text('text') + "\n"
    else:
        # Return an error message if the file extension is not supported
        return "Unsupported file format. Please upload a PowerPoint or PDF file."
    # Return the text as a Flask response
    #return render_template("index.html", text=text, lg_text = check_language_type(text),translated_text = translate_tig_eng(text), latin_text = geez_to_latin(my_map, text),files = os.listdir(r'C:\Users\selon\Documents\Bete Christian\Mezmur'))
    return render_template("index.html", text=text, lg_text = check_language_type(text),translated_text = translate_tig_eng(text), latin_text = geez_to_latin(my_map, text),files = os.listdir(pp_parent_folder))

#This function downloads the files listed on the index page.
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(pp_parent_folder, filename, as_attachment=True)

# A route to process the user's input and display the converted paragraph in Latin alphabet
@app.route("/convert", methods=['GET', 'POST'])
def convert():
    geez_text = rq.form.get("geez_text")
    if rq.method == 'POST' and geez_text != "":
        geez_text = rq.form.get("geez_text")
        translated_text = translate_tig_eng(geez_text)
        lg_text = check_language_type(geez_text)
        if 't_convert' in rq.form:
            latin_text = geez_to_latin(my_map, geez_text)
            print(f"latin_text '{latin_text}'")
            #return render_template("index.html", latin_text=latin_text, lg_text = lg_text, geez_text_t = geez_text, translated_text = translated_text,files = os.listdir(r'/python-docker/flask_package/pp'))
            return render_template("index.html", latin_text=latin_text, lg_text = lg_text, geez_text_t = geez_text, translated_text = translated_text,files = os.listdir(pp_parent_folder))
        elif 'my_button' in rq.form:
            lg_text = translate_tig_eng()
            test = "Button clicked!"
            return render_template('index.html', test_text=test, lg_text = lg_text)
    else:      
        msg = Message('Hello', sender = 'mulualem.hailom@gmail.com', recipients = ['hailomulalem@gmail.com'])
        msg.body = "Hello Flask message sent from Flask-Mail"
        mail.send(msg)
        flash("email have been sent successfuly")
        return render_template('index.html')

#Configuration
app.config['UPLOAD_FOLDER'] = pp_parent_folder
app.config['ALLOWED_EXTENSIONS'] = {'pdf','pptx','ppt'}
#Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#Check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
@app.route("/uplaod", methods=['POST'])
def uplaod_file ():
    #check if the post request has the file part
    if 'file' not in rq.files:
        return render_template('index.html')
    file = rq.files['file']
    #Check if for empty file and has no name
    if file.filename == '':
        return render_template ('index.html')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        return 'File uploaded and processed successfully'
    else:
        return 'File type not allowed'

 
app.config["SECRET_KEY"]= b'\xa4\x99hM\x12s\xc3\x8d'


    