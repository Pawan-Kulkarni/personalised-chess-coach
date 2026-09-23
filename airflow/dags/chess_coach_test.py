from airflow.sdk import dag, task
from datetime import datetime


@dag(
    dag_id="chess_coach_test",
    start_date=datetime(2026, 9, 23),
    schedule=None,
    catchup=False,
)
def chess_coach_test():

    @task
    def parse_pgn():
        print("Parsing chess PGN...")

    @task
    def load_database():
        print("Loading data into PostgreSQL...")

    @task
    def finish():
        print("Chess Coach pipeline finished!")


    parse = parse_pgn()
    load = load_database()
    done = finish()

    parse >> load >> done


chess_coach_test()