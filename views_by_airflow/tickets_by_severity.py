import pandas as pd
from io import StringIO
from airflow import DAG
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch, helpers
from airflow.operators.python import PythonOperator
from failure_notify import notify_personel

#5. Tickets by Severity

es = Elasticsearch(hosts=['http://localhost:9200'])

default_parameters = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(hours=1),
    'start_date': datetime(2025, 3, 1)
}


with DAG(
        'tickets-by-severity',
        default_args=default_parameters,
        schedule='06 0 * * 1',
        tags=['support_tickets'],
        description='to understand the severity distribution over time'

) as tickets_by_severity_dag:
    
    def extract_ticket(**kwargs):
        ti = kwargs['ti']
        query_result = es.esql.query(
            query="FROM support_tickets",
            format='csv'
        )

        tickets = pd.read_csv(StringIO(query_result.body))
        tickets_file_path = 'tmp/extracted_tickets.csv'
        tickets.to_csv(tickets_file_path)

        ti.xcom_push(
            key="tickets_file_path",
            value=tickets_file_path
        )
    
    extract_ticket_task = PythonOperator(
        task_id="extract_ticket_task",
        python_callable=extract_ticket,
        dag=tickets_by_severity_dag,
        on_failure_callback=notify_personel
    )


    def build_histogram_mart(**kwargs):
        ti = kwargs['ti']

        temp_file_path = ti.xcom_pull(
            task_ids= 'extract_ticket_task',
            key='tickets_file_path'
        )
        tickets = pd.read_csv(temp_file_path)

        sev_per_cat_histogram  = pd.DataFrame()

        tickets =  tickets[['severity', 'category', 'created_at']]
        tickets['created_at'] = pd.to_datetime(tickets['created_at'], format='mixed').dt.strftime('%Y-%m-%d')
        #get amount of prios per daycategory

        sev_per_cat_histogram = (tickets.groupby(['created_at', 'category', 'severity'])['severity']
                                        .count()    
                                        .reset_index(name='count')
                                        .set_index('created_at'))
        
        mart_csv_path = '/tmp/mart_csv_path.csv'
        sev_per_cat_histogram.to_csv(mart_csv_path)

        ti.xcom_push(
                key='mart_csv_path',
                value=mart_csv_path    
                     )
        
    build_histogram_mart = PythonOperator(
            task_id ='build_histogram_mart',
            python_callable=build_histogram_mart,
            dag=tickets_by_severity_dag,
            on_failure_callback=notify_personel
            )

    def load_mart_to_elastic(**kwargs):
        ti = kwargs['ti']

        mart_csv_path = ti.xcom_pull(
            task_ids='build_histogram_mart',
            key='mart_csv_path',
        )

        tickets_by_severity_mart = pd.read_csv(mart_csv_path)

        documets = [
                {
                   '_index': 'tickets_by_severity',  
                    '_source': record
                }

        for record in tickets_by_severity_mart.to_dict(orient="records")
        ]

    
        helpers.bulk(es, documets)

    load_mart_to_elastic = PythonOperator(
        task_id = 'load_mart_to_elastic',
        python_callable=load_mart_to_elastic,
        dag=tickets_by_severity_dag,
        on_failure_callback=notify_personel
    )

extract_ticket_task >>  build_histogram_mart >> load_mart_to_elastic