# Dashboard Endpoints

## Overview

Two new dashboard endpoints have been added to provide statistics and today's appointments data.

## Endpoints

### 1. Get Dashboard Statistics

**Endpoint:** `GET /api/dashboard/stats`

**Description:** Returns dashboard statistics including today's appointments, total patients, pending appointments, and monthly revenue.

**Response Format:**
```json
{
  "stats": [
    {
      "name": "Today's Appointments",
      "value": "12",
      "change": "+2",
      "changeType": "positive"
    },
    {
      "name": "Total Patients",
      "value": "1,234",
      "change": "+5.4%",
      "changeType": "positive"
    },
    {
      "name": "Pending Appointments",
      "value": "8",
      "change": "-12%",
      "changeType": "negative"
    },
    {
      "name": "Revenue This Month",
      "value": "$12,450",
      "change": "+8.2%",
      "changeType": "positive"
    }
  ]
}
```

**Data Sources:**
- **Today's Appointments:** Counts appointments scheduled for today
- **Total Patients:** Counts all patients in the database
- **Pending Appointments:** Counts appointments with status 'pending' or 'confirmed' and not yet completed
- **Revenue This Month:** Calculates estimated revenue based on monthly appointments (currently estimating $100 per appointment)

### 2. Get Today's Appointments

**Endpoint:** `GET /api/dashboard/appointments/today`

**Description:** Returns all appointments scheduled for today, ordered by time.

**Response Format:**
```json
{
  "appointments": [
    {
      "id": 1,
      "patient": "John Smith",
      "time": "9:00 AM",
      "treatment": "Cleaning",
      "status": "confirmed"
    },
    {
      "id": 2,
      "patient": "Sarah Johnson",
      "time": "10:30 AM",
      "treatment": "Checkup",
      "status": "confirmed"
    },
    {
      "id": 3,
      "patient": "Mike Davis",
      "time": "2:00 PM",
      "treatment": "Filling",
      "status": "pending"
    },
    {
      "id": 4,
      "patient": "Emily Wilson",
      "time": "3:30 PM",
      "treatment": "Extraction",
      "status": "confirmed"
    }
  ]
}
```

**Features:**
- ✅ Time formatted in 12-hour format (e.g., "9:00 AM")
- ✅ Ordered by appointment time
- ✅ Includes patient name, treatment, and status

## Database Schema

The endpoints query the following tables:

### Appointments Table
```sql
appointments
├── id (INTEGER)
├── dentist_id (INTEGER)
├── patient (TEXT)
├── phone (TEXT)
├── appointment_date (DATE)
├── appointment_time (TIME)
├── treatment (TEXT)
└── status (TEXT)
```

### Patients Table
```sql
patients
├── id (INTEGER)
├── name (TEXT)
├── email (TEXT)
├── phone (TEXT)
└── date_of_birth (DATE)
```

## Usage Examples

### cURL

**Get Dashboard Stats:**
```bash
curl http://localhost:8080/api/dashboard/stats
```

**Get Today's Appointments:**
```bash
curl http://localhost:8080/api/dashboard/appointments/today
```

### JavaScript (Frontend)

```javascript
// Fetch dashboard stats
async function getDashboardStats() {
  const response = await fetch('http://localhost:8080/api/dashboard/stats');
  const data = await response.json();
  return data.stats;
}

// Fetch today's appointments
async function getTodayAppointments() {
  const response = await fetch('http://localhost:8080/api/dashboard/appointments/today');
  const data = await response.json();
  return data.appointments;
}

// Usage
const stats = await getDashboardStats();
const appointments = await getTodayAppointments();

console.log('Stats:', stats);
console.log('Appointments:', appointments);
```

### Python

```python
import requests

# Get dashboard stats
response = requests.get('http://localhost:8080/api/dashboard/stats')
stats = response.json()['stats']

# Get today's appointments
response = requests.get('http://localhost:8080/api/dashboard/appointments/today')
appointments = response.json()['appointments']

print('Stats:', stats)
print('Appointments:', appointments)
```

## Testing

Run the test script:

```bash
python test_dashboard_endpoints.py
```

This will:
1. Test the `/api/dashboard/stats` endpoint
2. Test the `/api/dashboard/appointments/today` endpoint
3. Validate the response structure
4. Display the results

## Customization

### Modify Change Calculations

Currently, the `change` values are placeholders. To calculate real changes:

```python
# In app/routes/dashboard.py
# Calculate change from previous period
def calculate_change(current, previous):
    if previous == 0:
        return "+100%"
    change = ((current - previous) / previous) * 100
    return f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
```

### Add Revenue Calculation

To add real revenue calculation:

1. Add a `cost` field to the `appointments` table
2. Update the revenue query in `dashboard.py`:
```python
cur.execute("""
    SELECT SUM(cost) as revenue
    FROM appointments
    WHERE EXTRACT(MONTH FROM appointment_date) = EXTRACT(MONTH FROM CURRENT_DATE)
    AND EXTRACT(YEAR FROM appointment_date) = EXTRACT(YEAR FROM CURRENT_DATE)
""")
```

## Notes

- ⚠️ Currently no authentication required (public endpoints)
- 💡 Consider adding authentication in production
- 📊 Change calculations are placeholder values
- 💰 Revenue estimation is currently $100 per appointment (customize as needed)
- 🕒 Time is formatted in 12-hour format automatically
