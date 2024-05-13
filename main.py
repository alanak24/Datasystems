import os, uuid
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
from master.data_setup import *
# from master.dim_setup import *

load_dotenv()

account_storage = os.environ.get('ACCOUNT_STORAGE')


def main():
    # Create Azure DB object
    azureDB = AzureDB()

    # Access csv-files container
    azureDB.access_container("csv-files")

    # List blobs
    azureDB.list_blobs()

    # Access specific blob
    df = azureDB.access_blob_csv("user_data.csv")
    print(df.head())


if __name__ == "__main__":
    main()