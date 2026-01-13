# src/mcp/create_db.py
import os
import sqlite3
import pandas as pd

# Create directories
os.makedirs("src/mcp/db", exist_ok=True)

db_path = "src/mcp/db/banking.db"
csv_path = "data/Comprehensive_Banking_Database.csv"

if not os.path.exists(csv_path):
    print(f"❌ Error: CSV file not found at {csv_path}")
    print("Please ensure the CSV file exists in the data folder.")
    exit(1)

print(f"Loading data from {csv_path}...")
df = pd.read_csv(csv_path)

print(f"Loaded {len(df)} rows")
print(f"Columns: {df.columns.tolist()}")

# Create database
print(f"Creating database at {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create customers table
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    age INTEGER,
    gender TEXT,
    address TEXT,
    city TEXT,
    contact_number TEXT,
    email TEXT,
    account_type TEXT,
    account_balance REAL,
    date_of_account_opening TEXT
)
"""
)

# Create transactions table
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    transaction_date TEXT,
    transaction_type TEXT,
    transaction_amount REAL,
    account_balance_after REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
"""
)

# Extract unique customers
customers_df = df[
    [
        "Customer ID",
        "First Name",
        "Last Name",
        "Age",
        "Gender",
        "Address",
        "City",
        "Contact Number",
        "Email",
        "Account Type",
        "Account Balance",
        "Date Of Account Opening",
    ]
].drop_duplicates(subset=["Customer ID"])

customers_df.columns = [
    "customer_id",
    "first_name",
    "last_name",
    "age",
    "gender",
    "address",
    "city",
    "contact_number",
    "email",
    "account_type",
    "account_balance",
    "date_of_account_opening",
]

# Insert customers
customers_df.to_sql("customers", conn, if_exists="replace", index=False)

# Extract transactions
transactions_df = df[
    [
        "TransactionID",
        "Customer ID",
        "Transaction Date",
        "Transaction Type",
        "Transaction Amount",
        "Account Balance After Transaction",
    ]
]

transactions_df.columns = [
    "transaction_id",
    "customer_id",
    "transaction_date",
    "transaction_type",
    "transaction_amount",
    "account_balance_after",
]

# Insert transactions
transactions_df.to_sql("transactions", conn, if_exists="replace", index=False)

# Create indexes
cursor.execute(
    """
CREATE INDEX IF NOT EXISTS idx_customer_id 
ON transactions(customer_id)
"""
)

cursor.execute(
    """
CREATE INDEX IF NOT EXISTS idx_transaction_date 
ON transactions(transaction_date DESC)
"""
)

conn.commit()

# Verify data
cursor.execute("SELECT COUNT(*) FROM customers")
customers_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM transactions")
transactions_count = cursor.fetchone()[0]

cursor.execute("SELECT customer_id, first_name, last_name FROM customers LIMIT 5")
sample_customers = cursor.fetchall()

conn.close()

print(f"\n✅ Database created successfully!")
print(f"   Total customers: {customers_count}")
print(f"   Total transactions: {transactions_count}")
print(f"   Location: {db_path}")
print(f"\nSample customers:")
for cust in sample_customers:
    print(f"   - ID: {cust[0]}, Name: {cust[1]} {cust[2]}")
