import sqlite3
import click
from flask import current_app, g

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

#Add mezmur in geez in database.
def mv_database(title,geez_text,latin_text,filename,audio,cat1,cat2,cat3):
    db_ob = get_db()
    sql = 'Insert INTO mezmur (title, azmach,azmachen,dir,audio_file,cat1,cat2,cat3) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
    values = (title,geez_text, latin_text, filename, audio, cat1, cat2, cat3)
    db_ob.execute(sql, values)
    db_ob.commit()
    #db_ob.close()
    return 'Mezmur added successfuly'

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
    db_ob = get_db()
    sql = 'UPDATE mezmur SET azmachen = ? where m_id = ?'
    values = (azmachen, id)
    db_ob.execute(sql,values)
    db_ob.commit()
    return "updated!"

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
    sql = 'SELECT * FROM mezmur where m_id = ?'
    cursor.execute(sql,(id,))
    data = cursor.fetchall()[0]
    cursor.close()
    return data

@click.command('init-db')
def init_db_command():
    """Clear the exitsting data and create new tables"""
    init_db()
    click.echo('Initialized the database.')
    
def init_app(app):
    app.teardown_appcontext(close_db) 
    app.cli.add_command(init_db_command)