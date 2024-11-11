from typing import Literal, TypedDict


class MonobankAccountData(TypedDict):
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


class MonobankJarData(TypedDict):
    id: str
    sendId: str
    title: str
    description: str
    currencyCode: int
    balance: int
    goal: int


class MonobankProfileData(TypedDict):
    clientId: str
    name: str
    webHookUrl: str
    permissions: str


class MonobankRawProfileData(MonobankProfileData):
    accounts: list[MonobankAccountData]
    jars: list[MonobankJarData]


class MonobankStatementItemData(TypedDict):
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
