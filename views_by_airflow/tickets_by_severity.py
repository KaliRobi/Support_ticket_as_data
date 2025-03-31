import pandas as pd
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.providers.elasticsearch.hooks.elasticsearch import ElasticsearchHook

#5. Tickets by Severity



#    X-axis: severity

#    Y-axis: Count of tickets

#    Insight: Shows which severity levels are most common and if there are trends over time.
