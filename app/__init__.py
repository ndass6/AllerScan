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

@app.route('/')
def hello_world():
  return render_template('index.html')

@app.route('/upc')
def process_upc():
  # Retrieve args
  upc = request.args.get('num')
  user_id = request.args.get('user_id')

  # Retrieve food info
  getCursor().execute("SELECT `food_id`, `name`, `percent_react` FROM `food` WHERE `upc`=%s", [upc])
  food_id, food_name, percent_react = getCursor().fetchone()

  # Retrieve user symtom info for people that had a reaction
  getCursor().execute("SELECT `user_id`, `reaction` FROM `food_symptoms` WHERE `food_id`=%s AND NOT `reaction`='None'", [food_id])
  user_ids, reactions = zip(*getCursor().fetchall())

  if hasattr(g, 'mysql_db'):
    g.mysql_db.close()

  return jsonify(food_name=food_name, percent_react=percent_react, user_ids=user_ids, reactions=reactions)

@app.route('/react')
def process_react():
  # Retrieve args
  try:
    user_id = request.args.get('user_id')
    reaction = request.args.get('reaction')
    food_name = request.args.get('food_name')

    getCursor().execute("SELECT `food_id` FROM `food` WHERE `name`=%s", [food_name])
    food_id = getCursor().fetchone()[0]

    getCursor().execute("INSERT INTO `food_symptoms`(`user_id`,`reaction`,`food_id`) VALUES (%s,%s,%s)",
      [user_id, reaction, food_id])
    getDB().commit()

    if hasattr(g, 'mysql_db'):
      g.mysql_db.close()

    return "True"
  except:
    if hasattr(g, 'mysql_db'):
      g.mysql_db.close()

    return "False"

if __name__ == '__main__':
  app.run()
