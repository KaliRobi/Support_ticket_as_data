from elasticsearch import Elasticsearch


es = Elasticsearch('http://localhost:9200')

tickets_mapping = {
  "mappings": {
    "properties": {
      "ticket_id": {"type": "long"},
      "created_at": {
        "type": "date",
        "format": "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
      },
      "resolved_at": {
        "type": "date",
        "format": "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
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
        "format": "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
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
def create_index(name, body):
    es.indices.create(index=name, body=body)  




def delete_index(index_name):
  es.indices.delete(index=index_name)


#delete_index("support_tickets") 
#delete_index("user_index")
create_index(name="support_tickets", body=tickets_mapping)
#create_index(name="user_index", body=users_mapping)