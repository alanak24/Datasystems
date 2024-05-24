import os, uuid
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
from master.data_setup import AzureDB

load_dotenv()

class ETLFlow():
    def __init__(self, database):
        self.db = database

        # CSV Files
        self.blobs = ["Brand.csv"
                      ,"Laptop.csv"
                      ,"Major_Usage.csv"
                      ,"Purchase_History.csv"
                      ,"Purchased_Item.csv"
                      ,"Review.csv"
                      ,"Usage.csv"
                      ,"Users.csv"
                      ,"Wishlist.csv"
                      ,"Wishlist_Item.csv"
                      ]
        
        
        self.primary_keys = {
            'Brand' : ['Brand_ID']
            ,'Laptop' : ['Laptop_ID']
            ,'Major_Usage' : ['Usage_ID', 'User_ID']
            ,'Purchase_History' : ['Purchase_History_ID', 'User_ID']
            ,'Purchased_Item' : ['Purchase_History_ID', 'User_ID', 'Laptop_ID']
            ,'Review' : ['Review_ID', 'User_ID', 'Purchase_History_ID', 'Laptop_ID']
            ,'Usage' : ['Usage_ID']
            ,'Users' : ['User_ID']
            ,'Wishlist' : ['Wishlist_ID', 'User_ID']
            ,'Wishlist_Item' : ['Wishlist_ID', 'User_ID', 'Laptop_ID']
        }

    
    def extract(self, csv_file : str):
        # Extract using pandas: open csv, extract data
        print(f'Extracting Data from CSV file: {csv_file}')
        dataFrame = self.db.access_blob_csv(csv_file)
        if dataFrame is not None:
            self.entity = dataFrame
            print(f'CSV File: {csv_file} has {len(self.entity.index)} rows and {len(self.entity.columns)} columns.')
            print(f'Extraction Completed')
            return self.entity
        else:
            print(f'Failed to extract from {csv_file}')
            return None


    def transform(self, entity, table_name):
        # Transform Data Type
        if entity is None:
            print("No data to transform.")
            return None
        
        # Date Time Transformations
        datetime_columns = ['Date_Added', 'Time_Added', 'Date_Created', 'Time_Created', 'Date_Purchased', 'Release_Date']

        columns = list(entity.columns)

        for col in datetime_columns:
            if col in columns:
                if 'Date' in col:
                    entity[col] = pd.to_datetime(entity[col], errors='coerce')
                if 'Time' in col:
                    entity[col] = pd.to_datetime(entity[col], format='%H:%M:%S', errors='coerce').dt.time

        # Sort Primary Key
        primary_key = self.primary_keys[table_name]
        if primary_key:
            entity.sort_values(by=primary_key, inplace=True)
        
        # Remove Duplicates
        entity.drop_duplicates(subset=primary_key, keep='first', inplace=True)
        
        # TASK: Merge join tables [Wishlist + Wishlist Item, Purchase History + Purchased Item, Purchased Item + Review]
        transformedDF = entity.to_csv('./data/{dataFrame}', sep=',',header=True)

        print(f'Transformation Completed')
        return entity
    
    def load(self, entity, table_name):

        if entity is not None:
            print(f'Starting loading process for {table_name}')
            self.db.upload_df_db(table_name, entity)
            print(f'Loading completed for {table_name}')
        else:
            print(f'No data to load for {table_name}')
            
def main():
    db = AzureDB()
    db.access_container("test-merge")

    MainETL = ETLFlow(db)
    
    # Extract
    for b in MainETL.blobs:
        entity = MainETL.extract(b)
        table_name = b.split('.')[0]
        # Transform
        transformed_entity = MainETL.transform(entity, table_name)
        # Load
        MainETL.load(transformed_entity, table_name)


if __name__ == '__main__':
    main()