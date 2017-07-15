import pymysql

db = pymysql.connect('sql3.freemysqlhosting.net',
  'sql3185369',
  'X6qaMSPe7I',
  'sql3185369')
cursor = db.cursor()

cursor.execute("SELECT `food_id`, `user_id`, `reaction` FROM `food_symptoms`")
food_ids, user_ids, reactions = zip(*cursor.fetchall())

all_data = {}
for pos, food_id in enumerate(food_ids):
  if food_id not in all_data:
    # First index of list counts number of reactions, second index of list counts total responses
    all_data[food_id] = [0, 0]

  # There is a reaction
  if reactions[pos] != "None":
    all_data[food_id] = [all_data[food_id][0] + 1, all_data[food_id][1] + 1]

  # There is not a reaction
  else:
    all_data[food_id] = [all_data[food_id][0], all_data[food_id][1] + 1]
  print "%s/%s" % (pos, len(food_ids))

for food_id in all_data:
  cursor.execute("UPDATE `food` SET `percent_react`=%s", [float(all_data[food_id][0]) / float(all_data[food_id][1])])
  print float(all_data[food_id][0]) / float(all_data[food_id][1])
  print "%s/%s" % (pos, len(food_ids))

db.commit()