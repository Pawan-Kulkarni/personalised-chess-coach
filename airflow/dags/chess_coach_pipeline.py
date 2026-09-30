from datetime import datetime

from airflow.sdk import dag
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator


@dag(
    dag_id="chess_coach_pipeline",
    start_date=datetime(2026, 9, 30),
    schedule=None,
    catchup=False,
    tags=["chess-coach", "pipeline"],
)
def chess_coach_pipeline():

    ingestion = TriggerDagRunOperator(
        task_id="run_ingestion",
        trigger_dag_id="chess_coach_ingestion",
        wait_for_completion=True,
        poke_interval=10,
        reset_dag_run=False,
        fail_when_dag_is_paused=True,
    )

    engine_eval = TriggerDagRunOperator(
        task_id="run_engine_eval",
        trigger_dag_id="chess_coach_ingest_engine_eval",
        wait_for_completion=True,
        poke_interval=10,
        reset_dag_run=False,
        fail_when_dag_is_paused=True,
    )

    analysis = TriggerDagRunOperator(
        task_id="run_analysis",
        trigger_dag_id="chess_coach_analysis",
        wait_for_completion=True,
        poke_interval=10,
        reset_dag_run=False,
        fail_when_dag_is_paused=True,
    )

    ingestion >> engine_eval >> analysis


chess_coach_pipeline()
