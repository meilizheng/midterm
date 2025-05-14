from api import app,db
#Creates database 
with app.app_context():
  db.create_all()
#run python3 create_db.py
# Creates the database and folder called instance