from dotenv import load_dotenv
from cryptography.fernet import Fernet
load_dotenv()
import os
MDKEY = os.getenv("MDKEY")
EKEY = Fernet(os.getenv("Encryptkey"))
UNAME = os.getenv("USERNAME")
PASS = os.getenv("PASSWORD")
CLI_ID = os.getenv("CLIID")