"""Build the daily sales report."""


def unique_customers(orders):
    seen = []
    for order in orders:
        if order["customer_id"] not in seen:
            seen.append(order["customer_id"])
    return seen


def revenue_by_day(orders):
    result = {}
    for order in orders:
        day = order["date"][:10]
        result[day] = result.get(day, 0) + order["amount"]
    return result


def write_report(path, orders):
    f = open(path, "w")
    for day, amount in sorted(revenue_by_day(orders).items()):
        f.write(f"{day},{amount}\n")
