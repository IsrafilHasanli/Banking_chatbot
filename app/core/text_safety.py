import re


def remove_user_name(response: str, firstname: str | None, surname: str | None) -> str:
    cleaned = str(response or "").replace("\r\n", "\n").replace("\r", "\n")
    for name in (firstname, surname):
        if not name:
            continue
        escaped = re.escape(name)
        cleaned = re.sub(rf"\bfor\s+{escaped}\b", "for you", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(rf"\b{escaped}'s\b", "your", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(rf"\b{escaped}\b,?[ \t]*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[ \t]+([.,!?])", r"\1", cleaned)
    cleaned = "\n".join(re.sub(r"[ \t]{2,}", " ", line).strip() for line in cleaned.split("\n"))
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()
