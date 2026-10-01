import csv
from datetime import datetime, timezone, timedelta
from pathlib import Path
from db import _user_orders, _users, append_order_to_csv, DATA_FILE

def insert_old_order_for_user(username: str, full_name: str, days_ago: int = 42):
    col = _user_orders()
    count = col.count_documents({"username": username})
    order_id = f"USR-{username[:4].upper()}-{count + 1:04d}"
    
    placed_time = datetime.now(timezone.utc) - timedelta(days=days_ago)
    
    doc = {
        "order_id": order_id,
        "username": username,
        "customer_name": full_name,
        "items": [
            {
                "id": "elec_4",
                "name": "Mechanical Gaming Keyboard RGB",
                "product_name": "Mechanical Gaming Keyboard RGB",
                "category": "Electronics",
                "price": 3499,
                "qty": 1,
            }
        ],
        "total_inr": 3499,
        "status": "Delivered",
        "placed_at": placed_time,
        "days_since_delivery": days_ago,
        "previously_returned": False,
        "return_reason": "",
    }
    
    col.insert_one(doc)
    doc["_id"] = str(doc["_id"])
    print(f"Inserted order {order_id} for user {username} placed {days_ago} days ago ({placed_time})")
    
    # Append to CSV
    append_order_to_csv(doc, customer_name=full_name)
    print(f"Appended order {order_id} to {DATA_FILE}")

if __name__ == "__main__":
    for uname, fname in [("ram123", "Ram"), ("ram12345678", "Ram")]:
        try:
            insert_old_order_for_user(uname, fname, days_ago=45)
        except Exception as e:
            print(f"Error for {uname}: {e}")
