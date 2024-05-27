import pandas as pd
from db_connect import eng, conn

# Create Cursor Connection
cur = conn.cursor()

# List all tables
tables = ["Brand",
          "Laptop",
          "User",
          "Purchase_History",
          "Purchased_Item",
          "Review",
          "Wishlist",
          "Wishlist_Item"
          ]

# Select all query
for t in tables:
    try: 
        print(t)
        query = f"SELECT * FROM {t}"
        df = pd.read_sql_query(query, conn)
        print(f"Date from table {t}")
        print(df)
    except Exception as e:
        print(f"Error fetching data from table {t}: {e}")