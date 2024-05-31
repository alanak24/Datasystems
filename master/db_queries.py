import pandas as pd
from db_connect import eng, conn

# Create Cursor Connection
cur = conn.cursor()

# List all tables
tables = ["Brand",
          "Usage",
          "User",
          "Laptop",
          "Purchase_History",
          "Purchased_Item",
          "Review",
          "Wishlist",
          "Wishlist_Item"
          ]

def query_database(conn, query):
    try:
        print(query)
        df = pd.read_sql_query(query, conn)
        print(df)
        return df
    except Exception as e:
        print(f"Could not query database: {e}")

def save_result(df):
    save = input("Save file? (y/n): ")
    if save.lower() == 'y':
        file_name = input("Enter File Name: ")
        df.to_csv(f'./data/{file_name}.csv', sep=',', index=False, encoding='UTF-8')
    else:
        print("Query result not saved.")

if __name__ == "__main__":

    while True:
        userInput = input("Enter Query: ")

        if (userInput.lower()) == "quit":
            break

        else:
            df = query_database(conn, userInput)

            save_result(df)