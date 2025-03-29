import os
import librosa
import sqlite3  # Import sqlite3 for error handling
from flask import Flask
from db import get_db, init_app

import os
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Absolute path to the database
    base_dir = os.path.abspath(os.path.dirname(__file__))  # Path to `flask_package`
    instance_dir = os.path.join(base_dir, 'instance')
    db_path = os.path.join(instance_dir, 'site.db')
    
    # Create the "instance" folder if it doesn't exist
    os.makedirs(instance_dir, exist_ok=True)
    
    # Configure the database
    app.config['DATABASE'] = db_path
    app.config['SECRET_KEY'] = 'dev'
    
    # Debugging: Print the database path
    print(f"Database path: {app.config['DATABASE']}")  # Should match your expectations
    
    # Initialize database
    init_app(app)  # From db.py
    return app
    
def migrate_existing_lyrics():
    app = create_app()
    with app.app_context():
        db = get_db()
        
        # Add new columns if they don't exist
        try:
            db.execute('ALTER TABLE mezmur ADD COLUMN timed_geez TEXT')
            db.execute('ALTER TABLE mezmur ADD COLUMN timed_latin TEXT')
            db.execute('ALTER TABLE mezmur ADD COLUMN timed_english TEXT')
            db.commit()
        except sqlite3.OperationalError as e:
            print(f"Columns may already exist: {e}")
            
        # Get all mezmurs with their audio files
        # In migrate_existing_lyrics(), add a WHERE clause to skip populated entries
        mezmurs = db.execute('''
            SELECT m_id, azmach, azmachen, engTrans, audio_file 
            FROM mezmur
            WHERE timed_geez IS NULL  -- Only process entries without timed lyrics
        ''').fetchall()

        for mez in mezmurs:
            m_id = mez['m_id']
            audio_file = mez['audio_file']

            # Get audio duration if exists
            audio_duration = None
            if audio_file:
                try:
                    audio_path = os.path.join('static', 'audio', audio_file)
                    if os.path.exists(audio_path):
                        audio_duration = librosa.get_duration(filename=audio_path)
                except Exception as e:
                    print(f"Error processing audio for mezmur {m_id}: {str(e)}")
                    audio_duration = None

            # Convert all lyric versions
            timed_geez = convert_to_timed_format(mez['azmach'], audio_duration)
            timed_latin = convert_to_timed_format(mez['azmachen'], audio_duration)
            timed_english = convert_to_timed_format(mez['engTrans'], audio_duration)

            # Update database
            db.execute('''UPDATE mezmur SET
                        timed_geez = ?,
                        timed_latin = ?,
                        timed_english = ?
                        WHERE m_id = ?''',
                     (timed_geez, timed_latin, timed_english, m_id))

        db.commit()
        check_columns()
        db.close()

def convert_to_timed_format(lyrics, audio_duration=None):
    if not lyrics:
        return None
    
    lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
    if not lines:
        return None
    
    if audio_duration and audio_duration > 0:
        line_interval = audio_duration / len(lines)
    else:
        line_interval = 5
    
    timed_lines = []
    current_time = 0.0
    
    for line in lines:
        mins, secs = divmod(current_time, 60)
        timestamp = f"[{int(mins):02d}:{int(secs):02d}]"
        timed_lines.append(f"{timestamp} {line}")
        current_time += line_interval
    
    return '\n'.join(timed_lines)

def check_columns():
    app = create_app()
    with app.app_context():
        db = get_db()
        cursor = db.execute("PRAGMA table_info(mezmur)")
        columns = cursor.fetchall()
        for column in columns:
            print(column['name'])
            
if __name__ == '__main__':
    migrate_existing_lyrics()