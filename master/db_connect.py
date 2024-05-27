import sqlite3
import sqlalchemy as db

db_name = 'LaptopRecommendation'

conn = sqlite3.connect("LaptopRecommendation.db")
db_URI = "sqlite:///LaptopRecommendation.db"

eng = db.create_engine(db_URI)
sqlalchemy_conn = eng.connect()