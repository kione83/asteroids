from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

# === CONFIG ===
USERNAME = "smarlow"
PASSWORD = "!mpt76jsAAMC6fw"

# === LAUNCH BROWSER ===
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

# Step 1: Click the login link
login_link = driver.find_element(By.CSS_SELECTOR, 'a[href="/login"]')
login_link.click()
time.sleep(2)

# Step 2: Enter login credentials
driver.find_element(By.ID, "username").send_keys(USERNAME)
driver.find_element(By.ID, "password").send_keys(PASSWORD)

# Step 3: Click the login button (use JS to avoid click interception)
login_button = driver.find_element(By.XPATH, '//button[normalize-space()="Log in"]')
driver.execute_script("arguments[0].click();", login_button)
time.sleep(3)

# Step 4: Go to admin panel
driver.get("https://vetsintech.co/administrator")
time.sleep(2)

# Step 5: Confirm dashboard loaded
try:
    header = driver.find_element(By.XPATH, '//h1[normalize-space()="Home Dashboard"]')
    print("✅ Login successful and admin dashboard loaded.")
except:
    print("❌ Login failed or dashboard not found.")

# Close browser
driver.quit()