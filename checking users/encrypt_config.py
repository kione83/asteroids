from cryptography.fernet import Fernet
import json

# Step 1: Generate and save encryption key
key = Fernet.generate_key()
with open("secret.key", "wb") as key_file:
    key_file.write(key)
print("🔑 secret.key generated.")

# Step 2: Define your credentials here
data = {
    "username": "",
    "password": ""
}

# Step 3: Encrypt the credentials
fernet = Fernet(key)
encrypted = fernet.encrypt(json.dumps(data).encode())

with open("config.enc", "wb") as enc_file:
    enc_file.write(encrypted)

print("🔒 Encrypted config saved to config.enc")