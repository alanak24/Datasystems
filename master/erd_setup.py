import os, io, uuid, pyodbc
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from master.data_setup import *
from dotenv import load_dotenv

load_dotenv()

# example using "Cleaned_Laptop_data.csv"
container_name = os.environ.get('CONTAINER_NAME')
db = AzureDB()
db.access_container(container_name)

class ModelAbstract:
    def __init__(self):
        self.columns = None
        self.entity = None
        self.name = None
        print("Model Created")
    
    def table_generator(self, name : str, columns : list):
        df = db.access_blob_csv(blob_name=name)
        entity = df[columns]
        entity = entity.drop_duplicates()

        self.entity = entity
        self.name = name
        self.columns = columns
    
    def load(self):
        if self.entity is not None:
            # Upload table to data warehouse
            db.upload_df_db(f'{self.name}', blob_df=self.entity)

            # Save locally as separate file
            self.entity.to_csv(f'./data/{self.name}.csv')
        else:
            print("Create entity first using table_generator")
        
    def set_primary_key(self, pk_columns : list):
        self.entity.set_index(pk_columns, inplace=True, verify_integrity=True)
    
    def add_foreign_key(self, ref_table : str, ref_column : list):
        # This method will create SQL command to add foreign key
        with eng.connect() as con:
            con.execute(f"""ALTER TABLE {self.name}
                        ADD CONSTRAINT FK_{self.name}_{ref_table}
                        FOREIGN KEY ({ref_column}), REFERENCES {ref_table} ({ref_column}))
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                        """)

class User(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.table_generator('Users', ['User_ID', 'User_FirstName', 'User_LastName', 'User_Budget', 'User_Major'])
        self.set_primary_key(['User_ID'])

class Brand(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.table_generator('Brand', ['Brand_ID', 'Brand_Name'])
        self.set_primary_key(['Brand'])
    
class Laptop(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.table_generator('Laptop', ['Laptop_ID', 'Brand_ID', 'Laptop_Model', 'Laptop_Price', 'Release_Date', 'Processor', 'Display', 'RAM', 'Storage', 'Operating_System', 'Laptop_Weight'])
        self.set_primary_key(['Laptop'])

class Usage(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.table_generator('Usage', ['Usage_ID', 'Usage_Type'])
        self.set_primary_key(['Usage_ID'])

class Major_Usage(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.table_generator('Major_Usage', ['Usage_ID', 'User_ID', 'Major_Usage_Notes'])
        self.set_primary_key(['Usage_ID', 'User_ID'])

class Recommendation(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.table_generator('Recommendation', ['User_ID', 'Laptop_ID', 'Date_Added'])
        self.set_primary_key(['User_ID', 'Laptop_ID'])
        self.add_foreign_key('User', ['User_ID'])
        self.add_foreign_key('Laptop', ['Laptop_ID'])
 
class Purchase_History(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.table_generator('Purchase_History', ['Purchase_History_ID', 'User_ID', 'Date_Created', 'Time_Created'])
        self.set_primary_key(['Purchase_History_ID', 'User_ID'])
        self.add_foreign_key('User', ['User_ID'])

class Purchased_Item(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.table_generator('Purchased_Item', ['Purchase_History_ID', 'User_ID', 'Laptop_ID', 'Date_Purchased'])
        self.set_primary_key(['Purchase_History_ID', 'User_ID', 'Laptop_ID'])
        self.add_foreign_key('Purchase_History', ['Purchase_History_ID', 'User_ID', 'Laptop_ID'])
    
class Review(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.table_generator('Review', ['Review_ID', 'Purchase_History_ID', 'User_ID', 'Laptop_ID', 'Review_Rating', 'Review_Comment'])
        self.set_primary_key(['Review_ID', 'Purchase_History_ID', 'User_ID', 'Laptop_ID'])
        self.add_foreign_key('Purchased_Item', ['Purchase_History_ID', 'User_ID', 'Laptop_ID'])

class Wishlist(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.table_generator('Wishlist', ['Wishlist_ID', 'User_ID', 'Date_Created', 'Time_Created'])
        self.set_primary_key(['Wishlist_ID', 'User_ID'])
        self.add_foreign_key('User', ['User_ID'])

class Wishlist_Item(ModelAbstract):
    def __init__(self):
        super().__init__()
        self.table_generator('Wishlist_Item', ['Wishlist_ID', 'User_ID', 'Laptop_ID', 'Date_Added', 'Time_Added'])
        self.set_primary_key(['Wishlist_ID', 'User_ID', 'Laptop_ID'])
        self.add_foreign_key('Wishlist', ['Wishlist_ID', 'User_ID', 'Laptop_ID'])
