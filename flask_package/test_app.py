from flask import Flask

app = Flask(__name__)

@app.before_first_request
def before_first_request_func():
    print("This runs before the first request")

if __name__ == "__main__":
    app.run(debug=True)