from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from selenium.webdriver.common.keys import Keys
import json
import os
from cryptography.fernet import Fernet
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tkinter as tk
from tkinter import filedialog, messagebox 


root = tk.Tk()
root.title("User Account Automation")
root.geometry("500x300") 

# === DECRYPT CONFIGURATION ===
base_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base_dir, "secret.key"), "rb") as key_file:
    key = key_file.read()

fernet = Fernet(key)

with open(os.path.join(base_dir, "config.enc"), "rb") as enc_file:
    decrypted_data = fernet.decrypt(enc_file.read())

config = json.loads(decrypted_data)
USERNAME = config["username"]
PASSWORD = config["password"]

selected_folder = None  # Global variable or part of a class if using OOP

def select_folder():
    global selected_folder
    folder_path = filedialog.askdirectory()
    if folder_path:
        selected_folder = folder_path
        folder_label.config(text=f"📂 Selected: {folder_path}")
    else:
        messagebox.showinfo("Info", "No folder selected.")

# Button in your GUI:
folder_label = tk.Label(root, text="No folder selected", wraplength=400)
folder_label.pack(pady=5)

select_button = tk.Button(root, text="Select Folder", command=select_folder)
select_button.pack(pady=5)


# === CONFIGURATION ===
# FOLDER_PATH = "checking users"
if not selected_folder:
    raise Exception("No folder selected. Please choose a folder before running.")
FOLDER_PATH = selected_folder
FILE_PREFIX = "report-2025"
df_list = []

for filename in os.listdir(FOLDER_PATH):
    if filename.startswith(FILE_PREFIX) and filename.endswith(".xlsx"):
        file_path = os.path.join(FOLDER_PATH, filename)
        temp_df = pd.read_excel(file_path)  # loads first/only sheet
        temp_df = temp_df[["First Name", "Last Name", "Email"]]
        df_list.append(temp_df)

df = pd.concat(df_list, ignore_index=True)

# Remove rows with "Info Requested" in any critical field
df = df[~df[["First Name", "Last Name", "Email"]].isin(["Info Requested"]).any(axis=1)].reset_index(drop=True)

df["has account"] = ""

OUTPUT_FILE = "test_run_v2_results.xlsx"

def create_user(driver, first_name, last_name, username, email):
    print(f"➕ Creating user: {email}")

    # Click "New"
    new_button = driver.find_element(By.CLASS_NAME, "button-new")
    driver.execute_script("arguments[0].click();", new_button)
    time.sleep(2)

    # Create password dynamically
    password = f"{username.capitalize()}!2025"

    # Fill form
    driver.find_element(By.ID, "jform_name").send_keys(f"{first_name} {last_name}")
    driver.find_element(By.ID, "jform_username").send_keys(username)
    driver.find_element(By.ID, "jform_email").send_keys(email)
    driver.find_element(By.ID, "jform_password").send_keys(password)
    driver.find_element(By.ID, "jform_password2").send_keys(password)

    # Click Apply
    save_button = driver.find_element(By.CLASS_NAME, "button-apply")
    driver.execute_script("arguments[0].click();", save_button)
    time.sleep(2)

    # Assigned User Groups tab
    user_groups_tab = driver.find_element(By.XPATH, '//button[@aria-controls="groups"]')
    driver.execute_script("arguments[0].click();", user_groups_tab)
    time.sleep(1)

    # Check the correct groups
    allowed_groups = {"Registered", "Veteran", "ID.ME Verified"}
    labels = driver.find_elements(By.CSS_SELECTOR, 'label.form-check-label')

    for label in labels:
        label_text = label.text.strip().replace("\u00a0", " ")
        for group in allowed_groups:
            if group in label_text:
                checkbox = label.find_element(By.TAG_NAME, "input")
                if not checkbox.is_selected():
                    checkbox.click()
                    print(f"✔️ Checked: {group}")
                break
        else:
            checkbox = label.find_element(By.TAG_NAME, "input")
            if checkbox.is_selected():
                checkbox.click()
                print(f"❌ Unchecked: {label_text}")

    # Save & Close
    save_close_button = driver.find_element(By.XPATH, '//button[normalize-space()="Save & Close"]')
    driver.execute_script("arguments[0].click();", save_close_button)
    time.sleep(2)

    print(f"✅ User created and saved: {email} | Password: {password}")


