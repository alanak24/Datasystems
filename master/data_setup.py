import os, io, uuid, pyodbc
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# Load all .env variables
account_storage = os.environ.get('ACCOUNT_STORAGE')
username = os.environ.get('USERNAME_AZURE')
password = os.environ.get('PASSWORD')
server = os.environ.get('SERVER')
database = os.environ.get('DATABASE')
connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')

# Create pyodbc engine
eng = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+18+for+SQL+Server')

class AzureDB():
    def __init__(self, local_path="./data", account_storage=account_storage):
        self.local_path = local_path
        self.account_url = f"https://{account_storage}.blob.core.windows.net"
        self.default_credential = DefaultAzureCredential()
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = None  # Initialize the container client as None

    # create or access container {container_name }
    def access_container(self, container_name):
        # Create Container
        try:
            self.container_client = self.blob_service_client.create_container(container_name)
            print(f"Creating container {container_name}")
            self.container_name = container_name
        
        # Access Container
        except Exception as ex:
            print(f"Accessing container {container_name}")
            self.container_client = self.blob_service_client.get_container_client(container=container_name)
            self.container_name = container_name
    
    # delete container
    def delete_container(self):
        print("Deleting container")
        self.container_client.delete_container()
        print("Delete complete")
    
    # upload container
    def upload_blob(self, blob_name, blob_data = None):
        local_file_name = blob_name
        upload_file_path = os.path.join(self.local_path, local_file_name)
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=local_file_name)
        print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

        with open(file=upload_file_path, mode="rb") as data:
            blob_client.upload_blob(data)

        # if blob_data is not None:
        #     blob_client.create_blob_from_text(container_name=self.container_name, blob_name=blob_name, text=blob_data)
        # else:
        #     # Upload the created file
        #     with open(file=upload_file_path, mode="rb") as data:
        #         blob_client.upload_blob(data)
    
    # list blobs
    def list_blobs(self):
        print("\nBlob List: ")
        blob_list = self.container_client.list_blobs()
        for blob in blob_list:
            print("\t" + blob.name)

    # download blob to local storage
    def download_blob(self, blob_name):
        download_file_path = os.path.join(self.local_path, blob_name)
        print("\nDownloading blob to \n\t" + download_file_path)
        with open(file=download_file_path, mode="wb") as download_file:
            download_file.write(self.container_client.download_blob(blob_name).readall())
    
    # deleting a blob
    def delete_blob(self, container_name: str, blob_name: str):
        print("\nDeleting blob " + blob_name)
    
    # acces blob csv
    def access_blob_csv(self, blob_name):
        try:
            print(f"Accessing blob {blob_name}")

            df = pd.read_csv(io.StringIO(self.container_client.download_blob(blob_name).readall().decode('utf-8')))
            return df
        
        except Exception as ex:
            print("Exception: ")
            print(ex)
    
    def upload_df_db(self, blob_name, blob_df):
        # Upload blob to table
        print(f"Uploading {blob_name} to SQL database...")
        blob_df.to_sql(blob_name, eng, if_exists='replace', index=False)
        
        with eng.connect() as con:
            trans = con.begin()
            fk_columns = []
            
            if f'{blob_name}_id' == col:
                # Set blob_name_ID as Primary Key
                con.execute(text(f'ALTER TABLE [dbo].[{blob_name}] ALTER COLUMN {blob_name}_ID int NOT NULL'))
                con.execute(text(f'ALTER TABLE [dbo].[{blob_name}] ADD CONSTRAINT PK_{blob_name} PRIMARY KEY CLUSTERED ({blob_name}_ID) ASC'))
                trans.commit()

            # Extract foreign keys
            for col in blob_df.columns:
                if 'ID' in col.upper() and col != f'{blob_name}_ID':
                    fk_columns.append(col)
            
            for fk in fk_columns:
                fk_ref = fk.replace("_ID", "")
                con.execute(text(f'ALTER TABLE [dbo].[{blob_name}] ADD CONSTRAINT FK_{blob_name} FOREIGN KEY ({fk}) REFERENCES [dbo].[{fk_ref}] ({fk})'))
                trans.commit()
    
    def append_df_db(self, blob_name, blob_df):
        # Append data to blob table
        print(f"Appending {blob_name} to SQL database...")
        blob_df.to_sql(blob_name, eng, if_exists='append', index=False)

    
    def delete_db(self, table_name):
        # Delete table
        print(f"Deleting {table_name}...")
        with eng.connect() as con:
            trans = con.begin()
            con.execute(text(f"DROP TABLE [dbo].[{table_name}]"))
            trans.commit()


    def get_sql_table(self, query):
        # Execute SQL query
        df = pd.read_sql_query(query, eng)
        output = df.to_dict(orient='records')
        return output





 