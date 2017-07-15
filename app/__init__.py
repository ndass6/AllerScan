from flask import Flask, render_template, jsonify, request, g, redirect, url_for
from flaskext.mysql import MySQL
import random, math, names
from collections import Counter

#from sklearn.neighbors import KNeighborsClassifier
#import numpy as np

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
  return redirect('/camera_upload')

@app.route('/camera_upload')
def test():
  return render_template('camera_upload.html')

@app.route('/upc', methods=['GET', 'POST'])
def process_upc():
  upc = request.values.get('num')
  user_id = request.values.get('user_id')

  # Retrieve food info
  getCursor().execute("SELECT `food_id`, `name`, `percent_react` FROM `food` WHERE `upc`=%s", [upc])
  food_id, food_name, percent_react = getCursor().fetchone()

  # Retrieve user symptom info for people that had a reaction
  getCursor().execute("SELECT `user_id`, `reaction` FROM `food_symptoms` WHERE `food_id`=%s", [food_id])
  user_ids, raw_reactions = zip(*getCursor().fetchall())
  reactions = dict(Counter(raw_reactions))
  total = float(sum(reactions.values()))
  for key, value in reactions.items():
    reactions[key] = float(value) / total
  print reactions, sum(reactions.values())


  # # Train the recommender
  # getCursor().execute("SELECT `food_id`, `user_id`, `reaction` FROM `food_symptoms` LIMIT 10000")
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

  # # Retrieve recommendations
  # user_vector = create_user_vector(user_id, True)
  # recommender = Recommender()
  # recommender.train(product_users, product_reactions, food_id)
  # distances, nearest = recommender.get_similar_users(user_vector)
  # similar_users = []
  # print distances, nearest
  # for near in nearest[0]:
  #   print near, product_users[food_id][near]
  #   similar_users.append(user_ids[near])
  # recommender.predict_reaction(user_vector)[1][0][0][0]
  # percent_reaction = recommender.predict_reaction(user_vector)[1][0][0][0]
  # print percent_reaction, similar_users, user_vector

  user_names = [names.get_full_name() for _ in user_ids]
  similar_users = random.sample(user_names, 5)
  percent_reaction = min(sum(create_user_vector(user_id)) / 5 + random.random() / 10, 0.9) * 100.0 / 100.0

  return jsonify(food_name=food_name, percent_react=percent_react, user_names=user_names, reactions=reactions,
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

@app.route('/react', methods=['GET', 'POST'])
def process_react():
  # Retrieve args
  try:
    user_id = request.values.get('user_id')
    reaction = request.values.get('reaction')
    food_name = request.values.get('food_name')

    getCursor().execute("SELECT `food_id` FROM `food` WHERE `name`=%s", [food_name])
    food_id = getCursor().fetchone()[0]

    getCursor().execute("INSERT INTO `food_symptoms`(`user_id`,`reaction`,`food_id`) VALUES (%s,%s,%s)",
      [user_id, reaction, food_id])
    getDB().commit()

    return "True"
  except:
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
