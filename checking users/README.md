# 🧠 ViT Account Automation Desktop App

This desktop app automates the process of checking for existing user accounts and creating new ones on the VetsInTech platform using a simple, intuitive interface.

---

## ✅ Features

- 🔐 **Encrypted Login**: Securely stores your username and password in encrypted form.
- 📁 **Folder Picker**: Easily select the folder that contains user Excel files (`report-2025*.xlsx`).
- 📤 **Output File Selector**: Choose where to save the results or append to an existing Excel file.
- 🧮 **Account Checking**: Automatically checks if users already have an account on the site.
- 🆕 **Account Creation**: Creates accounts for users who don't have one, assigning default user groups.
- 📦 **Summary Sheet**: Saves all results to an Excel file with a summary tab.
- 👁️ **Preview Results**: Instantly view the output Excel file within the app.
- 🖥️ **Desktop GUI**: Clean, responsive Tkinter interface — no coding required.

---

## 🚀 Getting Started

### 1. Install Requirements

Make sure Python 3.10+ is installed. Then run:

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:

```
selenium
pandas
openpyxl
cryptography
webdriver-manager
```

---

### 2. Generate Your Secret Key and Encrypted Config

From the app, click the **Setup Credentials** button and enter your login credentials. These are securely encrypted using your unique key.

This creates:

- `secret.key` — the encryption key
- `config.enc` — your encrypted credentials

---

### 3. Prepare Input Files

Create a folder containing Excel files named like:

```
report-2025-something.xlsx
```

Each file should contain at least the following headers:

- `First Name`
- `Last Name`
- `Email`

The app will ignore any rows where any of these fields contain `"Info Requested"`.

---

### 4. Run the App

Launch the app (`main.exe` on Windows or `main` on macOS/Linux).

- Select the folder with your input files
- Choose or create an output `.xlsx` file
- Click **Start Automation** to begin

You'll see live status updates in the console area.

---

### 5. Preview Results

After completion, click **Preview Excel File** to see the contents of the output file right in the app.

---

## 🛠 Packaging as a Desktop App

To turn this into a standalone app (no Python required):

```bash
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

- `--onefile`: bundle everything into a single file
- `--windowed`: suppress terminal window
- `--icon=icon.ico`: adds your custom icon

You’ll find the executable in the `/dist` folder.

---

## 🔐 Security Notes

- The app never stores or transmits credentials in plain text.
- Credentials are encrypted using Fernet (symmetric encryption).
- Each user generates their own unique `secret.key`.

---

## 📄 Output Excel File

The output Excel file includes:

### `All Users` tab

| First Name | Last Name | Email | has account |
| ---------- | --------- | ----- | ----------- |

### `Summary` tab

Only users without an account.

---

## 📬 Contact

For questions or support, contact: `smarlow@vetsintech.co`
