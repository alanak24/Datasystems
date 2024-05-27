import os, uuid
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
from master.data_setup import AzureDB
from master.db_connect import eng, conn

load_dotenv()

class ETLFlow():
    def __init__(self, database):
        self.db = database

        # CSV Files
        self.blobs = ["Brand.csv"
                      ,"Laptop.csv"
                      ,"User.csv"
                      ,"Purchase_History.csv"
                      ,"Purchased_Item.csv"
                      ,"Review.csv"
                      ,"Recommendation.csv"
                    #   ,"Usage.csv"
                      ,"Wishlist.csv"
                      ,"Wishlist_Item.csv"
                      ]
        
        # Primary Keys
        self.primary_keys = {
            'Brand' : ['Brand_ID']
            ,'Laptop' : ['Laptop_ID']
            ,'Purchase_History' : ['Purchase_History_ID', 'User_ID']
            ,'Purchased_Item' : ['Purchase_History_ID', 'User_ID', 'Laptop_ID']
            ,'Review' : ['Review_ID', 'User_ID', 'Purchase_History_ID', 'Laptop_ID']
            ,'Usage' : ['Usage_ID']
            ,'User' : ['User_ID']
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


    def transform(self, dataframe, table_name):
        # Transform Data Type
        if dataframe is None:
            print("No data to transform.")
            return None
        
        # Transform Date and Time Columns
        datetime_columns = ['Date_Added', 'Time_Added', 'Date_Created', 'Time_Created', 'Date_Purchased', 'Release_Date']

        columns = list(dataframe.columns)

        for col in datetime_columns:
            if col in columns:
                if 'Date' in col:
                    dataframe[col] = pd.to_datetime(dataframe[col], errors='coerce')
                if 'Time' in col:
                    dataframe[col] = pd.to_datetime(dataframe[col], format='%H:%M:%S', errors='coerce').dt.time
        
        ## TRANSFORM BY ENTITY
        # Laptop
        if table_name == 'Laptop':
            # Laptop + Brand on Brand_Name to Brand_ID
            brand_entity = self.db.access_blob_csv('Brand.csv')
            dataframe = pd.merge(dataframe, brand_entity, how='left', left_on='Brand', right_on='Brand_Name')
            dataframe = dataframe.drop(['Brand', 'Brand_Name'], axis=1)
            # TASK: Format Price
            # dataframe['Laptop_Price'] = dataframe['Laptop_Price'].astype(str)
            # for row in range(len(dataframe)):
            #     entry = dataframe.at[row, 'Laptop_Price']
            #     entry = entry[:-2] + entry[-2:]
            #     row['Laptop_Price']
            #     print(row)

        # TASK: Merge join tables [Wishlist + Wishlist Item, Purchase History + Purchased Item, Purchased Item + Review]

        # Add primary key if non existant
        primary_key = self.primary_keys[table_name]

        if primary_key[0] not in columns:
            new_pk = f'{table_name}_ID'
            dataframe.insert(0, f'{new_pk}', range(1000, 1000 + len(dataframe)))
        
        print(list(dataframe.columns))
        
        # Sort Primary Key
        if primary_key:
            dataframe.sort_values(by=primary_key, inplace=True)
        
        # Remove Duplicates
        dataframe.drop_duplicates(subset=primary_key, keep='first', inplace=True)
        
        transformedDF = dataframe.to_csv('./data/{dataFrame}', sep=',',header=True)

        print(f'Transformation Completed')
        return dataframe

    def load(self, dataframe, table_name):
        # Upload dataframe to SQLite3
        if dataframe is not None:
            print(f'Starting loading process for {table_name}')
            self.db.upload_df_db(table_name, dataframe)
            print(f'Loading completed for {table_name}')
        else:
            print(f'No data to load for {table_name}')
            

def main():
    db = AzureDB()
    db.access_container("test-merge")

    MainETL = ETLFlow(db)
    
    for b in MainETL.blobs:
        # Extract
        entity = MainETL.extract(b)
        table_name = b.split('.')[0]

        # Transform
        transformed_entity = MainETL.transform(entity, table_name)

        # Load
        MainETL.load(transformed_entity, table_name)

        cur = conn.cursor()

        
    #     for row in cur.execute(f"SELECT * FROM {table_name}"):
    #         print(row)


if __name__ == '__main__':
    main()