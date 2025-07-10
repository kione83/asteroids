from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from cryptography.fernet import Fernet
from tkinter import filedialog, Tk, Text, Label, Entry, Button, StringVar, BooleanVar, Checkbutton, END, CENTER
from tkinter.scrolledtext import ScrolledText
import pandas as pd
import threading
import json
import os
import time
from datetime import datetime, timedelta

# === GUI SETUP ===
root = Tk()
root.title("User Account Automation")
root.geometry("800x640")

log_output = ScrolledText(root, wrap='word', height=15, width=95)
log_output.pack(pady=10)

username_label = Label(root, text="Username:")
username_label.pack()
username_entry = Entry(root, width=50, justify=CENTER)
username_entry.pack()

password_label = Label(root, text="Password:")
password_label.pack()
password_entry = Entry(root, width=50, show="*", justify=CENTER)
password_entry.pack()

course_code_label = Label(root, text="Course MMYY:")
course_code_label.pack()
course_code_entry = Entry(root, width=50, justify=CENTER)
course_code_entry.pack()

folder_path = StringVar()
output_file_path = StringVar()
create_account_csv = BooleanVar()
create_course_csv = BooleanVar()

def log(message):
    log_output.insert(END, message + '\n')
    log_output.see(END)

def setup_credentials():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    if not username or not password:
        log("❌ Please enter both username and password.")
        return
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    fernet = Fernet(key)
    config = {"username": username, "password": password}
    encrypted = fernet.encrypt(json.dumps(config).encode())
    with open("config.enc", "wb") as enc_file:
        enc_file.write(encrypted)
    log("🔐 Encrypted credentials file created.")

def select_folder():
    path = filedialog.askdirectory()
    folder_path.set(path)
    log(f"📁 Selected folder: {path}")

def select_output_file():
    path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    output_file_path.set(path)
    log(f"📄 Output file set to: {path}")

def run_automation():
    thread = threading.Thread(target=automation_logic)
    thread.start()

