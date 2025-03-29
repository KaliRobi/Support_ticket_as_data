from elasticsearch import Elasticsearch
import pandas as pd

PASS = '3q3B5bB-27ndRS6RF6oz'

es = Elasticsearch("http://localhost:9200")

role_definition = {
    "cluster": ["all"],
    "index": [
        {
            "names": ["support_tickets"],
            "privileges": ["read"],
            "query": {
                "term": {
                    "user_id": "{{username}}"
                }
            }
        }
    ]
}

kibana_role_def = {
    "cluster": ["all"],
    "index": [{
        "name": ["support_tickets"],
        "privileges":  ["read"],
        "query": {
            "term": {
                "user_id": "{{username}}"
            }
        }
    }],
    "kibana":[{
        "feature": {
                "dashboard": ["read"]
        },
        "spaces": ["*"]
    }]
}

users_list = pd.read_json('users.json', orient='records')



def create_users(user_list):
    for _, row in user_list.iterrows():
        es.security.put_user(
                password = row["password"],
                roles = row["roles"],
                username = row["full_name"],
                email = row["email"]
        )
        
                


def create_roles():  
    try:
        es.security.put_role(name="user_dashboard_role", body=role_definition )
    except Exception as e:
        print(f'{e}')


    try:    
        es.security.put_role(name="kibana_user_dashboard", body= kibana_role_def) 
    except Exception as e:
        print(f'{e}')

create_roles()
create_users(users_list)



