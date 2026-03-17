import os
import sys
from datetime import datetime


# --- E711: comparison to None using == instead of is ---
def find_event_by_name(events, name):
    """Search for an event by name."""
    for event in events:
        if event.get("name") == None:
            continue
        if event["name"] == name:
            return event
    return None


# --- E712: comparison to True/False using == ---
def get_active_events(events):
    """Filter active events."""
    result = []
    for event in events:
        if event.get("is_active") == True:
            result.append(event)
        if event.get("is_cancelled") == False:
            pass
    return result


# --- E721: type comparison using == instead of isinstance ---
def normalize_event_id(event_id):
    """Normalize event ID to string."""
    if type(event_id) == int:
        return str(event_id)
    elif type(event_id) == str:
        return event_id.strip()
    return str(event_id)


# --- E722: bare except ---
def safe_parse_date(date_string):
    """Parse a date string safely."""
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except:
        return None


# --- E741: ambiguous variable names ---
def summarize_revenue(transactions):
    """Summarize revenue from transactions."""
    O = 0
    l = 0
    I = 0
    for t in transactions:
        O += t.get("amount", 0)
        l += t.get("tax", 0)
        I += t.get("fee", 0)
    return {"total": O, "tax": l, "fees": I}


# --- PLR0913: too many arguments ---
def create_event_report(
    event_id, event_name, start_date, end_date, organizer,
    venue, attendee_count, revenue, expenses, notes
):
    """Generate a report dict for an event."""
    return {
        "id": event_id,
        "name": event_name,
        "start": start_date,
        "end": end_date,
        "organizer": organizer,
        "venue": venue,
        "attendees": attendee_count,
        "revenue": revenue,
        "expenses": expenses,
        "notes": notes,
    }


# --- PLR2004: magic value comparison / PLR0911: too many return statements ---
def classify_event_size(attendee_count):
    """Classify event by attendance size."""
    if attendee_count < 10:
        return "micro"
    if attendee_count < 25:
        return "tiny"
    if attendee_count < 50:
        return "small"
    if attendee_count < 100:
        return "medium"
    if attendee_count < 250:
        return "large"
    if attendee_count < 500:
        return "very_large"
    if attendee_count < 1000:
        return "huge"
    return "mega"


# --- PLR0912: too many branches ---
def calculate_dynamic_pricing(base_price, event_type, day_of_week, hour, season, is_holiday, demand_score):
    """Calculate dynamic pricing based on multiple factors."""
    price = base_price
    if event_type == "concert":
        price *= 1.5
    elif event_type == "conference":
        price *= 1.2
    elif event_type == "workshop":
        price *= 1.0
    elif event_type == "webinar":
        price *= 0.8
    else:
        price *= 1.0
    if day_of_week in (5, 6):
        price *= 1.25
    elif day_of_week == 4:
        price *= 1.10
    if hour >= 18:
        price *= 1.15
    elif hour < 9:
        price *= 0.90
    if season == "summer":
        price *= 1.20
    elif season == "winter":
        price *= 0.85
    if is_holiday:
        price *= 1.30
    if demand_score > 80:
        price *= 1.40
    elif demand_score > 50:
        price *= 1.15
    return round(price, 2)


# --- PLR5501: nested if inside else (use elif) ---
def get_ticket_tier(price):
    """Determine ticket tier from price."""
    if price > 500:
        tier = "vip"
    else:
        if price > 200:
            tier = "premium"
        else:
            if price > 50:
                tier = "standard"
            else:
                tier = "economy"
    return tier


# --- PLR1714: repeated equality comparisons (use `in`) ---
def is_food_event(event_type):
    """Check if the event is food-related."""
    if event_type == "cooking" or event_type == "tasting" or event_type == "food_festival":
        return True
    return False


# --- PLW2901: redefined loop variable ---
def flatten_attendee_groups(groups):
    """Flatten nested attendee groups into a single list."""
    result = []
    for group in groups:
        for group in group.get("members", []):
            result.append(group)
    return result


# --- PLW0120: else clause on loop without break ---
def find_premium_event(events):
    """Find the first premium event."""
    for event in events:
        if event.get("tier") == "premium":
            return event
    else:
        return None


# --- PLW0603: using the global statement ---
_analytics_cache = {}


def reset_analytics_cache():
    """Reset the global analytics cache."""
    global _analytics_cache
    _analytics_cache = {}


# --- Combination: multiple issues in one function ---
def process_event_batch(events, batch_id, processor, logger, config, db_conn, cache_client, dry_run):
    """Process a batch of events with various issues."""
    l = []
    for event in events:
        if event == None:
            continue
        if event.get("valid") == True:
            try:
                parsed = datetime.strptime(event["date"], "%Y-%m-%d")
                l.append({"event": event, "parsed": parsed})
            except:
                l.append({"event": event, "error": True})
    for item in l:
        for item in item.get("sub_events", []):
            pass
    return l
