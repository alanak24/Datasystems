import os, io, uuid, pyodbc
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

# Load all .env variables
account_storage = os.environ.get('ACCOUNT_STORAGE')
username = os.environ.get('USERNAME_AZURE')
password = os.environ.get('PASSWORD')
server = os.environ.get('SERVER')
connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')

sql_engine = create_engine('sqlite:///LaptopRecommendation.db', echo=False)

class AzureDB():
    def __init__(self, local_path="./data", account_storage=account_storage):
        self.local_path = local_path
        self.account_url = f"https://{account_storage}.blob.core.windows.net"
        self.default_credential = DefaultAzureCredential()
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = None

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
    
    def delete_container(self):
        # Delete container
        print("Deleting container")
        self.container_client.delete_container()
        print("Delete complete")
    
    def upload_blob(self, blob_name, blob_data=None):
        # Upload container
        local_file_name = blob_name
        upload_file_path = os.path.join(self.local_path, local_file_name)
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=local_file_name)
        print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

        with open(file=upload_file_path, mode="rb") as data:
            blob_client.upload_blob(data)

    def list_blobs(self):
        # List blobs
        print("\nBlob List: ")
        blob_list = self.container_client.list_blobs()
        for blob in blob_list:
            print("\t" + blob.name)

    def download_blob(self, blob_name):
        # Download blob to local storage
        download_file_path = os.path.join(self.local_path, blob_name)
        print("\nDownloading blob to \n\t" + download_file_path)
        with open(file=download_file_path, mode="wb") as download_file:
            download_file.write(self.container_client.download_blob(blob_name).readall())
    
    def delete_blob(self, container_name: str, blob_name: str):
        # Deleting a blob
        print("\nDeleting blob " + blob_name)
    
    
    def access_blob_csv(self, blob_name):
        # Access blob csv
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
        blob_df.to_sql(blob_name, sql_engine, if_exists='replace', index=False)
    
    def append_df_db(self, blob_name, blob_df):
        # Append data to blob table
        print(f"Appending {blob_name} to SQL database...")
        blob_df.to_sql(blob_name, sql_engine, if_exists='append', index=False)



 