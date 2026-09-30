#!/bin/zsh

cd "/Users/pawankulkarni/Downloads/Chess Coach"

source .venv/bin/activate

export AIRFLOW_HOME="$HOME/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="$PWD/airflow/dags"
export PYTHONPATH="$PWD/src:$PYTHONPATH"
export AIRFLOW__API_AUTH__JWT_SECRET="chess-coach-local-secret-2026"
export AIRFLOW__CORE__LOAD_EXAMPLES="False"
pkill -f "airflow"

echo "Starting Airflow..."

airflow api-server > /tmp/chess_airflow_api.log 2>&1 &
airflow scheduler > /tmp/chess_airflow_scheduler.log 2>&1 &
airflow dag-processor > /tmp/chess_airflow_processor.log 2>&1 &

echo "Airflow started."
echo "UI: http://localhost:8080"
