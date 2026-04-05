from parser import process_document
from conflict_engine import detect_conflicts
import json

def test_conflict_engine():

    sample_text = """
    Service Provider guarantees uptime: 99.9%.
    Scheduled maintenance shall be 10 hours per month.
    The provider will respond within 4 hours.
    Throughput: 1000 transactions per second.
    Average payload size is 2 MB.
    Network bandwidth is 10 Mbps.
    """

    parsed = process_document(sample_text)

    print("\n--- PARSED DATA ---")
    print(json.dumps(parsed, indent=4))

    conflicts = detect_conflicts(parsed, debug=True)

    print("\n--- CONFLICTS DETECTED ---")
    print(json.dumps(conflicts, indent=4))


if __name__ == "__main__":
    test_conflict_engine()
