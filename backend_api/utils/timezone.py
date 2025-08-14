from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

def to_ist(dt: datetime):
    if dt is None:
        return None
    if dt.tzinfo is None:  # Assume UTC if no timezone
        dt = dt.replace(tzinfo=pytz.UTC)
    return dt.astimezone(IST)
