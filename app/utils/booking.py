# booking.py
from typing import Optional, List, Dict
from app.utils.db import fetch_available_slots, mark_slot_booked, insert_appointment

def build_context_text(slots: List[Dict]) -> str:
    # Convert slot records into human-readable lines
    lines = []
    for s in slots:
        lines.append(
            f"{s['dentist_name']} on {s['date']} at {s['start_time']}–{s['end_time']}"
        )
    return "\n".join(lines)

def parse_booking_intent(reply_text: str) -> Optional[Dict]:
    """
    Rudimentary parsing: from AIs reply, extract dentist, date, time, name.
    In practice, you'd use a small LLM or regex/grammar to parse reliably.
    Returns something like:
      { "dentist": "Dr. Smith", "date": "2025-10-20", "time": "10:00:00", "patient_name": "Alice" }
    Or None if unclear.
    """
    # Very naive example:
    # You might prompt GPT itself to generate a JSON with keys dentist, date, time, name.
    # For demo, assume reply is: "I book you with Dr. Smith on 2025-10-20 at 10:00 for Alice."
    import re
    pattern = r"Dr\.?\s*([A-Za-z]+).*on\s*([0-9]{4}-[0-9]{2}-[0-9]{2}).*at\s*([0-9]{1,2}:[0-9]{2}).*for\s*(\w+)"
    m = re.search(pattern, reply_text)
    if m:
        return {
            "dentist": "Dr. " + m.group(1),
            "date": m.group(2),
            "time": m.group(3),
            "patient_name": m.group(4),
        }
    return None

def book_if_possible(intent: Dict) -> bool:
    """
    Try to book; return True if successful, False otherwise.
    """
    # First find dentist_id matching name (you’d likely want a mapping)
    # For simplicity, assume you do a lookup in DB:
    # (You could extend db.py to get dentist_id by name)
    from db import conn
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM dentists WHERE name = %s", (intent["dentist"],))
        res = cur.fetchone()
        if not res:
            return False
        dentist_id = res[0]
    # Mark slot booked
    mark_slot_booked(dentist_id, intent["date"], intent["time"])
    insert_appointment(dentist_id, intent["patient_name"], intent["date"], intent["time"])
    return True
