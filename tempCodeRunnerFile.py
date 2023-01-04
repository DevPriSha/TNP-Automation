import os
from cryptography.fernet import Fernet

key = os.getenv("FERNET_KEY")
f = Fernet(key)

print(key)