import json
from datetime import datetime


# Determine the next visible astronomical event for a given location
def next_visible_event(location: str) -> str:
    """Returns the next visible astronomical event for a location."""

    today = int(datetime.now().strftime("%m%d"))
    loc = location.lower().replace(" ", "_")

    for name, event_type, date, date_str, locs in EVENTS:
        if loc in locs and date >= today:
            return json.dumps({
                "event": name,
                "type": event_type,
                "date": date_str,
                "visible_from": sorted(locs)
            })

    return json.dumps({
        "message": f"No upcoming events found for {location}."
    })


# Calculate the cost of an astronomical observation
def calculate_observation_cost(
    telescope_tier: str,
    hours: float,
    priority: str
) -> str:
    """Calculate telescope observation cost."""

    tier_rates = {
        "standard": 100,
        "advanced": 200,
        "premium": 350
    }

    priority_multipliers = {
        "low": 0.8,
        "normal": 1.0,
        "high": 1.5
    }

    tier = telescope_tier.lower()
    priority_level = priority.lower()

    if tier not in tier_rates:
        return json.dumps({
            "error": f"Unknown telescope tier: {telescope_tier}"
        })

    if priority_level not in priority_multipliers:
        return json.dumps({
            "error": f"Unknown priority level: {priority}"
        })

    base_cost = tier_rates[tier] * hours
    total_cost = base_cost * priority_multipliers[priority_level]

    return json.dumps({
        "telescope_tier": telescope_tier,
        "hours": hours,
        "priority": priority,
        "cost": total_cost
    })


# Generate an observation report
def generate_observation_report(
    event_name: str,
    location: str,
    telescope_tier: str,
    hours: float,
    priority: str,
    observer_name: str
) -> str:
    """Generate a summary report for an astronomical observation."""

    return json.dumps({
        "event_name": event_name,
        "location": location,
        "telescope_tier": telescope_tier,
        "hours": hours,
        "priority": priority,
        "observer_name": observer_name,
        "status": "Observation report generated successfully"
    })