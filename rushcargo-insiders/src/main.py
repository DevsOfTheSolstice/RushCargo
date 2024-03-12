from dotenv import load_dotenv
from pathlib import Path
import os

from lib.model.constants import *
from lib.model.exceptions import *
from lib.model.database import *

# Get Path to 'src' Directory
src = Path(__file__).parent

# Get Path to 'rushcargo-insiders' Directory
main = src.parent

# Get Path to the .env File for Local Environment Variables
dotenv_path =  main /"venv/.env"
# print(dotenv_path)

def main():
  # Load .env File
  load_dotenv(dotenv_path)

  # Get Database-related Environment Variables
  host = os.getenv('HOST')
  port = os.getenv('PORT')
  dbname = os.getenv('DBNAME')
  user = os.getenv('USER')
  password = os.getenv('PASSWORD')

  # Initialize Database Object
  db = Database(dbname, user, password, host, port)
  
  # Initialize Country Object
  country = Country(db)
  # country.insert("Colombia", 57)
  # country.printAll()


if __name__ == "__main__":
  main()