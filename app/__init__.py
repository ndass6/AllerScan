from flask import Flask, render_template, jsonify, request, g
from flaskext.mysql import MySQL

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'sql3185369'
app.config['MYSQL_DATABASE_PASSWORD'] = 'X6qaMSPe7I'
app.config['MYSQL_DATABASE_DB'] = 'sql3185369'
app.config['MYSQL_DATABASE_HOST'] = 'sql3.freemysqlhosting.net'
mysql.init_app(app)

def getDB():
  """Opens a new database connection if there is none yet for the
  current application context.
  """
  if not hasattr(g, 'mysql_db'):
    g.mysql_db = mysql.connect()
  
  return g.mysql_db

def getCursor():
  if not hasattr(g, 'mysql_db'):
    g.mysql_db = mysql.connect()

  if not hasattr(g, 'cursor'):
    g.cursor = g.mysql_db.cursor()

  return g.cursor

@app.teardown_appcontext
def closeDB(error):
  """Closes the database again at the end of the request."""
  if hasattr(g, 'mysql_db'):
    g.mysql_db.close()

# Secret key is necessary for creating user sessions within the app
app.secret_key = 'D8K27qBS8{8*sYVU>3DA530!0469x{'

@app.route('/')
def hello_world():
  return render_template('index.html')

if __name__ == '__main__':
  app.run()
