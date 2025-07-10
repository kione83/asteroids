import pandas as pd

# Simulated spreadsheet content (normally from Excel)
data = {
    "First Name": ["Alice", "Bob", "Charlie"],
    "Last Name": ["Smith", "Jones", "Brown"],
    "Email": ["alice@example.com", "bob@example.com", "charlie@example.com"]
}

df = pd.DataFrame(data)
df["has account"] = ""

# Simulate checking if accounts exist (hardcoded rule)
# For test purposes, let's say Bob has no account
for index, row in df.iterrows():
    email = row["Email"]
    if email == "bob@example.com":
        df.at[index, "has account"] = "No"
    else:
        df.at[index, "has account"] = "Yes"

# Show output
print(df[["Email", "has account"]])

# Optional: Save to Excel
df.to_excel("test_output.xlsx", index=False)