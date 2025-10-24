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
                   a.date, a.start_time, a.end_time
            FROM availability a
            JOIN dentists d ON a.dentist_id = d.id
            WHERE a.is_booked = FALSE
            ORDER BY a.date, a.start_time
            LIMIT %s
        """, (limit,))
        return cur.fetchall()

def mark_slot_booked(dentist_id, date, time):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE availability
            SET is_booked = TRUE
            WHERE dentist_id=%s AND date=%s AND start_time=%s
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

