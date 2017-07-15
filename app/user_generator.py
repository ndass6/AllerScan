import pymysql, random

db = pymysql.connect('sql3.freemysqlhosting.net',
    'sql3185369',
    'X6qaMSPe7I',
    'sql3185369')
cursor = db.cursor()

num_users = 1000
prob_react = 0.05
allergens = ['Peanuts', 'Soy', 'Dairy', 'Egg', 'Gluten']
reactions = ['Skin Rash', 'Watery Eyes', 'Itchy Mouth', 'Swollen Lips', 'Difficulty Breathing',
'Vomiting', 'Nasal Congestion', 'Anaphylactic Shock']

# Generate num_users amount of new users
for i in range(num_users):
  # Calculate this user's user_id
  cursor.execute("SELECT COUNT(*) FROM `users`")
  user_id = cursor.fetchone()[0] + 1
  print("user_id: %d" % user_id)

  # Insert the user into the database
  cursor.execute("INSERT INTO `users`(`age`,`email`,`name`,`password`,`points`) VALUES (%s,%s,%s,%s,%s)",
    [random.randint(10, 60), "person_%d@email.com" % user_id, "person_%d" % user_id,
    "person_%d" % user_id, 0])
  db.commit()

  # Generate [1, len(allergens) - 1] random allergens for this user
  num_allergens = random.randint(1, len(allergens) - 1)
  # print("num_allergens: %d" % num_allergens)
  for allergen in random.sample(allergens, random.randint(1, len(allergens) - 1)):
    # print(allergen)
    cursor.execute("INSERT INTO `allergies`(`name`,`severity`,`user_id`) VALUES (%s,%s,%s)",
      [allergen, random.randint(1, 3), user_id])
    db.commit()

  # Select 100 random food_ids to generate reactions
  cursor.execute("SELECT `food_id` FROM `food` ORDER BY RAND() LIMIT 100")
  food_ids = cursor.fetchall()
  for food_id in food_ids:
    food_id = food_id[0]
    # prob_react chance of having a reaction to this food
    if random.randint(1, 100) <= prob_react * 100:
      # print("food_id: %d" % food_id)
      num_reactions = random.randint(1, 3)
      # print("num_reactions: %d" % num_reactions)

      # Generate [0, 2] random reactions to the current food
      for i in range(num_reactions):
        cursor.execute("INSERT INTO `food_symptoms`(`food_id`,`user_id`,`reaction`) VALUES (%s,%s,%s)",
          [food_id, user_id, reactions[random.randint(0, len(reactions) - 1)]])
        db.commit()

    # No reaction to this food
    else:
      cursor.execute("INSERT INTO `food_symptoms`(`food_id`,`user_id`,`reaction`) VALUES (%s,%s,%s)",
        [food_id, user_id, 'None'])
      db.commit()
db.close()