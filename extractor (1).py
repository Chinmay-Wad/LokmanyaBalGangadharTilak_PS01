import re
from utils import ABBREVIATIONS, FORMS


def normalize(text):
    for k, v in ABBREVIATIONS.items():
        text = text.replace(k, v)
    return text


def find(pattern, text):
    m = re.search(pattern, text, re.I)
    return m.group(0) if m else None


def extract_single(part):
    part = normalize(part)
    tokens = part.split()

    med = {
        "drug_name": None,
        "strength": find(r'\d+\s?(mg|g|ml|units)', part),
        "form": None,
        "route": None,
        "frequency": None,
        "duration": find(r'\d+\s?(days?|d)', part)
    }

    for t in tokens:
        if t in FORMS:
            med["form"] = FORMS[t]
        if t.lower() in ["oral", "intravenous"]:
            med["route"] = t
        if "daily" in t.lower() or "needed" in t.lower():
            med["frequency"] = t

    for t in tokens:
        if t[0].isalpha() and t not in FORMS:
            med["drug_name"] = t
            break

    return med


def extract_medications(text):
    parts = re.split(r'\+|,', text)
    return [extract_single(p.strip()) for p in parts if p.strip()]