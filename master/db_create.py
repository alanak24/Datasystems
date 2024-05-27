from db_connect import eng
from entities import Base

def create_db():
    print(f"Creating emtpy database LaptopRecommendation...")
    Base.metadata.create_all(eng)

if __name__ == "__main__":
    create_db()