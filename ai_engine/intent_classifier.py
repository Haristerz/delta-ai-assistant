INTENT_KEYWORDS = {
    "miles_policy": [
        "miles expire", "earn miles", "how miles work", "miles program",
        "skymiles", "redeem miles", "miles for", "how many miles",
        "medallion", "miles transfer", "miles credit",
    ],
    "baggage": [
        "baggage", "bag", "luggage", "carry on", "carry-on",
        "checked bag", "overweight", "oversized", "suitcase",
        "lost bag", "damaged bag", "baggage fee",
    ],
    "upgrade": [
        "upgrade", "first class", "business class", "better seat",
        "comfort+", "delta one", "cabin", "seat upgrade",
        "global upgrade", "same day upgrade", "upgrade certificate",
    ],
    "account": [
        "my miles", "my balance", "my account", "my profile",
        "my flights", "my history", "my tier", "my status",
        "my invoices", "my bookings", "how many miles do i have",
    ],
}

def classify_intent(message: str) -> str:
    message_lower = message.lower()

    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                return intent

    return "general"
