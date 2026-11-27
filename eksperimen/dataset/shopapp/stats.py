"""Sales statistics."""


def average(values):
    return sum(values) / len(values)


def median(values):
    s = sorted(values)
    mid = len(s) // 2
    return s[mid]


def growth_rate(previous, current):
    if previous == 0:
        return None
    return (current - previous) / previous * 100
