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