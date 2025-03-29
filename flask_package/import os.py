import os
import base64
from datetime import datetime
from flask import request as rq, send_from_directory, render_template
# ... other necessary imports ...

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
