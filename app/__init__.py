from flask import Flask, render_template, jsonify, request, g
from flaskext.mysql import MySQL

from sklearn.neighbors import KNeighborsClassifier
import numpy as np

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'ndass1'
app.config['MYSQL_DATABASE_PASSWORD'] = 'database'
app.config['MYSQL_DATABASE_DB'] = 'ndass1$default'
app.config['MYSQL_DATABASE_HOST'] = 'ndass1.mysql.pythonanywhere-services.com'
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

  # Retrieve user symptom info for people that had a reaction
  getCursor().execute("SELECT `user_id`, `reaction` FROM `food_symptoms` WHERE `food_id`=%s AND NOT `reaction`='None'", [food_id])
  user_ids, reactions = zip(*getCursor().fetchall())

  # Retreive recommender info
  # user_vector = create_user_vector(user_id, True)
  # getCursor().execute("SELECT `food_id`, `user_id`, `reaction` FROM `food_symptoms`")
  # food_ids, user_ids, reactions = zip(*getCursor().fetchall())
  # product_users = {}
  # product_reactions = {}
  # for pos, food_id in enumerate(food_ids):
  #   if food_id not in product_users:
  #     product_users[food_id] = []
  #     product_reactions[food_id] = []
  #   product_users[food_id].append(create_user_vector(user_ids[pos]))
  #   product_reactions[food_id].append([1, 0] if reactions[pos] == "None" else [0, 1])
  #   print "%d/%d" % (pos, len(food_ids))

  # recommender = Recommender()
  # recommender.train(product_users, product_reactions, food_id)
  # nearest = recommender.get_similar_users(user_vector)
  # similar_users = [user_ids[near] for near in nearest]
  # percent_reaction = recommender.predict_reaction(user_vector)
  # print percent_reaction, similar_users, user_vector

  if hasattr(g, 'mysql_db'):
    g.mysql_db.close()

  return jsonify(food_name=food_name, percent_react=percent_react, user_ids=user_ids, reactions=reactions,
    similar_users=similar_users, percent_reaction=percent_reaction)

def create_user_vector(user_id, debug=False):
  getCursor().execute("SELECT `name`, `severity` FROM `allergies` WHERE `user_id`=%s", [user_id])
  user_allergens, severity = zip(*getCursor().fetchall())
  allergens = ['Peanuts', 'Soy', 'Dairy', 'Egg', 'Gluten']
  
  # Create a one dimensional array of one-hot encodings of allergen severity based on the severity of each allergy
  user_vector = []
  for allergen in allergens:
    user_vector += [0]*3
    if allergen in user_allergens:
      user_vector[severity[user_allergens.index(allergen)] - 4] = 1
  if debug:  
    print user_allergens, severity, user_vector
  return user_vector

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

class Recommender:
  def __init__(self, n_neighbors=5):
    self.classifier = KNeighborsClassifier(n_neighbors=n_neighbors)

  def train(self, users, reactions, product):

    # Dictionary of the form {product1: [user_vec1, user_vec2, ...], product2: [user_vec1, user_vec2, ...]}
    user_vecs = users[product]

    # Dictionary of the form {product1: [reaction1, reaction2, ...], product2: [reaction2, reaction2, ...]}
    reaction_vec = reactions[product]

    self.classifier.fit(user_vecs, reaction_vec)

  def get_similar_users(self, user_vec):
    return self.classifier.kneighbors(user_vec)

  def predict_reaction(self, user_vec):
    return self.classifier.predict_proba(user_vec)

if __name__ == '__main__':
  app.run()
