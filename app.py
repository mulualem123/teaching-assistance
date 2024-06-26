from flask_package import app


##Checks the Flask app's configuration to make sure it is listening on the correct port. This will print the port the Flask app is listening on when it is started
if __name__ == "__main__":
    print('Listening on port', app.config['SERVER_PORT'])
    app.run(host='0.0.0.0', port=app.config['SERVER_PORT'])
    #app.run(debug=True)