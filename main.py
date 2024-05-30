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

        # CSV File Name
        self.blobs = ["Brand.csv"
                      ,"Laptop.csv"
                      ,"User.csv"
                      ,"Purchase_History.csv"
                      ,"Purchased_Item.csv"
                      ,"Recommendation.csv"
                      ,"Review.csv"
                      ,"Usage.csv"
                      ,"Wishlist.csv"
                      ,"Wishlist_Item.csv"
                      ]
        
        # Entity Primary Keys
        self.primary_keys = {
            'Brand': ['Brand_ID'],
            'Laptop': ['Laptop_ID'],
            'User': ['User_ID'],
            'Purchase_History': ['Purchase_History_ID', 'User_ID'],
            'Purchased_Item': ['Purchase_History_ID', 'Laptop_ID'],
            'Recommendation':['User_ID', 'Laptop_ID'],
            'Review': ['Review_ID'],
            'Usage': ['Usage_ID'],
            'Wishlist': ['Wishlist_ID', 'User_ID'],
            'Wishlist_Item': ['Wishlist_ID', 'Laptop_ID']
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
        
        print(f"Transforming {table_name}, initial columns: {list(dataframe.columns)}")

        # Transform Date and Time Columns
        datetime_columns = ['Date_Added', 'Time_Added', 'Date_Created', 'Time_Created', 'Date_Purchased']

        for col in datetime_columns:
            if col in dataframe.columns:
                if 'Date' in col:
                    dataframe[col] = pd.to_datetime(dataframe[col], errors='coerce').dt.date
                if 'Time' in col:
                    dataframe[col] = pd.to_datetime(dataframe[col], format='%H:%M:%S', errors='coerce').dt.time

        # Handle specific entity transformations
        primary_key = self.primary_keys.get(table_name, None)
        
        if table_name == 'Laptop':
            brand_entity = self.db.access_blob_csv('Brand.csv')
            dataframe = pd.merge(dataframe, brand_entity, how='left', left_on='Brand', right_on='Brand_Name')
            dataframe = dataframe.drop(['Brand', 'Brand_Name'], axis=1)
            
            if 'Laptop_ID' not in dataframe.columns:
                dataframe.insert(0, 'Laptop_ID', range(1000, 1000 + len(dataframe)))

        elif table_name == 'Purchased_Item':
            purchase_history_entity = self.db.access_blob_csv('Purchase_History.csv')
            dataframe = pd.merge(dataframe, purchase_history_entity, how='left', left_on='Purchase_History_ID', right_on='Purchase_History_ID')
            

        elif table_name == 'Review':
            purchased_item_entity = self.db.access_blob_csv('Purchased_Item.csv')
            dataframe = pd.merge(dataframe, purchased_item_entity, how='left', left_on=['Purchase_History_ID', 'Laptop_ID'], right_on=['Purchase_History_ID', 'Laptop_ID'])

        elif table_name == 'Wishlist_Item':
            wishlist_entity = self.db.access_blob_csv('Wishlist.csv')
            dataframe = pd.merge(dataframe, wishlist_entity[['Wishlist_ID', 'Time_Created']], how='left', left_on='Wishlist_ID', right_on='Wishlist_ID')

        elif table_name == 'Major_Usage':
            usage_entity = self.db.access_blob_csv('Usage.csv')
            dataframe = pd.merge(dataframe, usage_entity, how='left', left_on='Usage_ID', right_on='Usage_ID')


        if primary_key:
            dataframe.sort_values(by=primary_key, inplace=True)
            dataframe.drop_duplicates(subset=primary_key, keep='first', inplace=True)

        dataframe.to_csv(f'./data/{table_name}.csv', sep=',', header=True)
        print('Transformation Completed')
        return dataframe
        # Laptop
    #     primary_key = self.primary_keys[table_name]
    #     if table_name == 'Laptop':
    #         # TASK: Laptop + Brand on Brand_Name to Brand_ID
    #         brand_entity = self.db.access_blob_csv('Brand.csv')
    #         dataframe = pd.merge(dataframe, brand_entity, how='left', left_on='Brand', right_on='Brand_Name')
    #         dataframe = dataframe.drop(['Brand', 'Brand_Name'], axis=1)

    #         # TASK: Format Price
    #         # dataframe['Laptop_Price'] = dataframe['Laptop_Price'].astype(str)
    #         # for row in range(len(dataframe)):
    #         #     entry = dataframe.at[row, 'Laptop_Price']
    #         #     entry = entry[:-2] + entry[-2:]
    #         #     row['Laptop_Price']
    #         #     print(row)

    #         # TASK: Form Unique ID's 
    #         if primary_key[0] not in columns:
    #             new_pk = f'{table_name}_ID'
    #             dataframe.insert(0, f'{new_pk}', range(1000, 1000 + len(dataframe)))

    #     # TASK: Merge join tables [Wishlist + Wishlist Item, Purchase History + Purchased Item, Purchased Item + Review]

    #     # Add primary key if non existant
    #     # primary_key = self.primary_keys[table_name]

    #     # if primary_key[0] not in columns:
    #     #     new_pk = f'{table_name}_ID'
    #     #     dataframe.insert(0, f'{new_pk}', range(1000, 1000 + len(dataframe)))

        
    #     # Confirm Transformed Columns
    #     print(list(dataframe.columns))
        
    #     # Sort Primary Key
    #     if primary_key:
    #         dataframe.sort_values(by=primary_key, inplace=True)
        
    #     # Remove Duplicates
    #     dataframe.drop_duplicates(subset=primary_key, keep='first', inplace=True)
        
    #     # Save Transformed Entity
    #     transformedDF = dataframe.to_csv('./data/{dataFrame}', sep=',',header=True)

    #     # Return Transformed Dataframe
    #     print(f'Transformation Completed')
    #     return dataframe

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