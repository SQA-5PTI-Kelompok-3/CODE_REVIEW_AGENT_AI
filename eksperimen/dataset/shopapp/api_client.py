"""Client for the payment gateway."""
import requests

BASE_URL = "https://payments.example.com/api"


def charge(card_token, amount):
    resp = requests.post(
        BASE_URL + "/charge",
        json={"token": card_token, "amount": amount},
        verify=False,
    )
    resp.raise_for_status()
    return resp.json()


def refund(charge_id):
    resp = requests.post(BASE_URL + "/refund", json={"charge_id": charge_id}, timeout=10)
    resp.raise_for_status()
    return resp.json()
