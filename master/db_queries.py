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

def query_database(conn, query):
    print(query)
    df = pd.read_sql_query(query, conn)
    print(df)
    return df

def save_result(df):
    save = input("Save file? (y/n): ")
    if save == 'y':
        file_name = input("Enter File Name: ")
        df.to_csv(f'./data/{file_name}.csv', sep=',', index=False, encoding='UTF-8')

if __name__ == "__main__":

    while True:
        userInput = input("Enter Query: ")

        if (userInput.lower()) == "quit":
            break

        else:
            df = query_database(conn, userInput)

            save_result(df)

# # Select all query
# for t in tables:
#     try: 
#         print(t)
#         query = f"SELECT * FROM {t}"
#         df = pd.read_sql_query(query, conn)
#         print(f"Date from table {t}")
#         print(df)
#     except Exception as e:
#         print(f"Error fetching data from table {t}: {e}")

# Select unique users from purchase_history
# try: 
#     purchase_users = pd.read_sql_query("SELECT DISTINCT(User_ID) FROM Purchase_History", conn)
#     print(purchase_users)
# except Exception as e:
#     print(f"Error in retrieving User_ID's from Purchase_History: {e}")

# try:
#     print("yes")
# except Exception as e:
#     print(e)
    