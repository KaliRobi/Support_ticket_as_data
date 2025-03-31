from io import StringIO
from elasticsearch import Elasticsearch, helpers   
import pandas as pd
import logging
from airflow import DAG
from airflow.exceptions import AirflowFailException
from datetime import timedelta, datetime
from airflow.operators.python import PythonOperator
from airflow.providers.elasticsearch.hooks.elasticsearch import ElasticsearchHook


es_hook = ElasticsearchHook(elasticsearch_conn_id="elasticsearch_default")
es_client = es_hook.get_conn()

default_arguments = {
    'owner': 'airflow',
    'retries':1,
    'retry_delay': timedelta(hours=24),
    'start_date' : datetime(2025, 1, 1)
}

with DAG(
    'most-common-cases',
    default_args=default_arguments,
    schedule='06 0 * * 1',
    tags=['support_tickets', 'performance'],
    catchup=False,
    description= 'metrics to see teamates compared to avearges'
) as common_cases_dag:
    
    def extract_tickets(**kwargs):
        query_result = es_client.esql.query( 
            query= "FROM support_tickets",
            format="csv"
        )
        
        if not query_result.body.strip():
            raise AirflowFailException("ES|QL query returned empty results")

        tickets = pd.read_csv(StringIO(query_result.body))
        extract_path = '/tmp/tickets_data.csv'
        tickets.to_csv(extract_path, index=False)
        kwargs['ti'].xcom_push(key='tickets_data', value=extract_path)
        

    extract_tickets_task = PythonOperator(
        task_id = 'extract_tickets_task',
        python_callable=extract_tickets,
        dag=common_cases_dag,
        on_failure_callback= lambda context: logging.error(
        f'data extract failed, extract_tickets_task')

    )

    def find_team_averages(**kwargs):
        ti = kwargs['ti']

        tmp_extract_path = ti.xcom_pull(
            task_id = 'extract_tickets_task',
            key='tickets_data'

        )
        #get the data from the csv
        tickets = pd.read_csv(tmp_extract_path)
        tickets = tickets[['created_at', 'date_assigned', 'resolved_at',  'category',  'assigned_technician'] ]

        #eliminating unusable data
        tickets = tickets.dropna()

        tickets['time_to_resolve'] = (( pd.to_datetime(tickets['resolved_at']) - pd.to_datetime(tickets['created_at'])).dt.total_seconds() /60 /60)
        
        resolution_pre_eng = pd.DataFrame()
        resolution_pre_eng =  tickets[['time_to_resolve', 'category']].groupby('category').mean().sort_values('time_to_resolve', ascending=False)  
        
        sm = pd.DataFrame()
        sm = tickets[['time_to_resolve', 'assigned_technician', 'category']].groupby([  'assigned_technician', 'category']).mean().round(2).sort_values('assigned_technician', ascending=False)

        sm_pivoted = sm.unstack('assigned_technician')

        resolution_pre_eng.rename(columns={'time_to_resolve': 'team_ave'}, inplace=True)
        sm_pivoted.columns = sm_pivoted.columns.get_level_values(1)

        sm_pivoted['Team Average'] = resolution_pre_eng['time_to_resolve'].round(2)
        sm_pivoted = sm_pivoted.fillna('-')

        result_mart_path = '/tmp/common_cases_result_mart.csv'

        sm_pivoted.to_csv(result_mart_path)

        ti.xcom_push(key='team_averages', value=result_mart_path)


    find_team_averages_task = PythonOperator(
        task_id = 'ind_team_averages_task',
        python_callable=find_team_averages,
        dag=common_cases_dag,
        on_failure_callback=lambda context: logging.error(
            'ind_team_averages_task failed'
        )
    )

    # mappings should be provided upfront

    def send_dataframe_to_es(**kwargs):
        team_preformance = kwargs['ti'].xcom_pull(
            task_id = 'find_team_averages_task',
            key = 'team_averages'
        )

        team_preformance_mart = pd.read_csv(team_preformance)

        es_hook = ElasticsearchHook(elasticsearch_conn_id="elasticsearch_default")
        es_client = es_hook.get_conn()

        # Convert DataFrame to Elasticsearch bulk format
        actions = [
            {
                "_index": "team_performance",
                "_source": record
            }
            for record in team_preformance_mart.to_dict(orient="records")
        ]

        # Use bulk API to send all data at once
        helpers.bulk(es_client, actions)



    send_dataframe_to_es_task = PythonOperator(
        task_id = 'send_dataframe_to_es_task',
        python_callable=send_dataframe_to_es,
        dag=common_cases_dag,
        on_failure_callback=lambda context: logging.error(
            'Sink operation failed, send_dataframe_to_es_task'
                            )

    )


extract_tickets_task >> find_team_averages_task >> send_dataframe_to_es_task
