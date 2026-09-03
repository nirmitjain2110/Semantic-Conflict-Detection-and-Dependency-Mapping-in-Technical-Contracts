import re
from difflib import SequenceMatcher
import fitz  # PyMuPDF

#pdf text extraction
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text


#preprocessing: lowercase, remove extra spaces
def preprocess(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text


#clause splitting
def split_lines(text):
    lines = re.split(r'[.\n;]', text)
    return [line.strip() for line in lines if line.strip()]


#key-value pair extraction
def extract_kv_pairs(lines):
    pairs = []

    for line in lines:
        # Case 1: key: value
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            value = parts[1].strip()
            pairs.append({"key": key, "value": value})
            continue

        # Case 2: key is value
        match = re.search(r'(.+?)\s+(is|=|shall be|will be|of|at least)\s+(.+)', line)
        if match:
            key = match.group(1).strip()
            value = match.group(3).strip()
            pairs.append({"key": key, "value": value})
            continue

        # Case 3: fallback → treat whole line as both key + value
        pairs.append({"key": line, "value": line})

    return pairs


# semantic matching using difflib
metric_map = {
    "U": ["uptime", "availability"],
    "M": ["maintenance", "downtime window", "scheduled downtime"],
    "R": ["reaction", "response time", "resolution time", "respond"],
    "Th": ["throughput", "tps", "transactions per second"],
    "P": ["payload", "message size", "data size"],
    "C": ["bandwidth", "capacity", "network speed", "mbps"]
}


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def match_metric(text):
    text = text.lower()
    best_match = None
    best_score = 0

    for metric, keywords in metric_map.items():
        for word in keywords:
            score = similarity(text, word)
            if score > best_score:
                best_score = score
                best_match = metric

    if best_score > 0.5:
        return best_match
    return None


#direct metric detection from keywords (backup)
def detect_metric_from_text(text):
    text = text.lower()

    if "uptime" in text or "availability" in text:
        return "U"
    if "maintenance" in text:
        return "M"
    if "response" in text or "respond" in text:
        return "R"
    if "throughput" in text or "tps" in text:
        return "Th"
    if "payload" in text or "data size" in text:
        return "P"
    if "bandwidth" in text or "capacity" in text:
        return "C"

    return None

#value extraction
def extract_number(text):
    match = re.search(r'\d+\.?\d*', text)
    return float(match.group()) if match else None


def extract_unit(text):
    text = text.lower()

    if "%" in text:
        return "%"
    elif "mbps" in text:
        return "Mbps"
    elif "mb" in text:
        return "MB"
    elif "hour" in text or "hr" in text:
        return "hours"
    elif "tps" in text or "transactions" in text:
        return "tps"

    return "unknown"


# -----------------------------
# ACTOR DETECTION
# -----------------------------
def detect_actor(text):
    text = text.lower()

    if "provider" in text or "service provider" in text or "amazon" in text:
        return "provider"
    elif "customer" in text or "client" in text:
        return "customer"

    return "unknown"


# -----------------------------
# MAIN PROCESSING FUNCTION
# -----------------------------
def process_document(text, debug=False):
    text = preprocess(text)
    lines = split_lines(text)
    kv_pairs = extract_kv_pairs(lines)

    result = {
        "U": None,
        "M": None,
        "R": None,
        "Th": None,
        "P": None,
        "C": None,
        "details": []
    }

    for pair in kv_pairs:
        key = pair["key"]
        value = pair["value"]

        combined_text = key + " " + value

        # STEP 1: semantic match
        metric = match_metric(combined_text)

        # STEP 2: fallback detection
        if not metric:
            metric = detect_metric_from_text(combined_text)

        # STEP 3: extract value
        number = extract_number(combined_text)
        unit = extract_unit(combined_text)
        actor = detect_actor(combined_text)

        if debug:
            print(f"DEBUG → {combined_text} | metric: {metric} | value: {number}")

        # STEP 4: store result
        if metric and number is not None:
            result[metric] = number

            result["details"].append({
                "metric": metric,
                "value": number,
                "unit": unit,
                "actor": actor,
                "source": combined_text
            })

    return result
