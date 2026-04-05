import math


# Convert uptime % to allowed downtime (hours/month)

def calculate_allowed_downtime(uptime_percent):
    total_hours_month = 30 * 24  # 720 hours
    downtime_fraction = (100 - uptime_percent) / 100
    return downtime_fraction * total_hours_month



# dependendcy graph for metrics 
def build_dependency_graph(data):
    graph = {
        "U": ["M", "R"],   # uptime depends on maintenance & reaction
        "Th": ["C", "P"]   # throughput depends on capacity & payload
    }
    return graph


# conflicy: Uptime vs Reaction Time

def check_uptime_vs_reaction(data):
    U = data.get("U")
    R = data.get("R")

    if U is None or R is None:
        return None

    allowed_downtime = calculate_allowed_downtime(U)

    if R > allowed_downtime:
        return {
            "type": "Uptime vs Reaction Time",
            "severity": "HIGH",
            "message": f"Reaction time ({R} hrs) exceeds allowed downtime ({allowed_downtime:.2f} hrs/month).",
            "fix": f"Reduce reaction time below {allowed_downtime:.2f} hrs OR lower uptime guarantee."
        }

    return None


#conflict: Uptime vs Maintenance
def check_uptime_vs_maintenance(data):
    U = data.get("U")
    M = data.get("M")

    if U is None or M is None:
        return None

    allowed_downtime = calculate_allowed_downtime(U)

    if M > allowed_downtime:
        return {
            "type": "Uptime vs Maintenance",
            "severity": "HIGH",
            "message": f"Scheduled maintenance ({M} hrs) exceeds allowed downtime ({allowed_downtime:.2f} hrs/month).",
            "fix": f"Reduce maintenance to ≤ {allowed_downtime:.2f} hrs OR reduce uptime guarantee."
        }

    return None


#conflict: Throughput vs Capacity
def check_throughput_vs_capacity(data):
    Th = data.get("Th")   # transactions per second
    P = data.get("P")     # MB
    C = data.get("C")     # Mbps

    if Th is None or P is None or C is None:
        return None

    # Convert payload MB → Mb
    payload_megabits = P * 8

    required_bandwidth = Th * payload_megabits  # Mbps

    if required_bandwidth > C:
        return {
            "type": "Throughput vs Capacity",
            "severity": "HIGH",
            "message": f"Required bandwidth ({required_bandwidth:.2f} Mbps) exceeds capacity ({C} Mbps).",
            "fix": (
                f"Options:\n"
                f"- Reduce throughput to ≤ {C / payload_megabits:.2f} TPS\n"
                f"- Increase bandwidth to ≥ {required_bandwidth:.2f} Mbps\n"
                f"- Reduce payload size"
            )
        }

    return None

def detect_conflicts(data, debug=False):
    conflicts = []

    graph = build_dependency_graph(data)

    if debug:
        print("\n--- DEPENDENCY GRAPH ---")
        for k, v in graph.items():
            print(f"{k} depends on {v}")

    # Run checks
    checks = [
        check_uptime_vs_reaction,
        check_uptime_vs_maintenance,
        check_throughput_vs_capacity
    ]

    for check in checks:
        result = check(data)
        if result:
            conflicts.append(result)

    return {
        "total_conflicts": len(conflicts),
        "conflicts": conflicts
    }
