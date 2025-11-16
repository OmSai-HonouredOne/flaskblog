from flask import Flask

app = Flask(__name__)


@app.route('/')
def home():
    print(app.root_path)
    return "Hello, World!"


if __name__ == '__main__':
    app.run(debug=True)