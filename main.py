import os, uuid
import pandas as pd
import numpy as np
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
from master.data_setup import AzureDB
from master.db_connect import eng, conn

load_dotenv()

class ETLFlow():
    def __init__(self, database):
        self.db = database

        # CSV File Name
        self.blobs = [
            "Brand.csv"
            ,"User.csv"
            ,"Laptop.csv"
            ,"Usage.csv"
            ,"Purchase_History.csv"
            ,"Purchased_Item.csv"
            ,"Review.csv"
            ,"Recommendation.csv"
            ,"Wishlist.csv"
            ,"Wishlist_Item.csv"
                      ]
        
        # Entity Primary Keys
        self.primary_keys = {
            'Brand' : ['Brand_ID']
            ,'User' : ['User_ID']
            ,'Laptop' : ['Laptop_ID']
            ,'Purchase_History' : ['Purchase_History_ID']
            ,'Purchased_Item' : ['Purchase_History_ID', 'Laptop_ID']
            ,'Review' : ['Review_ID']
            ,'Usage' : ['Usage_ID']
            ,'Recommendation' : ['Recommendation_ID']
            ,'Wishlist' : ['Wishlist_ID']
            ,'Wishlist_Item' : ['Wishlist_ID', 'Laptop_ID']
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
        # Transform Data Frame
        if dataframe is None:
            print("No data to transform.")
            return None
        
        # Transform Date and Time Columns
        datetime_columns = ['Date_Added', 'Time_Added', 'Date_Created', 'Time_Created', 'Date_Purchased']

        columns = list(dataframe.columns)

        for col in datetime_columns:
            if col in columns:
                if 'Date' in col:
                    dataframe[col] = pd.to_datetime(dataframe[col], errors='coerce').dt.strftime('%Y-%m-%d')
                elif 'Time' in col:
                    dataframe[col] = pd.to_datetime(dataframe[col], format='%H:%M:%S', errors='coerce').dt.strftime('%H:%M:%S')
        
        primary_key = self.primary_keys[table_name]

        ## TRANSFORM BY ENTITY
        if table_name == 'User':
            # TASK: User + Usage on User_ID = User_ID
            usage_entity = self.db.access_blob_csv('Usage.csv')
            dataframe = pd.merge(dataframe, usage_entity, how='left', left_on='User_ID', right_on='User_ID')
            dataframe.drop(['Usage_Type', 'Usage_Note'], axis=1, inplace=True)

        if table_name == 'Laptop':
            # TASK: Laptop + Brand on Brand_Name to Brand_ID
            brand_entity = self.db.access_blob_csv('Brand.csv')
            dataframe = pd.merge(dataframe, brand_entity, how='left', left_on='Brand_Name', right_on='Brand_Name')
            dataframe.drop(['Brand_Name', 'Brand_Name'], axis=1, inplace=True)

            # TASK: Format Price
            dataframe['Laptop_Price'] = dataframe['Laptop_Price'].astype(str)
            for row in range(len(dataframe)):
                entry = dataframe.at[row, 'Laptop_Price']
                entry = entry[:-2] + '.' + entry[-2:]
                dataframe.at[row, 'Laptop_Price'] = entry
            
            # TASK: Format RAM_GB, SSD_GB, HDD_GB
            gb_columns = ['RAM_GB', 'SSD', 'HDD']
            for col in gb_columns:
                dataframe[col] = dataframe[col].astype(str)
                for (row) in range(len(dataframe)):
                    entry = dataframe.at[row, col]
                    entry = entry.split(" ")[0]
                    dataframe.at[row,col] = entry

            # TASK: Format Touchscreen
            dataframe['Touchscreen'] = dataframe['Touchscreen'].map({'Yes': True, 'No': False})

            # # TASK: Nullify 'Missing' in Display_Size
            dataframe['Display_Size'] = dataframe['Display_Size'].replace('Missing', np.nan)

            # TASK: Transform Binary Columns
            dataframe['Laptop_ID'] = dataframe['Laptop_ID'].astype(str)
            dataframe['Brand_ID'] = dataframe['Brand_ID'].astype(str)
        
        if table_name == 'Usage':
            # TASK: Get Distinct Usage entries
            dataframe.drop_duplicates(subset=primary_key, keep='first', inplace=True)

            # TASK: Drop User column
            dataframe.drop(['User_ID'], axis=1, inplace=True)
        
        if table_name == 'Recommendation':
            # TASK: Assign Recommendation_ID
            if primary_key[0] not in columns:
                dataframe.insert(0, f'{table_name}_ID', range(1000, 1000 + len(dataframe)))

        # TASK: Transform Binary Columns
        col_to_convert = [col for col in dataframe.columns if dataframe[col].dtype == 'int64']

        for col in col_to_convert:
            dataframe[col] = dataframe[col].astype(str)
        
        # Confirm Transformed Columns and data types
        print(list(dataframe.columns))
        print(dataframe.dtypes)
        
        # Sort Primary Key
        if primary_key:
            dataframe.sort_values(by=primary_key, inplace=True)
        
        # Remove Duplicates
        dataframe.drop_duplicates(subset=primary_key, keep='first', inplace=True)
        
        # Save Transformed Entity
        transformedDF = dataframe.to_csv('./data/{dataFrame}', sep=',',header=True)

        # Return Transformed Dataframe
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

if __name__ == '__main__':
    main()