import sklearn
import psycopg2 as psy

conn = psy.connect(database="region_waterloo", user="postgres", password="love2Learn",host="localhost", port="5433")
cur = conn.cursor()

cur.execute('select * from kw_survey.training_expanded')

training_data= cur.fetchall()

print training_data[1][3]
