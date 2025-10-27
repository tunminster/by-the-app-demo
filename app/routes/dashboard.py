from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor
from app.utils.db import conn

dashboard_router = APIRouter()

# Helper function to get authenticated user (assuming you have this)
async def get_current_user():
    # For now, returning None to allow public access
    # In production, add authentication dependency
    return None

@dashboard_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """
    Get dashboard statistics
    Returns: Stats for today's appointments, total patients, pending appointments, and revenue
    """
    try:
        today = date.today()
        
        # 1. Today's Appointments
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT COUNT(*) as count
                FROM appointments
                WHERE appointment_date = %s
            """, (today,))
            today_appointments = cur.fetchone()['count'] or 0
            
            # 2. Total Patients
            cur.execute("""
                SELECT COUNT(*) as count
                FROM patients
            """)
            total_patients = cur.fetchone()['count'] or 0
            
            # 3. Pending Appointments (status = 'pending' or status = 'confirmed' but not completed)
            cur.execute("""
                SELECT COUNT(*) as count
                FROM appointments
                WHERE status = 'pending' OR (status = 'confirmed' AND appointment_date >= %s)
            """, (today,))
            pending_appointments = cur.fetchone()['count'] or 0
            
            # 4. Revenue This Month (assuming appointments have a cost field or estimating)
            # For now, we'll calculate based on appointments count
            # You may need to add a cost/price field to the appointments table
            cur.execute("""
                SELECT COUNT(*) * 100 as estimated_revenue
                FROM appointments
                WHERE EXTRACT(MONTH FROM appointment_date) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM appointment_date) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            revenue_data = cur.fetchone()
            revenue = revenue_data['estimated_revenue'] if revenue_data else 0
        
        # Calculate changes (simplified - in production, you'd compare with previous period)
        stats = [
            {
                "name": "Today's Appointments",
                "value": str(today_appointments),
                "change": "+2",  # Placeholder - calculate from historical data
                "changeType": "positive"
            },
            {
                "name": "Total Patients",
                "value": f"{total_patients:,}",
                "change": "+5.4%",  # Placeholder
                "changeType": "positive"
            },
            {
                "name": "Pending Appointments",
                "value": str(pending_appointments),
                "change": "-12%",  # Placeholder
                "changeType": "negative"
            },
            {
                "name": "Revenue This Month",
                "value": f"${revenue:,}",
                "change": "+8.2%",  # Placeholder
                "changeType": "positive"
            }
        ]
        
        return {"stats": stats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard stats: {str(e)}")

@dashboard_router.get("/dashboard/appointments/today")
async def get_today_appointments(current_user: dict = Depends(get_current_user)):
    """
    Get today's appointments
    Returns: List of appointments scheduled for today
    """
    try:
        today = date.today()
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    a.id,
                    a.patient,
                    a.appointment_time as time,
                    a.treatment,
                    COALESCE(a.status, 'confirmed') as status,
                    d.name as dentist_name
                FROM appointments a
                LEFT JOIN dentists d ON a.dentist_id = d.id
                WHERE a.appointment_date = %s
                ORDER BY a.appointment_time
            """, (today,))
            
            appointments = cur.fetchall()
        
        # Format appointments to match frontend requirements
        formatted_appointments = []
        for apt in appointments:
            # Format time from HH:MM to 12-hour format
            time_str = apt['time']
            if time_str:
                try:
                    # Parse time and convert to 12-hour format
                    hour, minute = map(int, time_str.split(':'))
                    if hour == 0:
                        formatted_time = f"12:{minute:02d} AM"
                    elif hour < 12:
                        formatted_time = f"{hour}:{minute:02d} AM"
                    elif hour == 12:
                        formatted_time = f"12:{minute:02d} PM"
                    else:
                        formatted_time = f"{hour - 12}:{minute:02d} PM"
                except:
                    formatted_time = time_str
            else:
                formatted_time = "N/A"
            
            formatted_appointments.append({
                "id": apt['id'],
                "patient": apt['patient'],
                "time": formatted_time,
                "treatment": apt['treatment'],
                "status": apt['status']
            })
        
        return {"appointments": formatted_appointments}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching today's appointments: {str(e)}")
