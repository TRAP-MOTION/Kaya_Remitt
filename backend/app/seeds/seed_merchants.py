"""Seed script: populates merchant categories, merchants, and services.

Run from the project root:
    python -m backend.app.seeds.seed_merchants
"""
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models.merchant_category import MerchantCategory
from backend.app.models.merchant import Merchant
from backend.app.models.service import Service


SEED_DATA = [
    {
        "category": "Groceries",
        "business_name": "Chipiku Plus",
        "email": "chipiku@example.com",
        "phone": "+265991000001",
        "address": "Area 47",
        "city": "Lilongwe",
        "district": "Lilongwe",
        "verification_status": "Verified",
        "services": [
            {"service_name": "Grocery Package", "price": 50000, "description": "Weekly grocery essentials"},
            {"service_name": "Essential Food Basket", "price": 30000, "description": "Basic food staples"},
        ],
    },
    {
        "category": "Groceries",
        "business_name": "Peoples Supermarket",
        "email": "peoples@example.com",
        "phone": "+265991000002",
        "address": "Victoria Avenue",
        "city": "Blantyre",
        "district": "Blantyre",
        "verification_status": "Verified",
        "services": [
            {"service_name": "Weekly Grocery Bundle", "price": 45000},
            {"service_name": "Monthly Staples Pack", "price": 120000},
        ],
    },
    {
        "category": "Pharmacy",
        "business_name": "Kamuzu Central Hospital Pharmacy",
        "email": "kch-pharmacy@example.com",
        "phone": "+265991000003",
        "address": "KCH Campus",
        "city": "Lilongwe",
        "district": "Lilongwe",
        "verification_status": "Verified",
        "services": [
            {"service_name": "Prescription Fill", "price": 15000},
            {"service_name": "Medical Consultation", "price": 25000},
        ],
    },
    {
        "category": "Utility Provider",
        "business_name": "ESCOM Utilities",
        "email": "escom@example.com",
        "phone": "+265991000004",
        "address": "Nationwide",
        "city": "Lilongwe",
        "district": "Lilongwe",
        "verification_status": "Verified",
        "services": [
            {"service_name": "Electricity Token 5,000 MWK", "price": 5000},
            {"service_name": "Electricity Token 10,000 MWK", "price": 10000},
            {"service_name": "Electricity Token 20,000 MWK", "price": 20000},
        ],
    },
]


def get_or_create_category(category_name: str) -> MerchantCategory:
    category = db.session.execute(
        db.select(MerchantCategory).filter_by(category_name=category_name)
    ).scalar_one_or_none()
    if category:
        return category
    category = MerchantCategory(category_name=category_name)
    db.session.add(category)
    db.session.flush()
    return category


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

            category = get_or_create_category(merchant_data["category"])
            merchant = Merchant(
                category_id=category.category_id,
                business_name=merchant_data["business_name"],
                email=merchant_data.get("email"),
                phone=merchant_data.get("phone"),
                address=merchant_data.get("address"),
                city=merchant_data.get("city"),
                district=merchant_data.get("district"),
                verification_status=merchant_data["verification_status"],
            )
            db.session.add(merchant)
            db.session.flush()

            for svc in merchant_data["services"]:
                service = Service(
                    merchant_id=merchant.merchant_id,
                    service_name=svc["service_name"],
                    description=svc.get("description"),
                    price=svc["price"],
                    availability=True,
                )
                db.session.add(service)

            print(
                f"  Seeded: {merchant_data['business_name']} "
                f"({len(merchant_data['services'])} services)"
            )

        db.session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    seed()
