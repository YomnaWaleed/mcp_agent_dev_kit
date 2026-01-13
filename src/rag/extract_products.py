# src/rag/extract_products.py
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../mcp/db/banking.db")


def extract_products_from_db():
    """Extract unique product information from banking database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # First, check what columns exist
    cursor.execute("PRAGMA table_info(customers)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Available columns: {columns}")

    products = []

    # Extract Account Types (this works - you have account_type)
    cursor.execute(
        """
        SELECT DISTINCT account_type 
        FROM customers 
        WHERE account_type IS NOT NULL
    """
    )
    for row in cursor.fetchall():
        products.append(
            {
                "id": f"account_{row[0].lower()}",
                "name": f"{row[0]} Account",
                "type": "account",
                "description": f"Banking {row[0].lower()} account for everyday transactions and savings.",
                "features": [
                    "Online banking",
                    "Mobile app",
                    "ATM access",
                    "Direct deposit",
                ],
            }
        )

    # Since loan/card data isn't in separate columns, create generic products
    # Based on common banking products

    # Loan products (generic - since data isn't in customer table)
    loan_types = [
        {
            "id": "loan_mortgage",
            "name": "Mortgage Loan",
            "type": "loan",
            "description": "Home mortgage loans with competitive rates for purchasing or refinancing property.",
            "typical_rate": "3-7%",
            "typical_term": "15-30 years",
            "features": [
                "Fixed and variable rates",
                "No prepayment penalty",
                "Online management",
            ],
        },
        {
            "id": "loan_auto",
            "name": "Auto Loan",
            "type": "loan",
            "description": "Financing for new and used vehicles with flexible terms.",
            "typical_rate": "4-8%",
            "typical_term": "24-72 months",
            "features": [
                "Quick approval",
                "Competitive rates",
                "Flexible payment terms",
            ],
        },
        {
            "id": "loan_personal",
            "name": "Personal Loan",
            "type": "loan",
            "description": "Unsecured personal loans for various purposes with fixed monthly payments.",
            "typical_rate": "6-12%",
            "typical_term": "12-60 months",
            "features": ["No collateral required", "Fixed rates", "Same-day decision"],
        },
    ]
    products.extend(loan_types)

    # Credit card products (generic)
    card_types = [
        {
            "id": "card_visa",
            "name": "Visa Credit Card",
            "type": "credit_card",
            "description": "Standard Visa credit card with worldwide acceptance and rewards.",
            "features": [
                "Fraud protection",
                "Rewards program",
                "No annual fee",
                "Travel benefits",
            ],
        },
        {
            "id": "card_mastercard",
            "name": "MasterCard Credit Card",
            "type": "credit_card",
            "description": "MasterCard with cashback rewards and purchase protection.",
            "features": [
                "Cashback on purchases",
                "Purchase protection",
                "Extended warranty",
                "Travel insurance",
            ],
        },
        {
            "id": "card_amex",
            "name": "American Express Card",
            "type": "credit_card",
            "description": "Premium American Express card with exclusive benefits and higher credit limits.",
            "features": [
                "Premium rewards",
                "Airport lounge access",
                "Concierge service",
                "Travel credits",
            ],
        },
    ]
    products.extend(card_types)

    conn.close()

    # Save to JSON
    output = {"products": products}
    os.makedirs("src/rag/products", exist_ok=True)
    with open("src/rag/products/products.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Extracted {len(products)} products")
    print(f"   Account types: {len([p for p in products if p['type'] == 'account'])}")
    print(f"   Loan types: {len([p for p in products if p['type'] == 'loan'])}")
    print(f"   Card types: {len([p for p in products if p['type'] == 'credit_card'])}")
    print(f"\n📁 Saved to: src/rag/products/products.json")

    return products


if __name__ == "__main__":
    extract_products_from_db()
