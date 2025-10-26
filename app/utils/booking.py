# booking.py
from typing import Optional, List, Dict
from app.utils.db import (
    fetch_available_slots, 
    mark_slot_booked, 
    insert_appointment,
    fetch_dentist_by_name,
    update_time_slot_availability
)
import openai
import os
import json

def get_dentist_names():
    """
    Get list of dentist names from database.
    """
    from app.utils.db import fetch_dentists
    dentists = fetch_dentists()
    return [dentist["name"] for dentist in dentists]

# Get dentist names dynamically
DENTISTS = get_dentist_names()
openai.api_key = os.environ.get('OPENAI_API_KEY')

def build_context_text(slots: List[Dict]) -> str:
    # Convert slot records into human-readable lines
    lines = []
    for s in slots:
        time_slot = s.get('time_slot', {})
        start_time = time_slot.get('start', 'N/A')
        end_time = time_slot.get('end', 'N/A')
        lines.append(
            f"{s['dentist_name']} on {s['date']} at {start_time}–{end_time}"
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
    # Find dentist by name
    dentist = fetch_dentist_by_name(intent["dentist"])
    if not dentist:
        print(f"Dentist {intent['dentist']} not found")
        return False
    
    dentist_id = dentist["id"]
    
    # Update time slot availability to false (booked)
    success = update_time_slot_availability(
        dentist_id, 
        intent["date"], 
        intent["time"], 
        available=False
    )
    
    if not success:
        print(f"Failed to book slot for {intent['dentist']} on {intent['date']} at {intent['time']}")
        return False
    
    # Insert appointment with phone and treatment
    phone = intent.get("phone", "N/A")
    treatment = intent.get("treatment", "General Checkup")
    insert_appointment(
        dentist_id, 
        intent["patient_name"], 
        intent["date"], 
        intent["time"],
        phone=phone,
        treatment=treatment
    )
    print(f"Successfully booked appointment for {intent['patient_name']} with {intent['dentist']}")
    return True

async def parse_booking_intent_ai(reply_text: str) -> Optional[Dict]:
    """
    Use LLM to parse patient reply into structured booking info.
    Fallback to first available slot if date/time missing.
    """
    #available_slots = fetch_available_slots(limit=5)
    available_slots = []
    
    # Get current dentist names
    current_dentists = get_dentist_names()
    
    prompt = f"""
        You are a dental receptionist assistant.
        Extract structured JSON information from the patient's message.

        Patient message:
        \"\"\"{reply_text}\"\"\"

        Return JSON with keys:
        - dentist: one of {current_dentists} or null
        - date: YYYY-MM-DD or null
        - time: HH:MM or null
        - patient_name: null if not mentioned

        Only respond with valid JSON.
        """
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
    except Exception as e:
        print("LLM parsing error:", e)
        return None

    # Fallback: assign first available slot if missing
    if available_slots and data.get("dentist"):
        slots = available_slots.get(data["dentist"], [])
        if slots:
            if not data.get("date") or not data.get("time"):
                first_slot = slots[0]
                data["date"] = data.get("date") or first_slot["date"]
                time_slot = first_slot.get('time_slot', {})
                data["time"] = data.get("time") or time_slot.get("start", "09:00")

    if data.get("dentist") and data.get("patient_name"):
        print(" save: ", data)
        return data
    return None