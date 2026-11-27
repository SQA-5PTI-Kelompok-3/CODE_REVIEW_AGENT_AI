"""Parse incoming order payloads."""
import json


def parse_order(raw):
    try:
        data = json.loads(raw)
        return {"id": int(data["id"]), "items": data["items"]}
    except:
        return None


def order_item_count(raw):
    order = parse_order(raw)
    return len(order["items"])
