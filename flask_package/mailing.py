from flask_mail import Mail, Message

class Gmail:
    def __init__(self, app):
        self.app=app
        
    def reminder():
        mail = Mail(app)
        app.config['MAIL_SERVER']='smtp.gmail.com'
        app.config['MAIL_PORT'] = 465
        app.config['MAIL_USERNAME'] = 'hailomulalem@gmail.com'
        app.config['MAIL_PASSWORD'] = '@Newlife#2009'
        app.config['MAIL_USE_TLS'] = False
        app.config['MAIL_USE_SSL'] = True
        
        msg = Message('Hello', sender = 'hailomulalem@gmail.com', recipients = ['mulualem.hailom@gmail.com'])
        msg.body = "Hello Flask message sent from Flask-Mail"
        mail.send(msg)
        flash("email have been sent successfuly")
        return "Sent"


@app.route('/')
def index():
    msg = Message('Hello', sender='your@gmail.com', recipients=['someone@example.com'])
    msg.body = 'This is a scheduled email sent from a Flask application.'
    # schedule the email to be sent one minute later
    send_time = datetime.now() + timedelta(minutes=1)
    msg.send_scheduled(send_time)
    # add the send_scheduled method to the scheduler
    scheduler.add_job(msg.send_scheduled, 'date', run_date=send_time)
    return 'Email scheduled!'