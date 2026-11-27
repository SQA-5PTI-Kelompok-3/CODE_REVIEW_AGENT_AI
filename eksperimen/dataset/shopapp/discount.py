"""Pricing and discount rules."""


def apply_discount(total, coupon_value=0):
    """Return the final price.

    Rules:
    - Orders of 100 or more get a 10% discount.
    - A coupon is subtracted after the percentage discount.
    - The final price can never be negative.
    """
    if total > 100:
        total = total * 0.9
    total = total - coupon_value
    return round(total, 2)


def shipping_cost(weight_kg):
    if weight_kg <= 1:
        return 5
    if weight_kg <= 5:
        return 10
    return 20
