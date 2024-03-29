airflow db migrate

airflow users create \
    --username ernie \
    --firstname Peter \
    --lastname Parker \
    --role Admin \
    --email spiderman@superhero.org \
    --password welcome

airflow webserver --port 8080

airflow scheduler