# === SETUP SELENIUM ===
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://vetsintech.co")
time.sleep(2)

# Step 0: Accept cookies if present
try:
    accept_button = driver.find_element(By.XPATH, '//button[contains(text(), "I Accept")]')
    driver.execute_script("arguments[0].click();", accept_button)
    print("🍪 Accepted cookies.")
    time.sleep(1)
except:
    print("No cookie popup found.")

# Step 1: Click login link
driver.find_element(By.CSS_SELECTOR, 'a[href="/login"]').click()
time.sleep(2)

# Step 2: Enter login credentials
driver.find_element(By.ID, "username").send_keys(USERNAME)
driver.find_element(By.ID, "password").send_keys(PASSWORD)

# Step 3: Click login button
login_button = driver.find_element(By.XPATH, '//button[normalize-space()="Log in"]')
driver.execute_script("arguments[0].click();", login_button)
time.sleep(3)

# Step 4: Go to admin dashboard
driver.get("https://vetsintech.co/administrator")
time.sleep(2)

# Step 5: Confirm dashboard loaded
try:
    driver.find_element(By.XPATH, '//h1[normalize-space()="Home Dashboard"]')
    print("✅ Logged in and admin dashboard confirmed.")
except:
    print("❌ Login may have failed or dashboard header not found.")
    driver.quit()
    exit()

# Step 6: Go to Users section
driver.get("https://vetsintech.co/administrator/index.php?option=com_users&view=users")
time.sleep(2)

# === LOAD SPREADSHEET DATA ===
df_list = []
FOLDER_PATH = "checking users"
FILE_PREFIX = "report-2025"

for filename in os.listdir(FOLDER_PATH):
    if filename.startswith(FILE_PREFIX) and filename.endswith(".xlsx"):
        file_path = os.path.join(FOLDER_PATH, filename)
        print(f"📂 Reading file: {file_path}")
        try:
            temp_df = pd.read_excel(file_path)
            temp_df = temp_df[["First Name", "Last Name", "Email"]]
            df_list.append(temp_df)
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")

if df_list:
    df = pd.concat(df_list, ignore_index=True)

    for i, row in df.iterrows():
        if any(str(row[col]).strip().lower() == "info requested" for col in ["First Name", "Last Name", "Email"]):
            print(f"⚠️ Skipping row {i + 2}: Found 'Info Requested' in {row.to_dict()}")

    mask = df[["First Name", "Last Name", "Email"]].apply(
        lambda col: col.str.strip().str.lower() != "info requested"
    ).all(axis=1)

    df = df[mask].reset_index(drop=True)
    df["has account"] = ""
else:
    print("❌ No matching files found.")
    exit()


# === LOOP THROUGH EMAILS AND SEARCH ===
for index, row in df.iterrows():
    email = row["Email"]
    first_name = row["First Name"]
    last_name = row["Last Name"]
    username = email
    print(f"🔍 Checking: {email}")

    wait = WebDriverWait(driver, 10)
    search_box = wait.until(EC.presence_of_element_located((By.ID, "filter_search")))
    search_box.clear()
    search_box.send_keys(email)
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)

    if "no matching results" in driver.page_source.lower():
        df.at[index, "has account"] = "No"
        print("→ ❌ No account found.")
        create_user(driver, first_name, last_name, username, email)
    else:
        df.at[index, "has account"] = "Yes"
        print("→ ✅ Account found.")

# === SAVE RESULTS TO MULTI-SHEET EXCEL FILE ===
with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="All Users", index=False)
    summary_df = df[df["has account"] == "No"][["First Name", "Last Name", "Email", "has account"]]
    summary_df.to_excel(writer, sheet_name="Summary", index=False)

print(f"🎉 Done! Results saved to: {OUTPUT_FILE}")

driver.quit()