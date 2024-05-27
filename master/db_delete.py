from pathlib import Path

def delete_db():
    print(f"Deleting existing database LaptopRecommendation.db")
    try:
        Path("LaptopRecommendation.db").unlink()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    delete_db()