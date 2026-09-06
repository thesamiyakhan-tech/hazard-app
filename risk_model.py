def calculate_risk_score(rainfall, slope, history):

    # ---- Step 1: Rainfall ke points (Max 40) ----
    # Reference point: 205mm/24hr preceded the 28 May 2024 Cyclone
    # Remal landslides in Aizawl (Sangi et al. 2025). We treat this
    # as our "high risk" reference, not a proven universal cutoff.
    if rainfall < 50:
        rainfall_points = 10          # Normal monsoon day
    elif rainfall <= 150:
        rainfall_points = 25          # Heavy rain, watch zone
    else:
        rainfall_points = 40          # Near/above the 205mm Remal reference

    # ---- Step 2: Slope ke points (Max 35) ----
    # Slope is repeatedly confirmed as a core factor in Aizawl-specific
    # studies (Barman & Das 2024). Exact degree bins are still a
    # prototype assumption pending DEM/GIS slope data.
    if slope < 15:
        slope_points = 5
    elif slope <= 30:
        slope_points = 20
    else:
        slope_points = 35

    # ---- Step 3: History ke points (Max 25) ----
    # Based on verified historical events (Mizoram SDMP 2020,
    # Science Vision 2015, Sangi et al. 2025).
    if history == True:
        history_points = 25
    else:
        history_points = 0

    # ---- Step 4: Sab points jodna ----
    total_score = rainfall_points + slope_points + history_points

    return total_score


def get_risk_category(score):
    """
    Score (0-100) leta hai aur uski category batata hai:
    Green (safe) -> Yellow -> Orange -> Red (bahut risky)
    """
    if score <= 25:
        return "Green"
    elif score <= 50:
        return "Yellow"
    elif score <= 75:
        return "Orange"
    else:
        return "Red"


# ==============================================
# TESTING - Real Aizawl historical locations
# (Source: Saif's research pack, Parts 1-3 + Improved Pack)
# ==============================================

if __name__ == "__main__":

    # Rainfall values below are illustrative daily/24hr figures for
    # testing the formula logic - NOT official recorded rainfall for
    # each specific historical event (exact per-event rainfall data
    # was not available for all locations in the research pack).
    # The 28 May 2024 entry uses the actual documented 205mm figure.
    test_locations = [
        {
            "name": "South Hlimen (1992 quarry rockslide, 66 deaths)",
            "rainfall": 60, "slope": 32, "history": True
        },
        {
            "name": "Hunthar (recurrent sinking, 1992-2011)",
            "rainfall": 40, "slope": 20, "history": True
        },
        {
            "name": "Armed Veng (2004-05, 100+ houses affected)",
            "rainfall": 55, "slope": 25, "history": True
        },
        {
            "name": "Laipuitlang (11 May 2013, 17 deaths)",
            "rainfall": 70, "slope": 38, "history": True
        },
        {
            "name": "Multiple sites - Cyclone Remal (28 May 2024, 34 deaths)",
            "rainfall": 205, "slope": 30, "history": True
        },
        {
            "name": "Hypothetical safe zone (no past history)",
            "rainfall": 20, "slope": 10, "history": False
        },
    ]

    print("=" * 65)
    print("AIZAWL LANDSLIDE RISK REPORT (Using Real Historical Locations)")
    print("=" * 65)

    for loc in test_locations:
        score = calculate_risk_score(loc["rainfall"], loc["slope"], loc["history"])
        category = get_risk_category(score)

        print(f"\nLocation      : {loc['name']}")
        print(f"Rainfall      : {loc['rainfall']} mm (24hr)")
        print(f"Slope         : {loc['slope']} degrees")
        print(f"Past History  : {loc['history']}")
        print(f"Risk Score    : {score} / 100")
        print(f"Risk Category : {category}")

    print("\n" + "=" * 65)
    print("NOTE: Weights above are prototype assumptions, not official")
    print("scientific weights. See disclaimer at top of file.")
    print("=" * 65)