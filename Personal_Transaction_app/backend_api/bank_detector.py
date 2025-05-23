import re

BANK_PATTERNS = {
    "SBI": re.compile(r".*SBI.*", re.IGNORECASE),
    "HDFC": re.compile(r".*HDFC.*", re.IGNORECASE),
    "ICICI": re.compile(r".*ICICI.*", re.IGNORECASE),
    "AXIS": re.compile(r".*AXIS.*", re.IGNORECASE),
    "BCCB": re.compile(r".*BCCB.*", re.IGNORECASE),
}

def detect_bank(sender: str) -> str:
    for bank, pattern in BANK_PATTERNS.items():
        if pattern.match(sender):
            return bank
    return "Unknown"
