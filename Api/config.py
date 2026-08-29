from dotenv import load_dotenv
from cryptography.fernet import Fernet
load_dotenv(encoding='utf-8-sig')
import os
MDKEY = os.getenv("MDKEY")
EKEY = Fernet(os.getenv("ENCRYPTKEY").encode())
UNAME = os.getenv("USERNAME")
PASS = os.getenv("PASSWORD")
MDID = os.getenv("MDID")

url = os.getenv("URL")
auth = os.getenv("AUTHURL")