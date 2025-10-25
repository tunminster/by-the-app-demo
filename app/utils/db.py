import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT", 5432)
)
conn.autocommit = True

def fetch_available_slots(limit=5):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT d.id AS dentist_id, d.name AS dentist_name,
                   a.date, 
                   jsonb_array_elements(a.time_slots) as time_slot
            FROM availability a
            JOIN dentists d ON a.dentist_id = d.id
            WHERE (jsonb_array_elements(a.time_slots)->>'available')::boolean = true
            ORDER BY a.date, (jsonb_array_elements(a.time_slots)->>'start')
            LIMIT %s
        """, (limit,))
        return cur.fetchall()

def mark_slot_booked(dentist_id, date, time):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE availability
            SET time_slots = jsonb_set(
                time_slots,
                array[jsonb_array_length(time_slots)::text],
                jsonb_set(
                    jsonb_array_elements(time_slots),
                    '{available}',
                    'false'::jsonb
                )
            )
            WHERE dentist_id=%s AND date=%s 
            AND jsonb_array_elements(time_slots)->>'start' = %s
        """, (dentist_id, date, time))

def insert_appointment(dentist_id, patient_name, date, time):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO appointments (dentist_id, patient_name, appointment_date, appointment_time)
            VALUES (%s, %s, %s, %s)
        """, (dentist_id, patient_name, date, time))

def fetch_dentists():
    """
    Returns all dentists with their names and IDs.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, name, specialty FROM dentists ORDER BY name")
        return cur.fetchall()

def fetch_dentist_by_name(name):
    """
    Get dentist by name for booking purposes.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, name, specialty FROM dentists WHERE name = %s", (name,))
        return cur.fetchone()

def get_availability_by_dentist_and_date(dentist_id, date):
    """
    Get availability for a specific dentist on a specific date.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT * FROM availability 
            WHERE dentist_id = %s AND date = %s
        """, (dentist_id, date))
        return cur.fetchone()

def update_time_slot_availability(dentist_id, date, time_slot_start, available=False):
    """
    Update a specific time slot availability.
    """
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE availability 
            SET time_slots = (
                SELECT jsonb_agg(
                    CASE 
                        WHEN slot->>'start' = %s 
                        THEN jsonb_set(slot, '{available}', %s::jsonb)
                        ELSE slot 
                    END
                )
                FROM jsonb_array_elements(time_slots) as slot
            )
            WHERE dentist_id = %s AND date = %s
        """, (time_slot_start, str(available).lower(), dentist_id, date))
        return cur.rowcount > 0

