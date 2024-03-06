from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    print("Request received for /")  # Print statement for logging
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()
