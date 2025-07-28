from datetime import datetime, timedelta
from dateutil import parser
import re


def convert_to_common_format(date_input):

    if isinstance(date_input, (int, float)):
        dt = datetime.fromtimestamp(date_input)
    elif isinstance(date_input, datetime):
        dt = date_input
    elif isinstance(date_input, str):
        # Handle relative date strings like "Posted 2 Days Ago", "3 hours ago", "30+ Days Ago"
        rel_match = re.search(
            r'(\d+)\+?\s*(day|hour|minute|second|week|month|year)s?\s*ago', date_input, re.IGNORECASE)
        if rel_match:
            amount = int(rel_match.group(1))
            unit = rel_match.group(2).lower()
            now = datetime.now()
            if unit == "day":
                dt = now - timedelta(days=amount)
            elif unit == "hour":
                dt = now - timedelta(hours=amount)
            elif unit == "minute":
                dt = now - timedelta(minutes=amount)
            elif unit == "second":
                dt = now - timedelta(seconds=amount)
            elif unit == "week":
                dt = now - timedelta(weeks=amount)
            elif unit == "month":
                # Approximate a month as 30 days
                dt = now - timedelta(days=amount*30)
            elif unit == "year":
                # Approximate a year as 365 days
                dt = now - timedelta(days=amount*365)
            else:
                return None
        else:
            try:
                dt = parser.parse(date_input)
            except Exception:
                return None
    else:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')
