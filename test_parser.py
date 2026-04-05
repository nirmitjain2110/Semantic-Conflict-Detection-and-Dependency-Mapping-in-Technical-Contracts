import json
from parser import process_document, extract_text_from_pdf


def test_with_text():
    print("\n===== TESTING WITH RAW TEXT =====\n")

    sample_text = """
    Service Provider guarantees uptime: 99.9%.
    Scheduled maintenance shall be 2 hours per month.
    The provider will respond within 4 hours.
    Throughput: 100 transactions per second.
    Average payload size is 1 MB.
    Network bandwidth is 10 Mbps.
    """

    output = process_document(sample_text)

    print("\n--- OUTPUT JSON ---")
    print(json.dumps(output, indent=4))

    print("\n--- DEBUG VIEW ---")
    for item in output["details"]:
        print(f"✅ {item['metric']} = {item['value']} {item['unit']} ({item['actor']})")
        print(f"   Source: {item['source']}")
        print()


def test_with_pdf(file_path):
    print("\n===== TESTING WITH PDF =====\n")

    text = extract_text_from_pdf(file_path)

    print("\n--- EXTRACTED TEXT (first 500 chars) ---")
    print(text[:500])  # avoid flooding output

    output = process_document(text)

    print("\n--- OUTPUT JSON ---")
    print(json.dumps(output, indent=4))

    print("\n--- DEBUG VIEW ---")
    for item in output["details"]:
        print(f"✅ {item['metric']} = {item['value']} {item['unit']} ({item['actor']})")
        print(f"   Source: {item['source']}")
        print()


# -----------------------------
# MAIN RUNNER
# -----------------------------
if __name__ == "__main__":

    # 🔹 OPTION 1: Test with TEXT
    test_with_text()

    # 🔹 OPTION 2: Test with PDF
    # Uncomment and provide your file
    test_with_pdf("amazon_sla_test.pdf")
