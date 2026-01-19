"""
Maps natural language intent to feature weights
"""

KEYWORD_MAP = {
    "camera": ["camera", "photo", "video", "low light"],
    "battery": ["battery", "long lasting", "all day"],
    "performance": ["fast", "gaming", "performance"],
    "price": ["cheap", "budget", "affordable"],
    "weight": ["light", "compact"],
    "display_size": ["big screen", "small screen"]
}

def infer_weights(nl_query: str):
    weights = {
        "price": 0.15,
        "cam_resolution": 0.15,
        "battery": 0.15,
        "ram": 0.15,
        "display_size": 0.15,
        "weight": 0.10,
        "release_year": 0.15,
    }

    text = nl_query.lower()

    for feature, keywords in KEYWORD_MAP.items():
        if any(k in text for k in keywords):
            for f in weights:
                weights[f] *= 0.85
            if feature == "camera":
                weights["cam_resolution"] += 0.25
            elif feature == "battery":
                weights["battery"] += 0.25
            elif feature == "price":
                weights["price"] += 0.25

    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}
