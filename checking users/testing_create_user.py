from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# === CONFIG ===
USERNAME = "smarlow"
PASSWORD = "!mpt76jsAAMC6fw"

# === START BROWSER AND LOGIN ===
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://vetsintech.co")
time.sleep(2)

# Accept cookies if needed
try:
    accept_button = driver.find_element(By.XPATH, '//button[contains(text(), "I Accept")]')
    driver.execute_script("arguments[0].click();", accept_button)
    print("🍪 Accepted cookies.")
    time.sleep(1)
except:
    print("No cookie popup found.")

# Login
driver.find_element(By.CSS_SELECTOR, 'a[href="/login"]').click()
time.sleep(2)
driver.find_element(By.ID, "username").send_keys(USERNAME)
driver.find_element(By.ID, "password").send_keys(PASSWORD)
login_button = driver.find_element(By.XPATH, '//button[normalize-space()="Log in"]')
driver.execute_script("arguments[0].click();", login_button)
time.sleep(3)

# Go to admin panel
driver.get("https://vetsintech.co/administrator")
time.sleep(2)

# Confirm dashboard loaded
driver.find_element(By.XPATH, '//h1[normalize-space()="Home Dashboard"]')
print("✅ Logged in and dashboard verified.")

# Go to Users section
driver.get("https://vetsintech.co/administrator/index.php?option=com_users&view=users")
time.sleep(2)

# === CREATE USER FUNCTION ===
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

# === TEST CASE: JOE DIRT ===
create_user(driver,
            first_name="Joe",
            last_name="Dirt",
            username="jaydizzle",
            email="fake_user_test@gimmesome.com")

# Done
driver.quit()