"""Deterministic synthetic sample mirroring the Olist schema.

Same tables/columns as the real Kaggle dump, ~1,200 orders, seeded RNG — so the
repo, tests, and eval all run with zero downloads, and everything transfers
unchanged when the full dataset is dropped into data/olist/.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

import pandas as pd

SEED = 42

CATEGORIES = {  # portuguese -> english, real Olist category names
    "beleza_saude": ("health_beauty", 65),
    "informatica_acessorios": ("computers_accessories", 90),
    "cama_mesa_banho": ("bed_bath_table", 55),
    "moveis_decoracao": ("furniture_decor", 75),
    "esporte_lazer": ("sports_leisure", 70),
    "relogios_presentes": ("watches_gifts", 130),
    "telefonia": ("telephony", 60),
    "brinquedos": ("toys", 50),
    "utilidades_domesticas": ("housewares", 45),
    "automotivo": ("auto", 85),
    "perfumaria": ("perfumery", 72),
    "eletronicos": ("electronics", 110),
}

STATES = ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "DF", "GO", "ES"]
STATE_W = [0.42, 0.13, 0.12, 0.06, 0.05, 0.04, 0.04, 0.02, 0.02, 0.02]
CITIES = {
    "SP": "sao paulo", "RJ": "rio de janeiro", "MG": "belo horizonte",
    "RS": "porto alegre", "PR": "curitiba", "SC": "florianopolis",
    "BA": "salvador", "DF": "brasilia", "GO": "goiania", "ES": "vitoria",
}
PAY_TYPES = ["credit_card", "boleto", "voucher", "debit_card"]
PAY_W = [0.74, 0.19, 0.04, 0.03]
STATUSES = ["delivered", "shipped", "canceled", "processing"]
STATUS_W = [0.93, 0.03, 0.025, 0.015]

START = datetime(2017, 1, 1)
DAYS = 607  # through 2018-08-31


def _hexid(rng: random.Random) -> str:
    return "".join(rng.choices("0123456789abcdef", k=32))


def generate(n_orders: int = 1200) -> dict[str, pd.DataFrame]:
    rng = random.Random(SEED)
    cats = list(CATEGORIES)

    products = [
        {
            "product_id": _hexid(rng),
            "product_category_name": rng.choice(cats),
            "product_weight_g": rng.randint(50, 8000),
            "product_length_cm": rng.randint(10, 100),
            "product_height_cm": rng.randint(2, 60),
            "product_width_cm": rng.randint(5, 60),
            "product_photos_qty": rng.randint(1, 6),
        }
        for _ in range(150)
    ]
    sellers = [
        {
            "seller_id": _hexid(rng),
            "seller_zip_code_prefix": rng.randint(1000, 99000),
            "seller_state": (st := rng.choices(STATES, STATE_W)[0]),
            "seller_city": CITIES[st],
        }
        for _ in range(40)
    ]
    people = [_hexid(rng) for _ in range(900)]  # unique persons; some order twice
    customers, orders, items, payments, reviews = [], [], [], [], []

    for _ in range(n_orders):
        st = rng.choices(STATES, STATE_W)[0]
        customer = {
            "customer_id": _hexid(rng),
            "customer_unique_id": rng.choice(people),
            "customer_zip_code_prefix": rng.randint(1000, 99000),
            "customer_city": CITIES[st],
            "customer_state": st,
        }
        customers.append(customer)

        # upward trend: later days slightly more likely
        day = int(DAYS * (rng.random() ** 0.8))
        purchase = START + timedelta(days=day, hours=rng.randint(0, 23), minutes=rng.randint(0, 59))
        status = rng.choices(STATUSES, STATUS_W)[0]
        approved = purchase + timedelta(hours=rng.randint(1, 24))
        carrier = approved + timedelta(days=rng.randint(1, 5)) if status in ("delivered", "shipped") else None
        delivery_days = rng.randint(3, 28)
        delivered = purchase + timedelta(days=delivery_days) if status == "delivered" else None
        estimated = purchase + timedelta(days=rng.randint(14, 38))

        order = {
            "order_id": _hexid(rng),
            "customer_id": customer["customer_id"],
            "order_status": status,
            "order_purchase_timestamp": purchase,
            "order_approved_at": approved,
            "order_delivered_carrier_date": carrier,
            "order_delivered_customer_date": delivered,
            "order_estimated_delivery_date": estimated,
        }
        orders.append(order)

        total = 0.0
        for item_no in range(1, rng.choices([1, 2, 3], [0.82, 0.13, 0.05])[0] + 1):
            product = rng.choice(products)
            base = CATEGORIES[product["product_category_name"]][1]
            price = round(base * rng.uniform(0.4, 2.5), 2)
            freight = round(rng.uniform(5, 45), 2)
            items.append(
                {
                    "order_id": order["order_id"],
                    "order_item_id": item_no,
                    "product_id": product["product_id"],
                    "seller_id": rng.choice(sellers)["seller_id"],
                    "shipping_limit_date": approved + timedelta(days=rng.randint(2, 7)),
                    "price": price,
                    "freight_value": freight,
                }
            )
            total += price + freight

        pay_type = rng.choices(PAY_TYPES, PAY_W)[0]
        payments.append(
            {
                "order_id": order["order_id"],
                "payment_sequential": 1,
                "payment_type": pay_type,
                "payment_installments": rng.randint(1, 10) if pay_type == "credit_card" else 1,
                "payment_value": round(total, 2),
            }
        )

        if status == "delivered" and rng.random() < 0.97:
            late = delivered is not None and delivered > estimated
            weights = [0.35, 0.15, 0.18, 0.17, 0.15] if late else [0.07, 0.03, 0.08, 0.20, 0.62]
            score = rng.choices([1, 2, 3, 4, 5], weights)[0]
            created = delivered + timedelta(days=rng.randint(0, 5))
            reviews.append(
                {
                    "review_id": _hexid(rng),
                    "order_id": order["order_id"],
                    "review_score": score,
                    "review_comment_title": None,
                    "review_comment_message": None,
                    "review_creation_date": created,
                    "review_answer_timestamp": created + timedelta(days=rng.randint(0, 3)),
                }
            )

    translation = [
        {"product_category_name": pt, "product_category_name_english": en}
        for pt, (en, _) in CATEGORIES.items()
    ]

    return {
        "customers": pd.DataFrame(customers),
        "orders": pd.DataFrame(orders),
        "order_items": pd.DataFrame(items),
        "order_payments": pd.DataFrame(payments),
        "order_reviews": pd.DataFrame(reviews),
        "products": pd.DataFrame(products),
        "sellers": pd.DataFrame(sellers),
        "category_translation": pd.DataFrame(translation),
    }
