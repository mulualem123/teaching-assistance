import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext 

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        
    return g.db

def close_db(e=None):
    db = g.pop ('db', None)
    
    if db is not None:
        db.close()
        
def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f: db.executescript(f.read().decode('utf8'))

#Adds data to the database
def add_data(data):
    db = get_db()
    db.execute('INSERT INTO data (data) VALUES (?)', (data,)) #data is the data that is being added
    db.commit()

#Add mezmur into database from files (PP). 
def mv_database(title, geez_text, latin_text, engTrans, filename, audio, cat1, cat2, cat3,
               timed_geez=None, timed_latin=None, timed_english=None):
    db_ob = get_db()
    sql = '''INSERT INTO mezmur 
            (title, azmach, azmachen, engTrans, dir, audio_file, cat1, cat2, cat3,
             timed_geez, timed_latin, timed_english) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    values = (title, geez_text, latin_text, engTrans, filename, audio, cat1, cat2, cat3,
              timed_geez, timed_latin, timed_english)
    db_ob.execute(sql, values)
    db_ob.commit()
    return 'Mezmur added successfully with timed lyrics support'

#Add a new Mezmur to database. 
def add_mezmur(title, titleen, geez_text, alpha_text, engTrans, timed_geez, timed_latin, timed_english, audioFilepath, tags):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO mezmur (title, titleen, azmach, azmachen, engTrans, timed_geez, timed_latin, timed_english, audio_file, dir, cat1, cat2, cat3)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, titleen, geez_text, alpha_text, engTrans, timed_geez, timed_latin, timed_english, audioFilepath, "NA", "NA", "NA", "NA"))

    mezmur_id = cursor.lastrowid

    # Add tags (assuming you have a mezmur_tags table)
    update_mez_tags(tags, mezmur_id)
    
    conn.commit()
    conn.close()

# Add timed lyrics
def set_timed_lyrics(m_id, geez=None, latin=None, english=None):
    db_ob = get_db()
    if geez:
        db_ob.execute('UPDATE mezmur SET timed_geez = ? WHERE m_id = ?', (geez, m_id))
    if latin:
        db_ob.execute('UPDATE mezmur SET timed_latin = ? WHERE m_id = ?', (latin, m_id))
    if english:
        db_ob.execute('UPDATE mezmur SET timed_english = ? WHERE m_id = ?', (english, m_id))
    db_ob.commit()
    return "Timed lyrics updated"

# Get timed lyrics
def get_timed_lyrics(m_id, language):
    db_ob = get_db()
    column = {
        'geez': 'timed_geez',
        'latin': 'timed_latin',
        'english': 'timed_english'
    }.get(language, 'timed_geez')
    
    result = db_ob.execute(
        f'SELECT {column} FROM mezmur WHERE m_id = ?',
        (m_id,)
    ).fetchone()
    
    return result[0] if result else None
#Delete entry from the database
def delete_data(id):
    db_ob = get_db()
    #curtsor = db_ob.cursor()
    sql = 'delete from mezmur where m_id = ?'
    db_ob.execute(sql,(id,))
    db_ob.commit()
    return "Deleted!"  

#Update entry from the database
def update_data(id):
    db_ob = get_db()
    #curtsor = db_ob.cursor()
    sql = 'UPDATE mezmur SET title = ?, azmach = ? where m_id = ?'
    values = (title,azmach, id)
    db_ob.execute(sql,values)
    db_ob.commit()
    return "updated!"

#Sets the title in english alphabet to the value titleen. 
def set_title(title, id):
    db_ob = get_db()
    sql = 'UPDATE mezmur SET title = ? where m_id = ?'
    values = (title, id)
    db_ob.execute(sql,values)
    db_ob.commit()
    return "updated!"

#Sets the title in english alphabet to the value titleen. 
def set_titleen(titlen, id):
    db_ob = get_db()
    sql = 'UPDATE mezmur SET titleen = ? where m_id = ?'
    values = (titlen, id)
    db_ob.execute(sql,values)
    db_ob.commit()
    return "updated!"

#Sets the azmach to given value parameter.
def set_azmach(azmach, id):
    db_ob = get_db()
    sql = 'UPDATE mezmur SET azmach = ? where m_id = ?'
    values = (azmach, id)
    db_ob.execute(sql,values)
    db_ob.commit()
    return "updated!"

#Sets the azmach in english alphabet to the summited value azmachen.
def set_azmachen(azmachen, id):
    print("set_azmachen method from db.py module has been called with inpute: " + str(id) + " and " + str(azmachen))
    db_ob = get_db()
    sql = 'UPDATE mezmur SET azmachen = ? where m_id = ?'
    values = (azmachen, id)
    db_ob.execute(sql,values)
    db_ob.commit()
    return "updated!"

# Sets the hyme (English meaning)
def set_engTrans(engTrans, id):
    print("db-set_engTrans: method from db.py module has been called with inpute: " + str(id) + " and " + str(engTrans))
    db_ob = get_db()
    sql = 'UPDATE mezmur SET engTrans = ? where m_id = ?'
    values = (engTrans, id)
    db_ob.execute(sql,values)
    db_ob.commit()
    return "updated!"

def set_timed_geez(timed_geez, id):
    db_ob = get_db()
    sql = 'UPDATE mezmur SET timed_geez = ? where m_id = ?'
    values = (timed_geez, id)
    db_ob.execute(sql,values)
    db_ob.commit()
    return "timed_geez updated!"

def set_timed_latin(timed_latin, id):
    db_ob = get_db()
    sql = 'UPDATE mezmur SET timed_latin = ? where m_id = ?'
    values = (timed_latin, id)
    db_ob.execute(sql,values)
    db_ob.commit()
    return "timed_latin updated!"

def set_timed_english(timed_english, id):
    db_ob = get_db()
    sql = 'UPDATE mezmur SET timed_english = ? where m_id = ?'
    values = (timed_english, id)
    db_ob.execute(sql,values)
    db_ob.commit()
    return "timed_english updated!"

def set_audio_file(audio_file, id):
    print("set_audio_file function called")
    print(audio_file)
    print("This is ID " + str(id))
    
    db_ob = get_db()
    sql = 'UPDATE mezmur SET audio_file = ? where m_id = ?'
    values = (audio_file, id)
    db_ob.execute(sql,values)
    db_ob.commit()
    return "updated!"
def get_audio(id):
    db_ob = get_db()
    cursor = db_ob.cursor()
    sql = 'SELECT audio_file FROM mezmur WHERE m_id = ?'
    cursor.execute(sql,(id,))
    data = cursor.fetchone()
    return data
def get_data():
    db_ob = get_db()
    cursor = db_ob.cursor()
    sql = 'SELECT * FROM mezmur'
    cursor.execute(sql)
    data = cursor.fetchall()
    #for word in data:
    #    print(word)
    #print(data)
    #cursor.close()
    return data

#def search (search_term):
##    #Split the search term into individual words
#    db = get_db()
#    words = search_term.split()
#    print (words)    
##    #create a subquery to search for rows where any of the words appear in the title or text colum
##    #subquery = db.session.query(func.count(func.match(mezmur.title,'|'.join(word))+func.match(mezmur.text,'|'.join(words))))
#    subquery = db.session.query(func.count(func.match(mezmur.title, '|'.join(words)) + func.match(mezmur.text, '|'.join(words)))[0] > 0)
#    results = db.session.query(mezmur).filter(subquery).all()   
#    return results 

#Not being used
def search(search_term):
    db = get_db()
    words = search_term.split()
    print(words)
    
    # Create the SQL query
    query = "SELECT * FROM mezmur WHERE "
    query += " OR ".join([f"title LIKE '%{word}%' OR azmach LIKE '%{word}%'" for word in words])
    
    # Execute the query
    cursor = db.execute(query)
    results = cursor.fetchall()
    
    return results

#####################################################################################################

def update_meztags(tag, id):
    db_ob = get_db()
    sql = 'UPDATE mezTags SET tag = ? where m_id = ?'
    values = (tag, id)
    db_ob.execute(sql,values)
    db_ob.commit()
    return "updated!"

def update_taglist(tag):
    db_ob = get_db()
    sql = 'UPDATE tagList SET tag = ?'
    values = (tag)
    db_ob.execute(sql,values)
    db_ob.commit()
    return "updated!"

####################################################################################################
def add_tags(name):
    db_ob = get_db()
    sql = 'INSERT or IGNORE INTO tagList (tag) VALUES(?)'
    values = (name,)
    print(f"SQL: {sql}")
    print(f"Values: {values} ")
    db_ob.execute(sql,values)
    db_ob.commit()
    return "added!"
# ... other functions ...

def add_tag(tag_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tagList (tag) VALUES (?)", (tag_name,))
    conn.commit()

def tag_exists(tag_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM tagList WHERE tag = ?", (tag_name,))
    result = cursor.fetchone()
    return result is not None

# Delete tag
def delete_tag(tag_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tagList WHERE t_id = ?", (tag_id,))
    conn.commit()


def add_tags_to_mez(m_id, tag_name):
    db_ob = get_db()
    cursor = db_ob.cursor()
    sql = 'SELECT id FROM tagList where tag = ?'
    cursor.execute(sql,(tag_name,))
    tag_id = cursor.fetchall()[0]
    
    if tag_id:
        sql = 'INSERT INTO mezTags (tag_id, m_id) VALUES(?, ?)'
        values = (tag_id[1], m_id)
        db_ob.execute(sql,values)
        db_ob.commit()
        return "added!"
    
def get_selectedMezTags(id):
    db_ob = get_db()
    cursor = db_ob.cursor()
    sql = 'SELECT tag FROM mezTags where m_id = ?'
    cursor.execute(sql,(id,))
    data = cursor.fetchall()
    return data

def get_allMezTags():
    db_ob = get_db()
    cursor = db_ob.cursor()
    sql = 'SELECT * FROM mezTags'
    cursor.execute(sql)
    data = cursor.fetchall()
    return data

def get_taglist():
    db_ob = get_db()
    cursor = db_ob.cursor()
    sql = 'SELECT * FROM tagList'
    cursor.execute(sql)
    data = cursor.fetchall()
    return data

def update_mez_tags(selected_tags, m_id):
    db_ob = get_db()
    cursor = db_ob.cursor()
    # delete any existing tags for this mezmur
    db_ob.execute("DELETE FROM mezTags WHERE m_id = ?", (m_id,))
    
    # add the selected tags to the mezTags table
    for tag_id in selected_tags:
        sql = 'SELECT tag FROM tagList where t_id = ?'
        cursor.execute(sql,(tag_id,))
        selected_tag = cursor.fetchone()[0]
        db_ob.execute("INSERT INTO mezTags (m_id, tag_id, tag) VALUES (?, ?, ?)", (m_id, tag_id, selected_tag))
    db_ob.commit()
    return "updated"

####################################################################################################
#Not being used
def get_script(command):
    db_ob = get_db()
    cursor = db_ob.cursor()
    sql = command
    cursor.execute(sql)
    data = cursor.fetchall()[0]
    return data


def get_selected_data(id):
    db_ob = get_db()
    cursor = db_ob.cursor()
    sql = '''SELECT 
        m_id, title, titleen, azmach, azmachen, engTrans,
        timed_geez, timed_latin, timed_english, 
        dir, audio_file, created, cat1, cat2, cat3 
        FROM mezmur WHERE m_id = ?'''
    cursor.execute(sql, (id,))
    print("get_selected_data has been called")
    return cursor.fetchone()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the exitsting data and create new tables"""
    init_db()
    click.echo('Initialized the database.')
    
def init_app(app):
    app.teardown_appcontext(close_db) 
    app.cli.add_command(init_db_command)
    
