import random
import json
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

# Sample data (Technicians, Drone Models, Categories, etc.)
technicians = ["Jaanus", "Kati", "Markus", "Siim", "Anna", "Maire", "Rainer", "Pille", "Erki"]
ticket_sources = ["Email", "Phone", "Web Portal"]
drone_types = ["Parrot Anafi", "Delair UX11",  "WingtraOne GEN II", "Flyability Elios 3", "Quantum Trinity F90+", "QuestUAV Q-Pod Lite", "Hexagon MA560"]
technical_categories = ["Flight Control System", "GPS Signal", "Battery Charging", "Firmware Update", "Camera", "Motors", "Propellers", "Calibration"]
severity_levels = ["Low", "Medium", "High"]
priority_levels = ["Low", "Medium", "High"]
statuses = ["Open", "In Progress", "Closed"]
issues = [
    "Drone unresponsive during flight, suspected issue with the flight control system.",
    "Battery fails to charge properly.",
    "GPS signal lost in flight, unable to return home.",
    "Calibration failed during pre-flight check.",
    "Firmware update error, update process incomplete.",
    "Camera malfunction, unable to capture images.",
    "Motor failure detected, abnormal vibration during flight.",
    "Propellers damaged during takeoff, need replacement."
]

def generate_ticket():
    ticket_id = random.randint(1000, 999999999)
    created_at = datetime.now() - timedelta(days=random.randint(0, 30))  
    resolved_at = created_at + timedelta(hours=random.randint(1, 72)) if random.choice([True, False]) else None
    assigned_technician = random.choice(technicians)
    severity = random.choice(severity_levels)
    priority = random.choice(priority_levels)
    status = random.choice(statuses)
    technical_category = random.choice(technical_categories)
    drone_type = random.choice(drone_types)
    issue_description = random.choice(issues)
    ticket_source = random.choice(ticket_sources)
    ticket_opened_by = f"{random.choice(technicians)} {random.choice(technicians)}"
    
    # Random urgency: set urgency based on severity (high severity often means higher urgency)
    urgency = "High" if severity in ["High", "Medium"] else "Low"
    
    # Random escalation flag
    escalated = random.choice([True, False])
    
    # Date and time of assignment
    date_assigned = created_at + timedelta(hours=random.randint(1, 24)) if resolved_at else created_at
    
    # Response time in hours (time to first response)
    time_to_first_response_hours = (date_assigned - created_at).total_seconds() / 3600

    # Technician's notes (simulating some realistic troubleshooting and resolution)
    technician_notes = f"Initial analysis indicates a possible issue with {technical_category.lower()}."

    # Calculate resolution time if resolved
    resolution_time = None
    if resolved_at:
        resolution_time = (resolved_at - created_at).total_seconds() / 3600  # in hours
    
    ticket_data = {
        "ticket_id": ticket_id,
        "created_at": created_at.isoformat(),
        "resolved_at": resolved_at.isoformat() if resolved_at else None,
        "assigned_technician": assigned_technician,
        "severity": severity,
        "priority": priority,
        "status": status,
        "category": technical_category,
        "drone_type": drone_type,
        "issue_description": issue_description,
        "tags": [technical_category, "Drone", drone_type],
        "ticket_source": ticket_source,
        "ticket_opened_by": ticket_opened_by,
        "urgency": urgency,
        "escalated": escalated,
        "date_assigned": date_assigned.isoformat(),
        "time_to_first_response_hours": round(time_to_first_response_hours, 2),
        "technician_notes": technician_notes,
        "resolution_time_hours": resolution_time,
        "response_time_hours": round(time_to_first_response_hours, 2)
    }

    return ticket_data

class TicketHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            ticket_count = random.randint(3, 12)  
            tickets = [generate_ticket() for _ in range(ticket_count)]
            response = json.dumps(tickets, indent=4)

            # Send response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=TicketHandler, port=55555):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting HTTP server on port {port}...")
    httpd.serve_forever()

# Entry point to start the server
if __name__ == '__main__':
    run(port=55555)
