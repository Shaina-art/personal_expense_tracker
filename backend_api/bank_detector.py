import re

BANK_PATTERNS = {
    "SBI": re.compile(r"\bSBI\b", re.IGNORECASE),
    "HDFC": re.compile(r"\bHDFC\b", re.IGNORECASE),
    "ICICI": re.compile(r"\bICICI\b", re.IGNORECASE),
    "AXIS": re.compile(r"\bAXIS\b", re.IGNORECASE),
    "KOTAK": re.compile(r"\bKOTAK\b", re.IGNORECASE),
    "BOB": re.compile(r"\bBANK OF BARODA\b|\bBOB\b", re.IGNORECASE),
    "Bassein Bank": re.compile(r"\bBCCB\b", re.IGNORECASE),  # ✅ Added
}

def detect_bank_name(sender: str, body: str, user_aliases: dict = {}) -> str:
    # 1. User-defined alias
    for alias, bank in user_aliases.items():
        if alias.lower() in sender.lower() or alias.lower() in body.lower():
            print(f"Alias matched: {alias} → {bank}")
            return bank

    # 2. Regex pattern
    for bank, pattern in BANK_PATTERNS.items():
        if pattern.search(sender) or pattern.search(body):
            print(f"Pattern matched: {bank}")
            return bank

    # 3. Fallback prefix
    fallback = extract_bank_from_prefix(sender)
    if fallback:
        print(f"Fallback prefix matched: {fallback}")
        return fallback

    print("Bank not detected.")
    return "Unknown"


def extract_bank_from_prefix(sender: str) -> str:
    known_prefixes = {
        "HDFC": "HDFC",
        "ICIC": "ICICI",
        "AXIS": "AXIS",
        "SBI": "SBI",
        "BOB": "BOB",
        "KOTK": "KOTAK"
        
    }
    for prefix, bank in known_prefixes.items():
        if prefix.lower() in sender.lower():
            return bank
    return None
