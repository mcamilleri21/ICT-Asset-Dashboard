"""Seed realistic demo values for provider trading_name, country, LEI, parent_company."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import Provider

PROVIDER_DETAILS = {
    "DocSys Corp Ltd.": {
        "trading_name": "DocSys",
        "country_of_incorporation": "IE",
        "lei": "5493001KJTIIGC8Y1R12",
        "parent_company": "Verint Systems Inc.",
    },
    "PortFolio Solutions Inc.": {
        "trading_name": "PortFolio",
        "country_of_incorporation": "US",
        "lei": "7LTWFZYICNSX8D621K86",
        "parent_company": "SS&C Technologies Holdings Inc.",
    },
    "DataMarkets Ltd.": {
        "trading_name": "DataMarkets",
        "country_of_incorporation": "GB",
        "lei": "213800WSGIIZCXF1P572",
        "parent_company": "Refinitiv Ltd.",
    },
    "ScreenCheck Ltd.": {
        "trading_name": "ScreenCheck",
        "country_of_incorporation": "NL",
        "lei": "724500PM7A7XIDTW5810",
        "parent_company": "IDEMIA Group S.A.S.",
    },
    "PeopleHR Systems Ltd.": {
        "trading_name": "PeopleHR",
        "country_of_incorporation": "GB",
        "lei": "2138001OBBCQPK9KRH66",
        "parent_company": "Access Group Holdings Ltd.",
    },
    "AccPkg Solutions Ltd.": {
        "trading_name": "AccPkg",
        "country_of_incorporation": "IE",
        "lei": "635400D0T3B3ZZ87JP07",
        "parent_company": "Sage Group PLC",
    },
    "TeleComm Provider PLC": {
        "trading_name": "TeleComm",
        "country_of_incorporation": "GB",
        "lei": "213800TB5WZRB1PLNF47",
        "parent_company": "BT Group PLC",
    },
    "CloudHost Services Ltd.": {
        "trading_name": "CloudHost",
        "country_of_incorporation": "US",
        "lei": "LUWFAEV42M0FTFD1SL01",
        "parent_company": "Amazon.com Inc.",
    },
    "SecureNet Ltd.": {
        "trading_name": "SecureNet",
        "country_of_incorporation": "GB",
        "lei": "549300LWXHKZWIVQZ070",
        "parent_company": "Palo Alto Networks Inc.",
    },
    "ServiceDesk Co. Ltd.": {
        "trading_name": "ServiceDesk",
        "country_of_incorporation": "IE",
        "lei": "5493001KJTIIGC8Y9911",
        "parent_company": "Freshworks Inc.",
    },
}


def run():
    db = SessionLocal()
    updated = 0
    missing = []
    for legal_name, details in PROVIDER_DETAILS.items():
        p = db.query(Provider).filter(Provider.legal_name == legal_name).first()
        if p:
            for k, v in details.items():
                setattr(p, k, v)
            updated += 1
        else:
            missing.append(legal_name)
    db.commit()
    db.close()
    print(f"Updated {updated}/{len(PROVIDER_DETAILS)} providers.")
    if missing:
        print(f"Not found (skipped): {', '.join(missing)}")


if __name__ == "__main__":
    run()
