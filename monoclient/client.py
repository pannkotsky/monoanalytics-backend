import requests

from .types import ClientInfo, StatementItem

base_url = "https://api.monobank.ua/"


def get_client_info(token: str) -> ClientInfo:
    url = base_url + "personal/client-info"
    response = requests.get(url, headers={"X-Token": token})
    return response.json()


def get_statement(
    token: str, account: str, from_date: str, to_date: str | None = ""
) -> list[StatementItem]:
    url = base_url + f"personal/statement/{account}/{from_date}/{to_date}"
    response = requests.get(url, headers={"X-Token": token})
    return response.json()
