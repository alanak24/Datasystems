import os, uuid, pydoc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from data_setup import AzureDB, eng
from entities import *

load_dotenv()

# Load all .env variables
account_storage = os.environ.get('ACCOUNT_STORAGE')
username = os.environ.get('USERNAME_AZURE')
password = os.environ.get('PASSWORD')
server = os.environ.get('SERVER')
database = os.environ.get('DATABASE')
connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')


# Create FastAPI
app = FastAPI()

# Access Azure Database
db = AzureDB()
db.access_container("test-merge")


# Authentication Models
class Admin(BaseModel):
    admin_id: int
    admin_name: str

class Token(BaseModel):
    access_token: str
    access_type: str

@app.get("/")
def root():
    return "OPTIMate Laptop Recommendation API"





