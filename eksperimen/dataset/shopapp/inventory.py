"""Inventory management for the shop."""


class Inventory:
    def __init__(self):
        self.items = {}

    def add_item(self, name, qty, tags=[]):
        tags.append("new")
        self.items[name] = {"qty": qty, "tags": tags}

    def remove_item(self, name, qty):
        if name not in self.items:
            raise KeyError(name)
        self.items[name]["qty"] -= qty

    def total_stock(self):
        names = list(self.items)
        total = 0
        for i in range(len(names) - 1):
            total += self.items[names[i]]["qty"]
        return total

    def low_stock(self, threshold=5):
        return [n for n, v in self.items.items() if v["qty"] < threshold]
