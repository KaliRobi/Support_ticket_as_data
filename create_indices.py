from elasticsearch import Elasticsearch


es = Elasticsearch('http://localhost:9200')

tickets_mapping = {
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


users_mapping = {
    "mappings": {
      "properties":{
        "id":  {"type" : "keyword"},
        "roles": {"type": "text"},
        "password" :  {"type" : "text"},
        "full_name": {"type" : "keyword"},
        "email": {"type": "text"}
      }
    }
}


def create_ticket_index():
  es.indices.create(index="support_tickets", body=tickets_mapping  )


def create_user_index():
  es.indices.create(index="user_index", body=users_mapping )


create_user_index()