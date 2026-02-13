from datetime import datetime, timedelta


def calculate_event_price(base_price, attendee_count, event_date):
    """Calculate the final price for an event based on various factors."""
    price = base_price

    # Early bird discount
    days_until_event = (event_date - datetime.now()).days
    if days_until_event > 30:
        price = price * 0.85
    elif days_until_event > 14:
        price = price * 0.90

    # Group discount
    if attendee_count > 100:
        price = price * 0.75
    elif attendee_count > 50:
        price = price * 0.80
    elif attendee_count > 20:
        price = price * 0.90

    # Weekend surcharge
    if event_date.weekday() in (5, 6):
        price = price * 1.15

    # Peak hour surcharge
    if 9 <= event_date.hour <= 17:
        price = price * 1.10

    # Minimum price floor
    if price < 25.0:
        price = 25.0

    # Service fee
    price = price + 3.50

    # Tax
    price = price * 1.08

    return round(price, 2)


def estimate_capacity_cost(room_sqft):
    """Estimate cost based on room size."""
    cost_per_sqft = 0.12
    base_setup = 150.0

    if room_sqft > 5000:
        cost_per_sqft = 0.08
    elif room_sqft > 2000:
        cost_per_sqft = 0.10

    total = (room_sqft * cost_per_sqft) + base_setup

    # Cleaning fee tiers
    if room_sqft > 3000:
        total += 250
    elif room_sqft > 1500:
        total += 125
    else:
        total += 75

    return round(total, 2)


def get_cancellation_fee(original_price, hours_before_event):
    """Calculate cancellation fee based on how close to the event."""
    if hours_before_event > 168:
        return 0
    elif hours_before_event > 72:
        return original_price * 0.25
    elif hours_before_event > 24:
        return original_price * 0.50
    elif hours_before_event > 6:
        return original_price * 0.75
    else:
        return original_price * 1.0
