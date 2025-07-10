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

# === CONFIGURATION ===
FOLDER_PATH = "checking users"
FILE_PREFIX = "report-2025"
df_list = []

for filename in os.listdir(FOLDER_PATH):
    if filename.startswith(FILE_PREFIX) and filename.endswith(".xlsx"):
        file_path = os.path.join(FOLDER_PATH, filename)
        temp_df = pd.read_excel(file_path)  # loads first/only sheet
        temp_df = temp_df[["First Name", "Last Name", "Email"]]
        df_list.append(temp_df)

df = pd.concat(df_list, ignore_index=True)
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
    # Step 5: Select only the correct user groups
    allowed_groups = {"Registered", "Veteran", "ID.ME Verified"}

    labels = driver.find_elements(By.CSS_SELECTOR, 'label.form-check-label')

    for label in labels:
        label_text = label.text.strip().replace("\u00a0", " ")  # Clean up nbsp
        for group in allowed_groups:
            if group in label_text:
                checkbox = label.find_element(By.TAG_NAME, "input")
                if not checkbox.is_selected():
                    checkbox.click()
                    print(f"✔️ Checked: {group}")
                break
        else:
            # Not in allowed list; uncheck if selected
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

# Step 3: Click login button (use JS to avoid overlay issues)
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
for sheet in SHEETS:
    temp_df = pd.read_excel(SPREADSHEET, sheet_name=sheet)
    temp_df = temp_df[["First Name", "Last Name", "Email"]]
    df_list.append(temp_df)

df = pd.concat(df_list, ignore_index=True)
df["has account"] = ""

# === LOOP THROUGH EMAILS AND SEARCH ===
for index, row in df.iterrows():
    email = row["Email"]
    first_name = row["First Name"]
    last_name = row["Last Name"]
    username = email
    print(f"🔍 Checking: {email}")

    # Clear search box and enter email
    search_box = driver.find_element(By.ID, "filter_search")
    search_box.clear()
    search_box.send_keys(email)
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)

    # Check if result exists
    if "no matching results" in driver.page_source.lower():
        df.at[index, "has account"] = "No"
        print("→ ❌ No account found.")
        create_user(driver,first_name, last_name, username, email)
    else:
        df.at[index, "has account"] = "Yes"
        print("→ ✅ Account found.")

# === SAVE RESULTS TO MULTI-SHEET EXCEL FILE ===
with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    start = 0
    for i, sheet_name in enumerate(SHEETS):
        temp_df = df.iloc[start : start + len(df_list[i])]
        temp_df.to_excel(writer, sheet_name=sheet_name, index=False)
        start += len(df_list[i])

    summary_df = df[df["has account"] == "No"][["First Name", "Last Name", "Email", "has account"]]
    summary_df.to_excel(writer, sheet_name="Summary", index=False)

print(f"🎉 Done! Results saved to: {OUTPUT_FILE}")

# === CLOSE BROWSER ===
driver.quit()