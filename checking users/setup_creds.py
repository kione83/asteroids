import tkinter as tk
from tkinter import simpledialog, messagebox
from cryptography.fernet import Fernet
import json
import os


def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    return key


def load_key():
    if not os.path.exists("secret.key"):
        return generate_key()
    with open("secret.key", "rb") as key_file:
        return key_file.read()


def setup_credentials():
    username = simpledialog.askstring("Input", "Enter your username:")
    password = simpledialog.askstring("Input", "Enter your password:", show='*')

    if not username or not password:
        messagebox.showwarning("Missing Info", "Both fields are required.")
        return

    creds = json.dumps({"username": username, "password": password}).encode()
    key = load_key()
    encrypted = Fernet(key).encrypt(creds)

    with open("config.enc", "wb") as config_file:
        config_file.write(encrypted)

    messagebox.showinfo("Success", "Credentials saved and encrypted.")


# === GUI ===
root = tk.Tk()
root.title("User Setup")
root.geometry("300x150")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(expand=True)

setup_button = tk.Button(frame, text="Setup Credentials", command=setup_credentials)
setup_button.pack(pady=10)

root.mainloop()