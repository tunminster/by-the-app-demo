# db.py
import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

conn_str = (
    f"DRIVER={{{os.getenv('AZURE_SQL_DRIVER')}}};"
    f"SERVER={os.getenv('AZURE_SQL_SERVER')};"
    f"DATABASE={os.getenv('AZURE_SQL_DATABASE')};"
    f"UID={os.getenv('AZURE_SQL_USERNAME')};"
    f"PWD={os.getenv('AZURE_SQL_PASSWORD')};"
    f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)

conn = pyodbc.connect(conn_str)

def fetch_available_slots(limit: int = 5):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT TOP (?) d.id, d.name, a.date, a.start_time, a.end_time
            FROM Availability a
            JOIN Dentists d ON a.dentist_id = d.id
            WHERE a.is_booked = 0
            ORDER BY a.date, a.start_time
        """, (limit,))
        rows = cur.fetchall()
        return [
            {
                "dentist_id": r[0],
                "dentist_name": r[1],
                "date": r[2],
                "start_time": str(r[3]),
                "end_time": str(r[4])
            } for r in rows
        ]

def mark_slot_booked(dentist_id: int, date: str, time: str):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE Availability
            SET is_booked = 1
            WHERE dentist_id = ? AND date = ? AND start_time = ?
        """, (dentist_id, date, time))
        conn.commit()

def insert_appointment(dentist_id: int, patient_name: str, date: str, time: str):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO Appointments (dentist_id, patient_name, appointment_date, appointment_time)
            VALUES (?, ?, ?, ?)
        """, (dentist_id, patient_name, date, time))
        conn.commit()
