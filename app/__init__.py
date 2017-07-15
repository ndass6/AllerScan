from flask import Flask, render_template, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ""
db = SQLAlchemy(app)

from app.logic import fn

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/api')
def api():
    return jsonify(text=fn())

if __name__ == '__main__':
    app.run(debug=True)
