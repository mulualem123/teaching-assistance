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

#gamail = Gmail(app)
#test = gamail.reminder  # test the connection with gmail server
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'mulualem.hailom@gmail.com'
app.config['MAIL_PASSWORD'] = 'mhubxjwvchnsahsn'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)


pp_parent_folder = r'flask_package\pp'



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
    file_loc = r"flask_package\doc\GeezEnglishAlphabetSingle.xlsx" # change this to your file location
    df = pd.read_excel(file_loc) # read the excel file into a dataframe
    map = {} # create an empty map
    for index, row in df.iterrows(): # iterate over the rows
        key = row.iloc[0] # get the first element of the row as the key
        value = row.iloc[1] # get the second element of the row as the value
        map[key] = value # store the key-value pair in the map
        print(map)
        for i in range(2, len(row), 2): # iterate over the rest of the elements with a step of 2
            key = row.iloc[i] # get the next element of the row as the key
            value = row.iloc[i+1] # get the next element of the row as the value
            map[key] = value # store the key-value pair in the map
    return(map)

my_map = geez_alpha_database()

#A function to accept a map and geez text then change it to eglish alphabate. 
def geez_to_latin(map,text):
    my_map = map
    text=text
    eng_txt=""
    for char in text:
        if char in my_map or char == '':
            print (f"The value '{my_map[char]}' is associated with the key '{char}'.")
            eng_txt = eng_txt + my_map[char]
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
    files = os.listdir(r'flask_package\pp')
    return render_template("index.html", files=files, events=events)

#A function that returns text from given/selected PowerPoint file.
@app.route('/display/<filename>')
def display (filename):
    # Get the uploaded file from the request
    f = pp_parent_folder + "\\" + filename
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
    return render_template("index.html", text=text, lg_text = check_language_type(text),translated_text = translate_tig_eng(text), latin_text = geez_to_latin(my_map, text),files = os.listdir(r'C:\Users\selon\Documents\Bete Christian\Mezmur'))

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
            #return render_template("convert.html", latin_text=latin_text)
            return render_template("index.html", latin_text=latin_text, lg_text = lg_text, geez_text_t = geez_text, translated_text = translated_text,files = os.listdir(r'flask_package\pp') )
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
    
@app.route("/try_it")
def try_it():
    
    return render_template("index.html") 

app.config["SECRET_KEY"]= b'\xa4\x99hM\x12s\xc3\x8d'