from elasticsearch import Elasticsearch


es = Elasticsearch('http://localhost:9200')

mapping = {
  "mappings": {
    "properties": {
      "ticket_id": {"type": "long"},
      "created_at": {
        "type": "date",
        "format": "strict_date_time"
      },
      "resolved_at": {
        "type": "date",
        "format": "strict_date_time"
      },
      "assigned_technician": { "type": "keyword" },
      "severity": {"type": "keyword"},
      "priority": {"type": "keyword"},
      "status": {"type": "keyword"},
      "category": {"type": "keyword"},
      "drone_type": {"type": "keyword"},
      "issue_description": {"type": "text"},
      "tags": {"type": "keyword"},
      "ticket_source": {"type": "keyword"},
      "ticket_opened_by": {"type": "text"},
      "urgency": {"type": "keyword"},
      "escalated": {"type": "boolean"},
      "date_assigned": {
        "type": "date",
        "format": "strict_date_time"
      },
      "time_to_first_response_hours": {"type": "float"},
      "technician_notes": {"type": "text"},
      "resolution_time_hours": {"type": "float"},
      "response_time_hours": {"type": "float"}
    }
  }
}

es.indices.create(index="support_tickets", body=mapping )