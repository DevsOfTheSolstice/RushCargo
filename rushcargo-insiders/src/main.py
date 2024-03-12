from dotenv import load_dotenv
from pathlib import Path
import os
import sys

from lib.model.database import *
from lib.model.classes import *
from lib.model.constants import *
from lib.model.exceptions import *
from lib.io.validator import *

# Get Path to 'src' Directory
src = Path(__file__).parent
print(sys.path)

# Get Path to 'rushcargo-insiders' Directory
main = src.parent

# Get Path to the .env File for Local Environment Variables
dotenvPath =  main /"venv/.env"
# print(dotenvPath)

def main():
  # Load .env File
  load_dotenv(dotenvPath)

  # Get Database-related Environment Variables
  host = os.getenv('HOST')
  port = os.getenv('PORT')
  dbname = os.getenv('DBNAME')
  user = os.getenv('USER')
  password = os.getenv('PASSWORD')

  # Initialize Database Object
  db = Database(dbname, user, password, host, port)
  
  # Initialize Country Object
  country = CountryTable(db)
  #country.insert(Country("United States", 1))
  country.getAll(COUNTRY_PHONE_PREFIX)


if __name__ == "__main__":
  main()