"""
Generates realistic-looking fake transaction data (PHP-flavored merchants)
for the last 3 months, plus a handful of deliberately anomalous transactions
so the `detect_anomalies` MCP tool has something interesting to find.

Run via: python run_seed.py
"""
import random
from datetime import date, timedelta

from app.database import Base, engine, get_db_session
from app.models import Transaction

random.seed(42)  # reproducible demo data

MERCHANTS_BY_CATEGORY = {
    "Food & Dining": [
        ("Jollibee", 150, 450),
        ("Mang Inasal", 120, 300),
        ("Grab Food", 200, 700),
        ("7-Eleven", 50, 250),
        ("Local Karinderya", 60, 180),
        ("Starbucks", 150, 350),
    ],
    "Transportation": [
        ("Grab", 80, 400),
        ("Angkas", 60, 200),
        ("Jeepney/Tricycle Fare", 15, 60),
        ("Petron Gas Station", 500, 2000),
    ],
    "Bills & Utilities": [
        ("Meralco", 1500, 4500),
        ("Maynilad", 400, 1200),
        ("PLDT Home Fibr", 1500, 2500),
        ("Globe Postpaid", 999, 1999),
    ],
    "Shopping": [
        ("Shopee", 200, 3000),
        ("Lazada", 300, 2500),
        ("SM Department Store", 500, 4000),
        ("Uniqlo", 800, 3500),
    ],
    "Subscriptions": [
        ("Netflix", 549, 549),
        ("Spotify", 149, 149),
        ("YouTube Premium", 199, 199),
        ("iCloud Storage", 149, 149),
    ],
    "Groceries": [
        ("SM Supermarket", 800, 3500),
        ("Puregold", 500, 2500),
        ("Robinsons Supermarket", 700, 3000),
    ],
    "Health": [
        ("Mercury Drug", 150, 1200),
        ("Watsons", 200, 900),
        ("Clinic Consultation", 500, 1500),
    ],
    "Entertainment": [
        ("SM Cinema", 250, 600),
        ("KTV Session", 500, 1500),
        ("Steam", 300, 2000),
    ],
}

INCOME_SOURCES = [
    ("Salary Deposit", 25000, 45000),
    ("Freelance Payment", 3000, 15000),
]


def _random_date_within(days_back: int) -> date:
    return date.today() - timedelta(days=random.randint(0, days_back))


def generate_transactions(months_back: int = 3) -> list[Transaction]:
    days_back = months_back * 30
    transactions: list[Transaction] = []

    # Regular spending, ~4-6 transactions per category per month
    for category, merchants in MERCHANTS_BY_CATEGORY.items():
        count = random.randint(4, 6) * months_back
        for _ in range(count):
            merchant, low, high = random.choice(merchants)
            transactions.append(
                Transaction(
                    date=_random_date_within(days_back),
                    merchant=merchant,
                    category=category,
                    amount=round(random.uniform(low, high), 2),
                    description=f"{merchant} purchase",
                )
            )

    # Monthly income (negative amount = money in)
    for m in range(months_back):
        source, low, high = random.choice(INCOME_SOURCES)
        pay_date = date.today() - timedelta(days=30 * m + random.randint(0, 3))
        transactions.append(
            Transaction(
                date=pay_date,
                merchant=source,
                category="Income",
                amount=-round(random.uniform(low, high), 2),
                description=f"{source}",
            )
        )

    # A few deliberate anomalies for detect_anomalies() to catch
    anomalies = [
        ("Unknown Merchant XYZ123", "Shopping", 18500.00, "Unusually large one-off charge"),
        ("Overseas ATM Withdrawal", "Bills & Utilities", 12000.00, "Withdrawal from unfamiliar location"),
        ("Duplicate Netflix Charge", "Subscriptions", 549.00, "Charged twice in same week"),
    ]
    for merchant, category, amount, desc in anomalies:
        transactions.append(
            Transaction(
                date=_random_date_within(20),
                merchant=merchant,
                category=category,
                amount=amount,
                description=desc,
            )
        )

    return transactions


def seed():
    Base.metadata.create_all(bind=engine)
    db = get_db_session()
    try:
        existing = db.query(Transaction).count()
        if existing > 0:
            print(f"[CentWhisper] DB already has {existing} transactions. Skipping seed.")
            print("           Delete centwhisper.db if you want to regenerate fresh data.")
            return

        transactions = generate_transactions(months_back=3)
        db.add_all(transactions)
        db.commit()
        print(f"[CentWhisper] Seeded {len(transactions)} fake transactions into {engine.url}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
