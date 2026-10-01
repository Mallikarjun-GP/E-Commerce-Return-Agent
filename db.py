"""MongoDB database layer – users, orders, carts, and CSV synchronization."""

from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import bcrypt
from pymongo import MongoClient
from pymongo.collection import Collection

def _get_mongo_uri() -> str:
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "MONGO_URI" in st.secrets:
            return str(st.secrets["MONGO_URI"])
    except Exception:
        pass
    uri = os.getenv("MONGO_URI")
    if uri:
        return uri
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("MONGO_URI="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
        except Exception:
            pass
    return "mongodb://localhost:27017/"


MONGO_URI = _get_mongo_uri()
DB_NAME = "ecommerce_returns"
DATA_FILE = Path(__file__).parent / "data" / "orders.csv"

CSV_FIELDNAMES = [
    "order_id",
    "customer_id",
    "customer_name",
    "product",
    "category",
    "amount_inr",
    "quantity",
    "payment_method",
    "status",
    "shipping_days",
    "city",
    "state",
    "days_since_delivery",
    "previously_returned",
    "return_reason",
]


def _client() -> MongoClient:
    return MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)


def _db():
    return _client()[DB_NAME]


def _users() -> Collection:
    return _db()["users"]


def _user_orders() -> Collection:
    return _db()["user_orders"]


# ── CSV Helpers ─────────────────────────────────────────────────────────────


def append_order_to_csv(doc: dict, customer_name: str = "") -> None:
    """Append a newly placed order to data/orders.csv."""
    try:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        file_exists = DATA_FILE.exists() and DATA_FILE.stat().st_size > 0

        product_name = ", ".join(i.get("product_name", "") for i in doc.get("items", [])) or "Item"
        category = doc["items"][0].get("category", "General") if doc.get("items") else "General"
        qty = sum(i.get("qty", 1) for i in doc.get("items", []))
        total_inr = int(doc.get("total_inr", 0))

        row = {
            "order_id": doc["order_id"],
            "customer_id": doc.get("username", "customer"),
            "customer_name": customer_name or doc.get("customer_name", doc.get("username", "Customer")),
            "product": product_name,
            "category": category,
            "amount_inr": total_inr,
            "quantity": qty,
            "payment_method": doc.get("payment_method", "Online UPI"),
            "status": doc.get("status", "Delivered"),
            "shipping_days": doc.get("shipping_days", 3),
            "city": doc.get("city", "Bangalore"),
            "state": doc.get("state", "Karnataka"),
            "days_since_delivery": doc.get("days_since_delivery", 0),
            "previously_returned": str(bool(doc.get("previously_returned", False))),
            "return_reason": doc.get("return_reason", "") or "",
        }

        with DATA_FILE.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except Exception as exc:
        print(f"[CSV Append Error] {exc}")


def update_order_in_csv(order_id: str, previously_returned: bool, return_reason: str) -> None:
    """Update return status of an order in data/orders.csv."""
    if not DATA_FILE.exists():
        return
    try:
        with DATA_FILE.open("r", newline="", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            fieldnames = reader[0].keys() if reader else CSV_FIELDNAMES

        updated = False
        for row in reader:
            if row.get("order_id") == order_id:
                row["previously_returned"] = str(previously_returned)
                row["return_reason"] = return_reason
                updated = True

        if updated:
            with DATA_FILE.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(reader)
    except Exception as exc:
        print(f"[CSV Update Error] {exc}")


def sync_all_mongo_orders_to_csv() -> None:
    """Sync any orders from MongoDB that are not in data/orders.csv."""
    try:
        existing_ids = set()
        if DATA_FILE.exists() and DATA_FILE.stat().st_size > 0:
            with DATA_FILE.open("r", newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    existing_ids.add(row.get("order_id"))

        col = _user_orders()
        all_orders = list(col.find({}))
        users_col = _users()
        user_names = {u["username"]: u.get("full_name", u["username"]) for u in users_col.find({})}

        for doc in all_orders:
            oid = doc.get("order_id")
            if oid and oid not in existing_ids:
                c_name = user_names.get(doc.get("username", ""), doc.get("username", ""))
                append_order_to_csv(doc, customer_name=c_name)
                existing_ids.add(oid)
    except Exception as exc:
        print(f"[CSV Sync Error] {exc}")


# ── Auth ────────────────────────────────────────────────────────────────────


def register_user(username: str, email: str, password: str, full_name: str) -> dict[str, Any]:
    """Create a new user; returns {"ok": True} or {"ok": False, "error": ...}."""
    col = _users()
    if col.find_one({"$or": [{"username": username}, {"email": email}]}):
        return {"ok": False, "error": "Username or e-mail already registered."}
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    col.insert_one({
        "username": username,
        "email": email,
        "password_hash": hashed,
        "full_name": full_name,
        "created_at": datetime.now(timezone.utc),
    })
    return {"ok": True}


def login_user(username: str, password: str) -> dict[str, Any]:
    """Verify credentials; returns user doc (without hash) or None."""
    user = _users().find_one({"username": username})
    if not user:
        return None
    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return None
    user.pop("password_hash", None)
    user["_id"] = str(user["_id"])
    return user


def get_user_by_username(username: str) -> dict | None:
    user = _users().find_one({"username": username})
    if user:
        user.pop("password_hash", None)
        user["_id"] = str(user["_id"])
    return user


# ── Orders ──────────────────────────────────────────────────────────────────


def place_order(username: str, items: list[dict], customer_name: str = "") -> dict[str, Any]:
    """Persist a new order for a user in MongoDB and data/orders.csv."""
    col = _user_orders()
    count = col.count_documents({"username": username})
    order_id = f"USR-{username[:4].upper()}-{count + 1:04d}"
    
    if not customer_name:
        u = get_user_by_username(username)
        customer_name = u.get("full_name", username) if u else username

    doc = {
        "order_id": order_id,
        "username": username,
        "customer_name": customer_name,
        "items": items,
        "total_inr": sum(i["price"] * i["qty"] for i in items),
        "status": "Delivered",
        "placed_at": datetime.now(timezone.utc),
        "days_since_delivery": 0,
        "previously_returned": False,
        "return_reason": "",
    }
    col.insert_one(doc)
    doc["_id"] = str(doc["_id"])

    # Synchronize order into data/orders.csv
    append_order_to_csv(doc, customer_name=customer_name)

    return doc


def get_user_orders(username: str) -> list[dict]:
    """Return all orders for a user, most recent first."""
    col = _user_orders()
    docs = list(col.find({"username": username}, sort=[("placed_at", -1)]))
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs


def mark_returned(order_id: str, return_reason: str) -> None:
    """Update the order document to reflect a completed return in MongoDB & CSV."""
    _user_orders().update_one(
        {"order_id": order_id},
        {"$set": {"previously_returned": True, "return_reason": return_reason}},
    )
    update_order_in_csv(order_id, True, return_reason)


def get_order_by_id(order_id: str) -> dict | None:
    doc = _user_orders().find_one({"order_id": order_id})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

