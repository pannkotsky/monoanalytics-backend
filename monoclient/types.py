from typing import Literal, TypedDict


class Account(TypedDict):
    id: str
    sendId: str
    balance: int
    creditLimit: int
    type: Literal[
        "black", "white", "platinum", "iron", "fop", "yellow", "eAid", "madeInUkraine"
    ]
    currencyCode: int
    cashbackType: Literal["UAH", "Miles", "None"]
    maskedPan: list[str]
    iban: str


class Jar(TypedDict):
    id: str
    sendId: str
    title: str
    description: str
    currencyCode: int
    balance: int
    goal: int


class ClientInfo(TypedDict):
    clientId: str
    name: str
    webHookUrl: str
    permissions: str
    accounts: list[Account]
    jars: list[Jar]


class StatementItem(TypedDict):
    id: str
    time: int
    description: str
    mcc: int
    originalMcc: int
    hold: bool
    amount: int
    operationAmount: int
    currencyCode: int
    commissionRate: int
    cashbackAmount: int
    balance: int
    counterName: str
