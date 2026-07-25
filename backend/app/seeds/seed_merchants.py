"""Seed script: populates the database with sample verified merchants and services.

Run from the project root:
    cd backend
    python -m backend.app.seeds.seed_merchants
"""
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models.merchant import Merchant
from backend.app.models.service import Service


SEED_DATA = [
    {
        "business_name": "Chipiku Plus",
        "category": "Groceries",
        "location": "Lilongwe",
        "verified": True,
        "services": [
            {"name": "Grocery Package", "amount": 50000},
            {"name": "Essential Food Basket", "amount": 30000},
        ],
    },
    {
        "business_name": "Peoples Supermarket",
        "category": "Groceries",
        "location": "Blantyre",
        "verified": True,
        "services": [
            {"name": "Weekly Grocery Bundle", "amount": 45000},
            {"name": "Monthly Staples Pack", "amount": 120000},
        ],
    },
    {
        "business_name": "Kamuzu Central Hospital Pharmacy",
        "category": "Healthcare",
        "location": "Lilongwe",
        "verified": True,
        "services": [
            {"name": "Prescription Fill", "amount": 15000},
            {"name": "Medical Consultation", "amount": 25000},
        ],
    },
    {
        "business_name": "ESCOM Utilities",
        "category": "Utilities",
        "location": "Nationwide",
        "verified": True,
        "services": [
            {"name": "Electricity Token 5,000 MWK", "amount": 5000},
            {"name": "Electricity Token 10,000 MWK", "amount": 10000},
            {"name": "Electricity Token 20,000 MWK", "amount": 20000},
        ],
    },
]


def seed():
    app = create_app("development")
    with app.app_context():
        for merchant_data in SEED_DATA:
            existing = db.session.execute(
                db.select(Merchant).filter_by(business_name=merchant_data["business_name"])
            ).scalar_one_or_none()

            if existing:
                print(f"  Skipped (already exists): {merchant_data['business_name']}")
                continue

            merchant = Merchant(
                business_name=merchant_data["business_name"],
                category=merchant_data["category"],
                location=merchant_data["location"],
                verified=merchant_data["verified"],
            )
            db.session.add(merchant)
            db.session.flush()  # Get merchant.id before adding services

            for svc in merchant_data["services"]:
                service = Service(
                    merchant_id=merchant.id,
                    name=svc["name"],
                    amount=svc["amount"],
                )
                db.session.add(service)

            print(f"  Seeded: {merchant_data['business_name']} ({len(merchant_data['services'])} services)")

        db.session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    seed()