def automation_logic():
    try:
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
        fernet = Fernet(key)
        with open("config.enc", "rb") as enc_file:
            decrypted_data = fernet.decrypt(enc_file.read())
        config = json.loads(decrypted_data)
        USERNAME = config["username"]
        PASSWORD = config["password"]

        folder = folder_path.get()
        if not folder:
            log("❌ Please select a folder containing input files.")
            return

        df_list = []
        ticket_types = set()

        for filename in os.listdir(folder):
            if filename.startswith("report-2025") and filename.endswith(".xlsx"):
                file_path = os.path.join(folder, filename)
                log(f"📂 Reading file: {file_path}")
                try:
                    temp_df = pd.read_excel(file_path)
                    temp_df = temp_df[["First Name", "Last Name", "Email", "Ticket Type"]]
                    df_list.append(temp_df)
                    ticket_types.update(temp_df["Ticket Type"].dropna().unique())
                except Exception as e:
                    log(f"⚠️ Error reading {file_path}: {e}")

        if not df_list:
            log("❌ No matching files found.")
            return

        df = pd.concat(df_list, ignore_index=True)
        df["has account"] = ""

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get("https://vetsintech.co")
        time.sleep(2)

        try:
            accept_button = driver.find_element(By.XPATH, '//button[contains(text(), "I Accept")]')
            driver.execute_script("arguments[0].click();", accept_button)
            log("🍪 Accepted cookies.")
            time.sleep(1)
        except:
            log("No cookie popup found.")

        driver.find_element(By.CSS_SELECTOR, 'a[href="/login"]').click()
        time.sleep(2)
        driver.find_element(By.ID, "username").send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        login_button = driver.find_element(By.XPATH, '//button[normalize-space()="Log in"]')
        driver.execute_script("arguments[0].click();", login_button)
        time.sleep(3)

        driver.get("https://vetsintech.co/administrator")
        time.sleep(2)
        driver.find_element(By.XPATH, '//h1[normalize-space()="Home Dashboard"]')
        log("✅ Logged in and admin dashboard confirmed.")

        driver.get("https://vetsintech.co/administrator/index.php?option=com_users&view=users")
        time.sleep(2)

        for index, row in df.iterrows():
            if any(str(row[field]).strip().lower() == "info requested" for field in ["First Name", "Last Name", "Email"]):
                log(f"⚠️ Skipping row due to 'Info Requested': {row.to_dict()}")
                continue

            email = row["Email"]
            first_name = row["First Name"]
            last_name = row["Last Name"]
            username = email
            log(f"🔍 Checking: {email}")

            search_box = driver.find_element(By.ID, "filter_search")
            search_box.clear()
            search_box.send_keys(email)
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)

            if "no matching results" in driver.page_source.lower():
                df.at[index, "has account"] = "No"
                log("→ ❌ No account found.")

                driver.find_element(By.CLASS_NAME, "button-new").click()
                time.sleep(2)
                password = f"{username.capitalize()}!2025"

                driver.find_element(By.ID, "jform_name").send_keys(f"{first_name} {last_name}")
                driver.find_element(By.ID, "jform_username").send_keys(username)
                driver.find_element(By.ID, "jform_email").send_keys(email)
                driver.find_element(By.ID, "jform_password").send_keys(password)
                driver.find_element(By.ID, "jform_password2").send_keys(password)

                driver.find_element(By.CLASS_NAME, "button-apply").click()
                time.sleep(2)

                user_groups_tab = driver.find_element(By.XPATH, '//button[@aria-controls="groups"]')
                driver.execute_script("arguments[0].click();", user_groups_tab)
                time.sleep(1)

                allowed = {"Registered", "Veteran", "ID.ME Verified"}
                labels = driver.find_elements(By.CSS_SELECTOR, 'label.form-check-label')
                for label in labels:
                    text = label.text.strip().replace("\u00a0", " ").lower()
                    checkbox = label.find_element(By.TAG_NAME, "input")
                    for group in allowed:
                        if group.lower() in text and not checkbox.is_selected():
                            checkbox.click()
                            log(f"✔️ Checked: {group}")
                            break

                driver.find_element(By.XPATH, '//button[normalize-space()="Save & Close"]').click()
                time.sleep(2)
                log(f"✅ User created and saved: {email} | Password: {password}")
            else:
                df.at[index, "has account"] = "Yes"
                log("→ ✅ Account found.")

        output_path = output_file_path.get() or "test_run_v2_results.xlsx"
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="All Users", index=False)
            summary_df = df[df["has account"] == "No"]["First Name"].to_frame()
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

        if create_account_csv.get():
            csv_path = os.path.join(folder, "account_creation.csv")
            df_out = df.copy()
            df_out["user_id"] = df_out["Email"]
            df_out["login_id"] = df_out["Email"]
            df_out["status"] = "active"
            df_out = df_out[["user_id", "login_id", "First Name", "Last Name", "Email", "status"]]
            df_out.columns = ["user_id", "login_id", "first_name", "last_name", "email", "status"]
            df_out.to_csv(csv_path, index=False)
            log(f"📄 Account creation CSV saved to: {csv_path}")

        if create_course_csv.get():
            course_prefix = course_code_entry.get().strip()
            if not course_prefix:
                log("❌ Course MMYY code is required for course CSV.")
                return
            for ticket_type in ticket_types:
                course_id = f"{course_prefix}{ticket_type}"
                course_path = os.path.join(folder, f"course_enrollments_{course_id}.csv")
                course_df = df.copy()
                course_df["course_id"] = course_id
                course_df["user_id"] = course_df["Email"]
                course_df["role"] = "student"
                course_df["status"] = "active"
                course_df["notify"] = True
                course_df = course_df[["course_id", "user_id", "role", "status", "notify"]]
                course_df.to_csv(course_path, index=False)
                log(f"📄 Course enrollment CSV saved to: {course_path}")

        driver.quit()
        log("🎉 Done! Process completed.")

    except Exception as e:
        log(f"❌ Error: {e}")

# === BUTTONS ===
Button(root, text="Setup Credentials", command=setup_credentials).pack(pady=2)
Button(root, text="Select Folder to Read Files", command=select_folder).pack(pady=2)
Button(root, text="Choose Output File (Optional)", command=select_output_file).pack(pady=2)
Checkbutton(root, text="Generate Canvas Account Creation CSV", variable=create_account_csv).pack(pady=2)
Checkbutton(root, text="Generate Canvas Course Enrollment CSV", variable=create_course_csv).pack(pady=2)
Button(root, text="Go", command=run_automation).pack(pady=10)

root.mainloop()