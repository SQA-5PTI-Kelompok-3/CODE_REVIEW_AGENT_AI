"""Money helpers. Amounts are stored as integer cents."""


def to_cents(amount_str):
    whole, _, frac = amount_str.partition(".")
    frac = (frac + "00")[:2]
    sign = -1 if whole.startswith("-") else 1
    return sign * (abs(int(whole or "0")) * 100 + int(frac))


def format_cents(cents):
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"


def split_evenly(cents, parts):
    if parts <= 0:
        raise ValueError("parts must be positive")
    base, remainder = divmod(cents, parts)
    return [base + 1 if i < remainder else base for i in range(parts)]
