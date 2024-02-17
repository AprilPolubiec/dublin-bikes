import sqlalchemy as db
import json

# Opening JSON file
f = open('secure/credentials.json')
 
# returns JSON object as 
# a dictionary
data = json.load(f)

URI="dublin-bikes-db.cl020iymavvj.us-east-1.rds.amazonaws.com"
PORT=3306
DB="dublin-bikes"
USER="admin"

engine = db.create_engine("mysql+mysqldb://{}:{}@{}:{}/{}".format(USER, data["DB_PASSWORD"], URI, PORT, DB), echo=True)
print("Got engine")

with engine.connect() as conn:
    result = conn.execute("SHOW VARIABLES;")
    engine.close()
    for res in result:
        print(res)
