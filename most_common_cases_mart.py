from io import StringIO
from elasticsearch import Elasticsearch
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator


es = Elasticsearch('http://localhost:9200')


query_result = es.esql.query( 
    query= "FROM support_tickets",
    format="csv"
)

tickets = pd.read_csv(StringIO(query_result.body))
sm = pd.DataFrame()
ks = pd.DataFrame()
resolution_pre_eng = pd.DataFrame()


tickets = tickets[['created_at', 'date_assigned', 'resolved_at',  'category',  'assigned_technician'] ]

tickets = tickets.dropna()


tickets['time_to_resolve'] = (( pd.to_datetime(tickets['resolved_at']) - pd.to_datetime(tickets['created_at'])).dt.total_seconds() /60 /60)


resolution_pre_eng =  tickets[['time_to_resolve', 'category']].groupby('category').mean().sort_values('time_to_resolve', ascending=False)

print(resolution_pre_eng)

sm = tickets[['time_to_resolve', 'assigned_technician', 'category']].groupby([  'assigned_technician', 'category']).mean().round(2).sort_values('assigned_technician', ascending=False)

sm_pivoted = sm.unstack('assigned_technician')

category_avg = resolution_pre_eng.rename(columns={'time_to_resolve': 'team_ave'})
sm_pivoted.columns = sm_pivoted.columns.get_level_values(1)

sm_pivoted['Team Average'] = resolution_pre_eng['time_to_resolve'].round(2)
sm_pivoted = sm_pivoted.fillna('-')


print(sm_pivoted)
# time and categories 






# histogram, weekly resolution

#ticket tags per user per week

# resolution time per user per ticket by tag by 